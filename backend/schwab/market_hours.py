"""
Schwab Market Hours API Endpoints
Wrapper for market hours and status.
"""

from typing import Dict, Any, Optional
from .client import SchwabAPIClient


class MarketHoursEndpoint:
    """
    Schwab Market Hours API endpoints.
    
    Endpoints:
    - GET /markets - Get hours for all markets
    - GET /markets/{market_id} - Get hours for specific market
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize market hours endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_markets(
        self,
        markets: Optional[str] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get market hours for all or specified markets.
        
        Args:
            markets: Comma-separated market IDs (equity, option, bond, future, forex)
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Dictionary of market hours by market ID
        
        Example:
            hours = endpoint.get_markets(markets='equity,option')
        """
        params = {}
        if markets:
            params['markets'] = markets
        if date:
            params['date'] = date
        
        return self.client.get('/markets', params=params)
    
    def get_market(
        self,
        market_id: str,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get market hours for a specific market.
        
        Args:
            market_id: Market ID (equity, option, bond, future, forex)
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Market hours object
        
        Example:
            hours = endpoint.get_market('equity')
        """
        params = {}
        if date:
            params['date'] = date
        
        return self.client.get(f'/markets/{market_id}', params=params)
    
    def get_equity_hours(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get equity market hours (convenience method).
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            Equity market hours
        
        Example:
            hours = endpoint.get_equity_hours()
        """
        return self.get_market('equity', date=date)
    
    def get_option_hours(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get option market hours (convenience method).
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            Option market hours
        
        Example:
            hours = endpoint.get_option_hours()
        """
        return self.get_market('option', date=date)
    
    def get_futures_hours(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get futures market hours (convenience method).
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            Futures market hours
        
        Example:
            hours = endpoint.get_futures_hours()
        """
        return self.get_market('future', date=date)
    
    def get_forex_hours(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get forex market hours (convenience method).
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            Forex market hours
        
        Example:
            hours = endpoint.get_forex_hours()
        """
        return self.get_market('forex', date=date)
    
    def is_market_open(
        self,
        market_id: str = 'equity',
        date: Optional[str] = None
    ) -> bool:
        """
        Check if market is currently open.
        
        Args:
            market_id: Market ID (equity, option, bond, future, forex)
            date: Date in YYYY-MM-DD format
        
        Returns:
            True if market is open, False otherwise
        
        Example:
            is_open = endpoint.is_market_open('equity')
        """
        try:
            hours = self.get_market(market_id, date=date)
            # Check if market is open based on response
            if market_id in hours:
                market_data = hours[market_id]
                if isinstance(market_data, dict):
                    return market_data.get('isOpen', False)
            return False
        except Exception:
            return False
