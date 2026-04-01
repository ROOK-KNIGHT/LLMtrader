"""
Schwab API Client
Core HTTP client with token management, auto-refresh, rate limiting, and retry logic.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SchwabAPIClient:
    """
    Core Schwab API client with:
    - Token management via AWS Secrets Manager
    - Auto-refresh on 401
    - Rate limiting
    - Retry with exponential backoff
    - Request/response logging
    """
    
    TRADER_BASE_URL = "https://api.schwabapi.com/trader/v1"
    MARKET_DATA_BASE_URL = "https://api.schwabapi.com/marketdata/v1"
    AUTH_BASE_URL = "https://api.schwabapi.com/v1/oauth"
    
    def __init__(
        self,
        aws_region: str = None,
        credentials_secret_name: str = "production/schwab-api/credentials",
        tokens_secret_name: str = "production/schwab-api/tokens",
        max_retries: int = 3,
        rate_limit_delay: float = 0.5
    ):
        """
        Initialize Schwab API client.
        
        Args:
            aws_region: AWS region for Secrets Manager
            credentials_secret_name: Secret name for API credentials
            tokens_secret_name: Secret name for access/refresh tokens
            max_retries: Max retry attempts for failed requests
            rate_limit_delay: Delay between requests (seconds)
        """
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
        self.credentials_secret_name = credentials_secret_name
        self.tokens_secret_name = tokens_secret_name
        self.rate_limit_delay = rate_limit_delay
        
        # Initialize AWS Secrets Manager client
        self.secrets_client = boto3.client('secretsmanager', region_name=self.aws_region)
        
        # Load credentials and tokens
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
        
        logger.info(f"Schwab API client initialized (region: {self.aws_region})")
    
    def _load_credentials(self):
        """Load Schwab API credentials from AWS Secrets Manager"""
        try:
            response = self.secrets_client.get_secret_value(SecretId=self.credentials_secret_name)
            credentials = json.loads(response['SecretString'])
            
            self.app_key = credentials.get('schwab_client_id')
            self.app_secret = credentials.get('schwab_client_secret')
            self.redirect_uri = credentials.get('schwab_redirect_uri')
            
            if not all([self.app_key, self.app_secret, self.redirect_uri]):
                raise ValueError("Missing required credentials in AWS secret")
            
            logger.info("Schwab API credentials loaded from AWS")
        except ClientError as e:
            logger.error(f"Failed to load credentials from AWS: {e}")
            raise
    
    def _load_tokens(self):
        """Load access/refresh tokens from AWS Secrets Manager"""
        try:
            response = self.secrets_client.get_secret_value(SecretId=self.tokens_secret_name)
            tokens = json.loads(response['SecretString'])
            
            self.access_token = tokens.get('access_token')
            self.refresh_token = tokens.get('refresh_token')
            
            # Parse token expiry
            expires_in = tokens.get('expires_in', 1800)  # Default 30 min
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Schwab API tokens loaded from AWS")
        except ClientError as e:
            logger.warning(f"Failed to load tokens from AWS: {e}")
            # Tokens might not exist yet (first run)
            self.access_token = None
            self.refresh_token = None
    
    def _save_tokens(self, tokens: Dict[str, Any]):
        """Save tokens to AWS Secrets Manager"""
        try:
            secret_value = json.dumps({
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'expires_in': tokens.get('expires_in', 1800),
                'token_type': tokens.get('token_type', 'Bearer'),
                'scope': tokens.get('scope', ''),
                'updated_at': datetime.now().isoformat()
            })
            
            self.secrets_client.put_secret_value(
                SecretId=self.tokens_secret_name,
                SecretString=secret_value
            )
            
            logger.info("Tokens saved to AWS Secrets Manager")
        except ClientError as e:
            logger.error(f"Failed to save tokens to AWS: {e}")
            raise
    
    def _is_token_expired(self) -> bool:
        """Check if access token is expired or about to expire"""
        if not self.token_expiry:
            return True
        # Refresh if less than 5 minutes remaining
        return datetime.now() >= (self.token_expiry - timedelta(minutes=5))
    
    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        logger.info("Refreshing access token...")
        
        url = f"{self.AUTH_BASE_URL}/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.app_key,
            'client_secret': self.app_secret
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens.get('refresh_token', self.refresh_token)
            
            expires_in = tokens.get('expires_in', 1800)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Save to AWS
            self._save_tokens(tokens)
            
            logger.info("Access token refreshed successfully")
        else:
            logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Token refresh failed: {response.status_code}")
    
    def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if self._is_token_expired():
            self.refresh_access_token()
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
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
            url: Full URL or path (will prepend base URL if needed)
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
        
        # Prepend base URL if needed
        if not url.startswith('http'):
            # Determine which base URL to use
            if '/trader/' in url or url.startswith('/accounts'):
                url = f"{self.TRADER_BASE_URL}{url}"
            elif '/marketdata/' in url or any(x in url for x in ['/quotes', '/chains', '/movers', '/markets', '/instruments', '/pricehistory']):
                url = f"{self.MARKET_DATA_BASE_URL}{url}"
        
        headers = self._get_headers()
        
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
            
            # Handle 401 (token expired)
            if response.status_code == 401 and auto_refresh:
                logger.warning("Received 401, refreshing token and retrying...")
                self.refresh_access_token()
                headers = self._get_headers()
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=30
                )
            
            # Log response
            if response.status_code >= 400:
                logger.error(f"API Error {response.status_code}: {response.text}")
            
            response.raise_for_status()
            
            # Return JSON if available
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
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
