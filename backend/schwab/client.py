"""
Schwab API Client
Core HTTP client with token management (PostgreSQL), auto-refresh, rate limiting, and retry logic.
"""

import os
import time
import base64
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class SchwabAPIClient:
    """
    Core Schwab API client with:
    - Token management via PostgreSQL (schwab_tokens / schwab_credentials tables)
    - Auto-refresh on 401 or token expiry
    - Rate limiting
    - Retry with exponential backoff
    - Request/response logging
    """

    TRADER_BASE_URL = "https://api.schwabapi.com/trader/v1"
    MARKET_DATA_BASE_URL = "https://api.schwabapi.com/marketdata/v1"
    AUTH_BASE_URL = "https://api.schwabapi.com/v1/oauth"

    def __init__(
        self,
        user_id: int,
        max_retries: int = 3,
        rate_limit_delay: float = 0.5
    ):
        """
        Initialize Schwab API client for a specific user.

        Args:
            user_id: The user's ID (used to look up credentials/tokens in PostgreSQL)
            max_retries: Max retry attempts for failed requests
            rate_limit_delay: Minimum delay between requests (seconds)
        """
        from backend.database import db
        from backend.auth.schwab_oauth import SchwabOAuth

        self.user_id = user_id
        self.rate_limit_delay = rate_limit_delay
        self.db = db
        self.oauth = SchwabOAuth()

        # Credential/token state
        self.app_key = None
        self.app_secret = None
        self.redirect_uri = None
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

        self._load_credentials()
        self._load_tokens()

        # Setup HTTP session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Rate limiting
        self.last_request_time = 0

        logger.info(f"Schwab API client initialized for user_id={user_id}")

    # -------------------------------------------------------------------------
    # Account Hash Cache
    # -------------------------------------------------------------------------

    _account_hash_cache: Dict[int, str] = {}  # class-level cache: user_id -> hash

    def get_default_account_hash(self) -> str:
        """
        Get the account hash for this user, using a class-level cache to avoid
        repeated API calls. Always returns the Schwab hashValue (not accountNumber).

        Returns:
            Account hash string

        Raises:
            Exception if no accounts found
        """
        if self.user_id in SchwabAPIClient._account_hash_cache:
            return SchwabAPIClient._account_hash_cache[self.user_id]

        account_numbers = self.get('/accounts/accountNumbers')
        if not account_numbers:
            raise Exception("No Schwab accounts found for this user.")

        hash_value = account_numbers[0]['hashValue']
        SchwabAPIClient._account_hash_cache[self.user_id] = hash_value
        return hash_value

    # -------------------------------------------------------------------------
    # Credential / Token Management (PostgreSQL)
    # -------------------------------------------------------------------------

    def _load_credentials(self):
        """Load Schwab API credentials from PostgreSQL schwab_credentials table."""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT app_key, app_secret_encrypted, callback_url FROM schwab_credentials WHERE user_id = %s",
                (self.user_id,)
            )
            row = cursor.fetchone()

        if not row:
            raise ValueError(f"No Schwab credentials found for user_id={self.user_id}. Complete onboarding first.")

        self.app_key = row['app_key']
        self.app_secret = self.oauth.decrypt_secret(row['app_secret_encrypted'])
        self.redirect_uri = row['callback_url']

        logger.info(f"Schwab credentials loaded from DB for user_id={self.user_id}")

    def _load_tokens(self):
        """Load access/refresh tokens from PostgreSQL schwab_tokens table."""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT access_token, refresh_token, expires_at FROM schwab_tokens WHERE user_id = %s",
                (self.user_id,)
            )
            row = cursor.fetchone()

        if not row:
            logger.warning(f"No Schwab tokens found for user_id={self.user_id}")
            self.access_token = None
            self.refresh_token = None
            self.token_expiry = None
            return

        self.access_token = row['access_token']
        self.refresh_token = row['refresh_token']
        self.token_expiry = row['expires_at']

        logger.info(f"Schwab tokens loaded from DB for user_id={self.user_id}")

    def _save_tokens(self, tokens: Dict[str, Any]):
        """Save refreshed tokens back to PostgreSQL schwab_tokens table."""
        expires_in = tokens.get('expires_in', 1800)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        with self.db.get_cursor() as cursor:
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
                    self.user_id,
                    tokens['access_token'],
                    tokens.get('refresh_token', self.refresh_token),
                    tokens.get('token_type', 'Bearer'),
                    expires_at,
                    tokens.get('scope', '')
                )
            )

        # Update in-memory state
        self.access_token = tokens['access_token']
        self.refresh_token = tokens.get('refresh_token', self.refresh_token)
        self.token_expiry = expires_at

        logger.info(f"Schwab tokens saved to DB for user_id={self.user_id}")

    # -------------------------------------------------------------------------
    # Token Validity
    # -------------------------------------------------------------------------

    def _is_token_expired(self) -> bool:
        """Check if access token is expired or about to expire (within 5 minutes)."""
        if not self.token_expiry or not self.access_token:
            return True
        # token_expiry may be a datetime or a string
        expiry = self.token_expiry
        if isinstance(expiry, str):
            expiry = datetime.fromisoformat(expiry)
        return datetime.utcnow() >= (expiry - timedelta(minutes=5))

    def refresh_access_token(self):
        """Refresh access token using refresh token and save to PostgreSQL."""
        if not self.refresh_token:
            raise ValueError("No refresh token available. Re-authenticate via Schwab OAuth.")

        logger.info(f"Refreshing access token for user_id={self.user_id}...")

        credentials = f"{self.app_key}:{self.app_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        response = requests.post(f"{self.AUTH_BASE_URL}/token", headers=headers, data=data)

        if response.status_code == 200:
            tokens = response.json()
            self._save_tokens(tokens)
            logger.info(f"Access token refreshed for user_id={self.user_id}")
        else:
            logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")

    def _ensure_valid_token(self):
        """Ensure we have a valid access token, refreshing if necessary."""
        if self._is_token_expired():
            self.refresh_access_token()

    # -------------------------------------------------------------------------
    # Rate Limiting & Headers
    # -------------------------------------------------------------------------

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _get_headers(self, method: str = 'GET') -> Dict[str, str]:
        """Get request headers with Bearer auth token.
        
        Note: Schwab API rejects GET requests that include Content-Type: application/json,
        so we only include it for methods that send a body (POST, PUT, PATCH).
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            headers['Content-Type'] = 'application/json'
        return headers

    # -------------------------------------------------------------------------
    # Core HTTP Request
    # -------------------------------------------------------------------------

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        auto_refresh: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Schwab API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            url: Full URL or path (base URL prepended automatically)
            params: Query parameters
            json_data: JSON body for POST/PUT/PATCH
            auto_refresh: Auto-refresh token on 401

        Returns:
            Response JSON as dict
        """
        # Ensure valid token
        self._ensure_valid_token()

        # Rate limiting
        self._rate_limit()

        # Prepend base URL if path only
        if not url.startswith('http'):
            if any(x in url for x in ['/accounts', '/orders', '/transactions', '/userPreference']):
                url = f"{self.TRADER_BASE_URL}{url}"
            else:
                url = f"{self.MARKET_DATA_BASE_URL}{url}"

        headers = self._get_headers(method)
        logger.debug(f"{method} {url}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=30
            )

            # Handle 401 — token may have just expired
            if response.status_code == 401 and auto_refresh:
                logger.warning("Received 401, refreshing token and retrying...")
                self.refresh_access_token()
                headers = self._get_headers(method)
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=30
                )

            if response.status_code >= 400:
                # Build a descriptive error message from the response body
                error_body = ""
                try:
                    error_json = response.json()
                    error_body = error_json.get('message') or error_json.get('error_description') or str(error_json)
                except Exception:
                    error_body = response.text.strip()[:300] if response.text else "(empty body)"

                # Add hints for common Schwab error patterns
                hint = ""
                if response.status_code == 400:
                    if 'date' in url.lower() or params and any('time' in k.lower() for k in params):
                        hint = " (Hint: Schwab requires dates in ISO 8601 format with .000Z suffix, e.g. 2026-04-02T00:00:00.000Z)"
                    elif '/quotes' in url:
                        hint = " (Hint: Use /quotes?symbols=SYMBOL not /quotes/{symbol})"
                    elif '/accounts' in url and 'orders' in url:
                        hint = " (Hint: Ensure account_hash is the hashValue, not the account number)"
                elif response.status_code == 401:
                    hint = " (Hint: Access token may be expired — re-authenticate via Schwab OAuth)"
                elif response.status_code == 403:
                    hint = " (Hint: Insufficient permissions for this endpoint)"
                elif response.status_code == 404:
                    hint = " (Hint: Resource not found — check symbol, account hash, or order ID)"

                logger.error(f"Schwab API Error {response.status_code}: {error_body}{hint}")

            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

        except requests.exceptions.HTTPError as e:
            # Re-raise with enriched message
            response = e.response
            error_body = ""
            try:
                error_json = response.json()
                error_body = error_json.get('message') or error_json.get('error_description') or str(error_json)
            except Exception:
                error_body = response.text.strip()[:300] if response.text else "(empty body)"
            raise requests.exceptions.HTTPError(
                f"Schwab API {response.status_code}: {error_body} [URL: {response.url}]",
                response=response
            ) from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------

    def get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        return self.request('GET', url, params=params)

    def post(self, url: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request"""
        return self.request('POST', url, json_data=json_data)

    def put(self, url: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT request"""
        return self.request('PUT', url, json_data=json_data)

    def delete(self, url: str) -> Dict[str, Any]:
        """DELETE request"""
        return self.request('DELETE', url)

    def patch(self, url: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """PATCH request"""
        return self.request('PATCH', url, json_data=json_data)
