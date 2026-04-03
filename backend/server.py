"""
FastAPI Server - Main application server
"""

import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

from backend.database import db
from backend.auth.service import AuthService
from backend.auth.schwab_oauth import SchwabOAuth
from backend.schwab import SchwabAPI
from backend.ai.llm_handler import LLMHandler
from backend.ai.tools_registry import ToolsRegistry
from backend.ai.prompts import get_system_prompt

# Initialize services
auth_service = AuthService()
schwab_oauth = SchwabOAuth()

# Create FastAPI app
app = FastAPI(
    title="LLMtrader API",
    description="AI-powered portfolio management platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "https://127.0.0.1:5173",
        "https://127.0.0.1:5174",
        "https://127.0.0.1:5175",
        "https://127.0.0.1:5176",
        "https://volflowagent.com",
        "https://www.volflowagent.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SchwabCredentialsRequest(BaseModel):
    app_key: str
    app_secret: str
    callback_url: str = "https://127.0.0.1:8000/api/schwab/callback"


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    schwab_connected: bool
    onboarding_complete: bool


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


# ============================================================================
# Auth Dependency
# ============================================================================

async def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """
    Dependency to get current user from JWT token.

    Usage:
        @app.get("/api/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = parts[1]
    user_info = auth_service.get_user_from_token(token)

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_info


def get_schwab_api(user: Dict[str, Any] = Depends(get_current_user)) -> SchwabAPI:
    """
    FastAPI dependency that returns a SchwabAPI instance for the current user.
    Loads credentials and tokens from PostgreSQL.
    """
    try:
        return SchwabAPI(user_id=user['user_id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Schwab client: {str(e)}")


# ============================================================================
# Auth Routes
# ============================================================================

@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Create a new user account"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (request.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")

        password_hash = auth_service.hash_password(request.password)

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, display_name)
                VALUES (%s, %s, %s)
                RETURNING id, email, display_name, avatar_url, created_at
                """,
                (request.email, password_hash, request.display_name or request.email.split('@')[0])
            )
            user = cursor.fetchone()

        token = auth_service.create_token(user['id'], user['email'])

        return AuthResponse(
            token=token,
            user=UserResponse(
                id=user['id'],
                email=user['email'],
                display_name=user['display_name'],
                avatar_url=user['avatar_url'],
                schwab_connected=False,
                onboarding_complete=False
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Sign in with email and password"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, email, password_hash, display_name, avatar_url FROM users WHERE email = %s",
                (request.email,)
            )
            user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not auth_service.verify_password(request.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM schwab_tokens WHERE user_id = %s",
                (user['id'],)
            )
            schwab_connected = cursor.fetchone() is not None

        token = auth_service.create_token(user['id'], user['email'])

        return AuthResponse(
            token=token,
            user=UserResponse(
                id=user['id'],
                email=user['email'],
                display_name=user['display_name'],
                avatar_url=user['avatar_url'],
                schwab_connected=schwab_connected,
                onboarding_complete=schwab_connected
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(user = Depends(get_current_user)):
    """Get current user info"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, email, display_name, avatar_url FROM users WHERE id = %s",
                (user['user_id'],)
            )
            user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM schwab_tokens WHERE user_id = %s",
                (user['user_id'],)
            )
            schwab_connected = cursor.fetchone() is not None

        return UserResponse(
            id=user_data['id'],
            email=user_data['email'],
            display_name=user_data['display_name'],
            avatar_url=user_data['avatar_url'],
            schwab_connected=schwab_connected,
            onboarding_complete=schwab_connected
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Schwab OAuth Routes
# ============================================================================

@app.post("/api/schwab/credentials")
async def save_schwab_credentials(
    request: SchwabCredentialsRequest,
    user = Depends(get_current_user)
):
    """Save Schwab API credentials"""
    try:
        encrypted_secret = schwab_oauth.encrypt_secret(request.app_secret)

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO schwab_credentials (user_id, app_key, app_secret_encrypted, callback_url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET app_key = EXCLUDED.app_key,
                    app_secret_encrypted = EXCLUDED.app_secret_encrypted,
                    callback_url = EXCLUDED.callback_url,
                    updated_at = NOW()
                """,
                (user['user_id'], request.app_key, encrypted_secret, request.callback_url)
            )

        return {"success": True, "message": "Credentials saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/auth-url")
async def get_schwab_auth_url(user = Depends(get_current_user)):
    """Get Schwab OAuth authorization URL"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT app_key, callback_url FROM schwab_credentials WHERE user_id = %s",
                (user['user_id'],)
            )
            creds = cursor.fetchone()

        if not creds:
            raise HTTPException(status_code=400, detail="Schwab credentials not configured")

        auth_url = schwab_oauth.get_authorization_url(
            app_key=creds['app_key'],
            redirect_uri=creds['callback_url'],
            state=str(user['user_id'])
        )

        return {"auth_url": auth_url}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/callback")
async def schwab_oauth_callback(
    code: str = Query(...),
    state: str = Query(None)
):
    """
    Legacy callback handler (kept for backward compatibility).
    New flow uses POST /api/schwab/exchange-token from the frontend.
    """
    return RedirectResponse(url=f"https://volflowagent.com/oauth/schwab/callback?code={code}&session={state or ''}")


@app.post("/api/schwab/exchange-token")
async def exchange_schwab_token(
    request_data: dict,
    user = Depends(get_current_user)
):
    """
    Exchange Schwab authorization code for tokens.
    Called by the frontend after Schwab redirects back with ?code=
    """
    try:
        code = request_data.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")

        user_id = user['user_id']

        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT app_key, app_secret_encrypted, callback_url FROM schwab_credentials WHERE user_id = %s",
                (user_id,)
            )
            creds = cursor.fetchone()

        if not creds:
            raise HTTPException(status_code=400, detail="Schwab credentials not configured. Please complete onboarding first.")

        app_secret = schwab_oauth.decrypt_secret(creds['app_secret_encrypted'])

        tokens = schwab_oauth.exchange_code_for_tokens(
            code=code,
            app_key=creds['app_key'],
            app_secret=app_secret,
            redirect_uri=creds['callback_url']
        )

        expires_at = schwab_oauth.calculate_token_expiry(tokens['expires_in'])

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO schwab_tokens (user_id, access_token, refresh_token, token_type, expires_at, scope)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    token_type = EXCLUDED.token_type,
                    expires_at = EXCLUDED.expires_at,
                    scope = EXCLUDED.scope,
                    updated_at = NOW()
                """,
                (
                    user_id,
                    tokens['access_token'],
                    tokens['refresh_token'],
                    tokens.get('token_type', 'Bearer'),
                    expires_at,
                    tokens.get('scope', '')
                )
            )

        return {"success": True, "message": "Schwab account connected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")


@app.get("/api/schwab/status")
async def get_schwab_status(user = Depends(get_current_user)):
    """Check if Schwab is connected and token is valid"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT expires_at FROM schwab_tokens WHERE user_id = %s",
                (user['user_id'],)
            )
            token = cursor.fetchone()

        if not token:
            return {
                "connected": False,
                "expired": None,
                "expires_at": None
            }

        expired = schwab_oauth.is_token_expired(token['expires_at'])

        return {
            "connected": True,
            "expired": expired,
            "expires_at": token['expires_at'].isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Schwab Data API Routes
# ============================================================================

# --- Accounts ---

@app.get("/api/schwab/accounts")
async def get_accounts(
    fields: Optional[str] = Query(None, description="Optional fields: positions"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get all linked Schwab accounts"""
    try:
        return schwab.accounts.get_all_accounts(fields=fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/accounts/numbers")
async def get_account_numbers(schwab: SchwabAPI = Depends(get_schwab_api)):
    """Get account numbers and hash values for all linked accounts"""
    try:
        return schwab.accounts.get_account_numbers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/accounts/{account_hash}")
async def get_account(
    account_hash: str,
    fields: Optional[str] = Query(None, description="Optional fields: positions"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get details for a specific account"""
    try:
        return schwab.accounts.get_account(account_hash, fields=fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/accounts/{account_hash}/positions")
async def get_positions(
    account_hash: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get current positions for an account"""
    try:
        return schwab.accounts.get_positions(account_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/accounts/{account_hash}/balances")
async def get_balances(
    account_hash: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get account balances and buying power"""
    try:
        return schwab.accounts.get_balances(account_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Quotes ---

@app.get("/api/schwab/quotes")
async def get_quotes(
    symbols: str = Query(..., description="Comma-separated symbols, e.g. AAPL,MSFT,GOOGL"),
    fields: Optional[str] = Query(None, description="quote, fundamental, extended, reference, regular"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get real-time quotes for multiple symbols"""
    try:
        symbol_list = [s.strip() for s in symbols.split(',')]
        return schwab.quotes.get_quotes(symbol_list, fields=fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/quotes/{symbol}")
async def get_quote(
    symbol: str,
    fields: Optional[str] = Query(None, description="quote, fundamental, extended, reference, regular"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get real-time quote for a single symbol"""
    try:
        return schwab.quotes.get_quote(symbol, fields=fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Price History ---

@app.get("/api/schwab/history/{symbol}")
async def get_price_history(
    symbol: str,
    period_type: Optional[str] = Query(None, description="day, month, year, ytd"),
    period: Optional[int] = Query(None),
    frequency_type: Optional[str] = Query(None, description="minute, daily, weekly, monthly"),
    frequency: Optional[int] = Query(None),
    start_date: Optional[int] = Query(None, description="Epoch milliseconds"),
    end_date: Optional[int] = Query(None, description="Epoch milliseconds"),
    extended_hours: bool = Query(False),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get historical OHLCV price data"""
    try:
        return schwab.price_history.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type=frequency_type,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            need_extended_hours_data=extended_hours
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Options Chain ---

@app.get("/api/schwab/options/{symbol}")
async def get_option_chain(
    symbol: str,
    contract_type: Optional[str] = Query(None, description="CALL, PUT, ALL"),
    strike_count: Optional[int] = Query(None),
    range: Optional[str] = Query(None, description="ITM, NTM, OTM, ALL"),
    from_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    exp_month: Optional[str] = Query(None, description="JAN, FEB, MAR, etc."),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get options chain with Greeks"""
    try:
        return schwab.options_chain.get_option_chain(
            symbol=symbol,
            contract_type=contract_type,
            strike_count=strike_count,
            range=range,
            from_date=from_date,
            to_date=to_date,
            exp_month=exp_month
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/options/{symbol}/expirations")
async def get_expiration_chain(
    symbol: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get available option expiration dates"""
    try:
        return schwab.options_chain.get_expiration_chain(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Market Movers ---

@app.get("/api/schwab/movers/{index}")
async def get_movers(
    index: str,
    sort: Optional[str] = Query(None, description="VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN"),
    frequency: Optional[int] = Query(None, description="0, 1, 5, 10, 30, 60"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get top movers for an index ($SPX, $COMPX, $DJI, NYSE, NASDAQ)"""
    try:
        return schwab.movers.get_movers(index, sort=sort, frequency=frequency)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Market Hours ---

@app.get("/api/schwab/market-hours")
async def get_market_hours(
    markets: Optional[str] = Query(None, description="equity, option, bond, future, forex (comma-separated)"),
    date: Optional[str] = Query(None, description="YYYY-MM-DD (defaults to today)"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get market hours for all or specified markets"""
    try:
        return schwab.market_hours.get_markets(markets=markets, date=date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/market-hours/{market_id}")
async def get_market_hours_by_id(
    market_id: str,
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get market hours for a specific market (equity, option, bond, future, forex)"""
    try:
        return schwab.market_hours.get_market(market_id, date=date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Instruments ---

@app.get("/api/schwab/instruments")
async def search_instruments(
    symbol: str = Query(..., description="Symbol or search query"),
    projection: str = Query("symbol-search", description="symbol-search, symbol-regex, desc-search, desc-regex, fundamental"),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Search for instruments by symbol or description"""
    try:
        return schwab.instruments.search_instruments(symbol, projection=projection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/instruments/{cusip}")
async def get_instrument_by_cusip(
    cusip: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get instrument details by CUSIP"""
    try:
        return schwab.instruments.get_instrument_by_cusip(cusip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- User Preferences ---

@app.get("/api/schwab/user-preferences")
async def get_user_preferences(schwab: SchwabAPI = Depends(get_schwab_api)):
    """Get Schwab user account preferences"""
    try:
        return schwab.user_preferences.get_user_preferences()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Orders ---

@app.get("/api/schwab/orders/{account_hash}")
async def get_orders(
    account_hash: str,
    from_entered_time: Optional[str] = Query(None, description="ISO 8601 datetime"),
    to_entered_time: Optional[str] = Query(None, description="ISO 8601 datetime"),
    status: Optional[str] = Query(None, description="WORKING, FILLED, CANCELED, REJECTED, etc."),
    max_results: Optional[int] = Query(None),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get orders for an account"""
    try:
        return schwab.orders.get_orders(
            account_hash,
            from_entered_time=from_entered_time,
            to_entered_time=to_entered_time,
            status=status,
            max_results=max_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/orders/{account_hash}/{order_id}")
async def get_order(
    account_hash: str,
    order_id: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get a specific order"""
    try:
        return schwab.orders.get_order(account_hash, order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schwab/orders/{account_hash}")
async def place_order(
    account_hash: str,
    order_payload: dict,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Place an order"""
    try:
        return schwab.orders.place_order(account_hash, order_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schwab/orders/{account_hash}/preview")
async def preview_order(
    account_hash: str,
    order_payload: dict,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Preview an order (validates without placing — shows commission, fees, buying power impact)"""
    try:
        return schwab.orders.preview_order(account_hash, order_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/schwab/orders/{account_hash}/{order_id}")
async def cancel_order(
    account_hash: str,
    order_id: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Cancel an order"""
    try:
        return schwab.orders.cancel_order(account_hash, order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Transactions ---

@app.get("/api/schwab/transactions/{account_hash}")
async def get_transactions(
    account_hash: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    types: Optional[str] = Query(None, description="TRADE, DIVIDEND_OR_INTEREST, etc."),
    symbol: Optional[str] = Query(None),
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get transaction history for an account"""
    try:
        return schwab.transactions.get_transactions(
            account_hash,
            start_date=start_date,
            end_date=end_date,
            types=types,
            symbol=symbol
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schwab/transactions/{account_hash}/{transaction_id}")
async def get_transaction(
    account_hash: str,
    transaction_id: str,
    schwab: SchwabAPI = Depends(get_schwab_api)
):
    """Get a specific transaction"""
    try:
        return schwab.transactions.get_transaction(account_hash, transaction_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI Chat Routes
# ============================================================================

class AIChatRequest(BaseModel):
    message: str
    model: str = "claude"
    persona: str = "portfolio_manager"
    conversation_history: Optional[List[Dict[str, Any]]] = None


class AIKeyRequest(BaseModel):
    service_name: str   # 'claude', 'grok', 'gemini'
    api_key: str


@app.post("/api/ai/chat")
async def ai_chat(
    request: AIChatRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to the AI trading assistant.
    Claude (or Grok/Gemini) will use Schwab tools to answer with real data.
    """
    try:
        user_id = user['user_id']

        # Initialize Schwab API for this user (tools need it)
        try:
            schwab_api = SchwabAPI(user_id=user_id)
        except Exception:
            schwab_api = None  # Allow chat without Schwab (e.g. general questions)

        # Initialize tools registry (only if Schwab is connected)
        tools_registry = None
        if schwab_api:
            try:
                tools_registry = ToolsRegistry(schwab_api=schwab_api)
            except Exception as e:
                logger.warning(f"Could not initialize tools registry for user {user_id}: {e}")

        # Initialize LLM handler with user's API keys from DB
        llm = LLMHandler(user_id=user_id)

        # Get system prompt for selected persona
        system_prompt = get_system_prompt(request.persona)

        # Call the model
        response_text, status, error = await llm.call_model(
            model_name=request.model,
            prompt=request.message,
            system_prompt=system_prompt,
            tools_registry=tools_registry,
            conversation_history=request.conversation_history
        )

        if status == 'error':
            raise HTTPException(status_code=500, detail=error or "AI model returned an error")

        return {
            "response": response_text,
            "model": request.model,
            "persona": request.persona,
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI chat error for user {user.get('user_id')}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/keys")
async def save_ai_key(
    request: AIKeyRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Save an AI API key for the current user"""
    try:
        valid_services = {'claude', 'grok', 'gemini'}
        service = request.service_name.lower()
        if service not in valid_services:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid service. Must be one of: {', '.join(valid_services)}"
            )

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ai_api_keys (user_id, service_name, api_key, is_active)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (user_id, service_name) DO UPDATE
                SET api_key = EXCLUDED.api_key,
                    is_active = true,
                    updated_at = NOW()
                """,
                (user['user_id'], service, request.api_key)
            )

        return {"success": True, "message": f"{service.capitalize()} API key saved"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/keys")
async def get_ai_keys(user: Dict[str, Any] = Depends(get_current_user)):
    """Get which AI services have keys configured (does not return the actual keys)"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT service_name, is_active, updated_at
                FROM ai_api_keys
                WHERE user_id = %s
                """,
                (user['user_id'],)
            )
            rows = cursor.fetchall()

        return {
            "keys": [
                {
                    "service": row['service_name'],
                    "is_active": row['is_active'],
                    "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
                }
                for row in rows
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ai/keys/{service_name}")
async def delete_ai_key(
    service_name: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Remove an AI API key"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM ai_api_keys WHERE user_id = %s AND service_name = %s",
                (user['user_id'], service_name.lower())
            )
        return {"success": True, "message": f"{service_name} key removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health/tokens")
async def token_health(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Show Schwab token health for the current user.
    Returns expiry time, minutes remaining, and whether a refresh is needed.
    """
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT access_token IS NOT NULL AS has_access_token,
                       refresh_token IS NOT NULL AS has_refresh_token,
                       expires_at,
                       updated_at
                FROM schwab_tokens
                WHERE user_id = %s
                """,
                (user['user_id'],)
            )
            row = cursor.fetchone()

        if not row:
            return {
                "connected": False,
                "message": "No Schwab tokens found. Complete OAuth flow to connect."
            }

        now = datetime.utcnow()
        expires_at = row['expires_at']
        if hasattr(expires_at, 'replace'):
            expires_at = expires_at.replace(tzinfo=None)

        minutes_remaining = (expires_at - now).total_seconds() / 60
        needs_refresh = minutes_remaining <= 15

        return {
            "connected": True,
            "has_access_token": row['has_access_token'],
            "has_refresh_token": row['has_refresh_token'],
            "expires_at": expires_at.isoformat() + "Z",
            "minutes_remaining": round(minutes_remaining, 1),
            "needs_refresh": needs_refresh,
            "last_refreshed": row['updated_at'].isoformat() + "Z" if row['updated_at'] else None,
            "status": "critical" if minutes_remaining <= 0 else "warning" if needs_refresh else "healthy"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    print("Starting LLMtrader API server...")
    try:
        db.create_tables()
        print("Database initialized")
    except Exception as e:
        print(f"Database initialization warning: {e}")
    print("Token refresh is handled by the dedicated token-refresher supervisor process.")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("Shutting down LLMtrader API server...")
    db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
