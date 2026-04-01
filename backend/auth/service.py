"""
Auth Service - JWT and password management
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class AuthService:
    """
    Authentication service for JWT tokens and password hashing.
    """
    
    def __init__(self, secret_key: str = None, algorithm: str = 'HS256'):
        """
        Initialize auth service.
        
        Args:
            secret_key: JWT secret key
            algorithm: JWT algorithm (default: HS256)
        """
        # Generate a secure random key if not provided
        if secret_key is None:
            import secrets
            secret_key = secrets.token_urlsafe(32)
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_hours = 24  # JWT expires in 24 hours
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password from database
        
        Returns:
            True if password matches
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_token(self, user_id: int, email: str, additional_claims: Dict[str, Any] = None) -> str:
        """
        Create a JWT token for a user.
        
        Args:
            user_id: User ID
            email: User email
            additional_claims: Additional claims to include in token
        
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user info from token.
        
        Args:
            token: JWT token string
        
        Returns:
            User info dict with user_id and email, or None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return {
            'user_id': payload.get('user_id'),
            'email': payload.get('email')
        }
