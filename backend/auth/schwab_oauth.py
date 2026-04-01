"""
Schwab OAuth - OAuth 2.0 flow for Schwab API
"""

import os
import base64
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from urllib.parse import urlencode


class SchwabOAuth:
    """
    Schwab OAuth 2.0 service for authorization and token management.
    """
    
    AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"
    TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
    
    def __init__(self, encryption_key: str = None):
        """
        Initialize Schwab OAuth service.
        
        Args:
            encryption_key: Fernet encryption key for app_secret (base64 encoded)
        """
        # Generate new key if not provided
        if encryption_key is None:
            encryption_key = Fernet.generate_key().decode()
        
        self.encryption_key = encryption_key
        self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
    
    def encrypt_secret(self, app_secret: str) -> str:
        """
        Encrypt app_secret for storage.
        
        Args:
            app_secret: Schwab app secret
        
        Returns:
            Encrypted secret (base64 string)
        """
        encrypted = self.cipher.encrypt(app_secret.encode())
        return encrypted.decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt app_secret from storage.
        
        Args:
            encrypted_secret: Encrypted secret from database
        
        Returns:
            Decrypted app secret
        """
        decrypted = self.cipher.decrypt(encrypted_secret.encode())
        return decrypted.decode()
    
    def get_authorization_url(
        self,
        app_key: str,
        redirect_uri: str,
        state: str = None
    ) -> str:
        """
        Generate Schwab OAuth authorization URL.
        
        Args:
            app_key: Schwab app key (client_id)
            redirect_uri: OAuth callback URL
            state: Optional state parameter for CSRF protection
        
        Returns:
            Authorization URL to redirect user to
        
        Example:
            url = oauth.get_authorization_url(
                'YOUR_APP_KEY',
                'https://127.0.0.1:8000/api/schwab/callback'
            )
            # Redirect user to this URL
        """
        params = {
            'client_id': app_key,
            'redirect_uri': redirect_uri,
            'response_type': 'code'
        }
        
        if state:
            params['state'] = state
        
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    def exchange_code_for_tokens(
        self,
        code: str,
        app_key: str,
        app_secret: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from callback
            app_key: Schwab app key
            app_secret: Schwab app secret
            redirect_uri: OAuth callback URL (must match registered URL)
        
        Returns:
            Token response dict with:
            - access_token: Access token
            - refresh_token: Refresh token
            - expires_in: Token expiry in seconds
            - token_type: Token type (Bearer)
            - scope: Granted scopes
        
        Raises:
            Exception if token exchange fails
        """
        # Create Basic Auth header
        credentials = f"{app_key}:{app_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")
    
    def refresh_access_token(
        self,
        refresh_token: str,
        app_key: str,
        app_secret: str
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from database
            app_key: Schwab app key
            app_secret: Schwab app secret
        
        Returns:
            Token response dict with new access_token and refresh_token
        
        Raises:
            Exception if refresh fails
        """
        # Create Basic Auth header
        credentials = f"{app_key}:{app_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")
    
    def calculate_token_expiry(self, expires_in: int) -> datetime:
        """
        Calculate token expiry timestamp.
        
        Args:
            expires_in: Seconds until expiry (from token response)
        
        Returns:
            Expiry datetime
        """
        return datetime.utcnow() + timedelta(seconds=expires_in)
    
    def is_token_expired(self, expires_at: datetime, buffer_minutes: int = 5) -> bool:
        """
        Check if token is expired or about to expire.
        
        Args:
            expires_at: Token expiry datetime
            buffer_minutes: Refresh if expiring within this many minutes
        
        Returns:
            True if token should be refreshed
        """
        buffer = timedelta(minutes=buffer_minutes)
        return datetime.utcnow() >= (expires_at - buffer)
