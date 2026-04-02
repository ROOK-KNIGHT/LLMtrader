"""
FastAPI Server - Main application server
"""

import os
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

from backend.database import db
from backend.auth.service import AuthService
from backend.auth.schwab_oauth import SchwabOAuth

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
        "https://127.0.0.1:5176"
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
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    user_info = auth_service.get_user_from_token(token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_info


# ============================================================================
# Auth Routes
# ============================================================================

@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """Create a new user account"""
    try:
        # Check if user exists
        with db.get_cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (request.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = auth_service.hash_password(request.password)
        
        # Create user
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
        
        # Create JWT token
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
        # Get user
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, email, password_hash, display_name, avatar_url FROM users WHERE email = %s",
                (request.email,)
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not auth_service.verify_password(request.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if Schwab is connected
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM schwab_tokens WHERE user_id = %s",
                (user['id'],)
            )
            schwab_connected = cursor.fetchone() is not None
        
        # Create JWT token
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
        
        # Check if Schwab is connected
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
        # Encrypt app_secret
        encrypted_secret = schwab_oauth.encrypt_secret(request.app_secret)
        
        # Save to database
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
        # Get user's credentials
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT app_key, callback_url FROM schwab_credentials WHERE user_id = %s",
                (user['user_id'],)
            )
            creds = cursor.fetchone()
        
        if not creds:
            raise HTTPException(status_code=400, detail="Schwab credentials not configured")
        
        # Generate auth URL with state = user_id for security
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
    # Redirect to frontend with code in query params - frontend handles exchange
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
        
        # Get user's credentials
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT app_key, app_secret_encrypted, callback_url FROM schwab_credentials WHERE user_id = %s",
                (user_id,)
            )
            creds = cursor.fetchone()
        
        if not creds:
            raise HTTPException(status_code=400, detail="Schwab credentials not configured. Please complete onboarding first.")
        
        # Decrypt app_secret
        app_secret = schwab_oauth.decrypt_secret(creds['app_secret_encrypted'])
        
        # Exchange code for tokens
        tokens = schwab_oauth.exchange_code_for_tokens(
            code=code,
            app_key=creds['app_key'],
            app_secret=app_secret,
            redirect_uri=creds['callback_url']
        )
        
        # Calculate expiry
        expires_at = schwab_oauth.calculate_token_expiry(tokens['expires_in'])
        
        # Save tokens to database
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
        # Redirect to frontend error page
        return RedirectResponse(url=f"http://localhost:5173/oauth/error?message={str(e)}")


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
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    print("🚀 Starting LLMtrader API server...")
    try:
        db.create_tables()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("👋 Shutting down LLMtrader API server...")
    db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
