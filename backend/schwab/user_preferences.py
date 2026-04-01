"""
Schwab User Preferences API Endpoints
Wrapper for user account preferences.
"""

from typing import Dict, Any
from .client import SchwabAPIClient


class UserPreferencesEndpoint:
    """
    Schwab User Preferences API endpoints.
    
    Endpoints:
    - GET /userPreference - Get user preferences
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize user preferences endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Get user account preferences.
        
        Returns:
            User preferences object with account settings
        
        Example:
            prefs = endpoint.get_user_preferences()
        """
        return self.client.get('/userPreference')
