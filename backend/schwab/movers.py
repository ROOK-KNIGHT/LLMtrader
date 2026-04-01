"""
Schwab Market Movers API Endpoints
Wrapper for top movers by index.
"""

from typing import Dict, Any, Optional
from .client import SchwabAPIClient


class MoversEndpoint:
    """
    Schwab Market Movers API endpoints.
    
    Endpoints:
    - GET /movers/{index} - Get top movers for an index
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize movers endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_movers(
        self,
        index: str,
        sort: Optional[str] = None,
        frequency: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get top movers for an index.
        
        Args:
            index: Index symbol ($DJI, $COMPX, $SPX, NYSE, NASDAQ, OTCBB, 
                   INDEX_ALL, EQUITY_ALL, OPTION_ALL, OPTION_PUT, OPTION_CALL)
            sort: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN
            frequency: Frequency in minutes (0, 1, 5, 10, 30, 60)
        
        Returns:
            List of mover objects with symbol, change, volume, etc.
        
        Example:
            movers = endpoint.get_movers('$SPX', sort='PERCENT_CHANGE_UP')
        """
        params = {}
        if sort:
            params['sort'] = sort
        if frequency is not None:
            params['frequency'] = frequency
        
        return self.client.get(f'/movers/{index}', params=params)
    
    def get_sp500_movers(
        self,
        sort: str = 'PERCENT_CHANGE_UP'
    ) -> Dict[str, Any]:
        """
        Get S&P 500 movers (convenience method).
        
        Args:
            sort: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN
        
        Returns:
            List of S&P 500 movers
        
        Example:
            gainers = endpoint.get_sp500_movers(sort='PERCENT_CHANGE_UP')
        """
        return self.get_movers('$SPX', sort=sort)
    
    def get_nasdaq_movers(
        self,
        sort: str = 'PERCENT_CHANGE_UP'
    ) -> Dict[str, Any]:
        """
        Get NASDAQ movers (convenience method).
        
        Args:
            sort: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN
        
        Returns:
            List of NASDAQ movers
        
        Example:
            gainers = endpoint.get_nasdaq_movers(sort='PERCENT_CHANGE_UP')
        """
        return self.get_movers('$COMPX', sort=sort)
    
    def get_dow_movers(
        self,
        sort: str = 'PERCENT_CHANGE_UP'
    ) -> Dict[str, Any]:
        """
        Get Dow Jones movers (convenience method).
        
        Args:
            sort: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN
        
        Returns:
            List of Dow Jones movers
        
        Example:
            gainers = endpoint.get_dow_movers(sort='PERCENT_CHANGE_UP')
        """
        return self.get_movers('$DJI', sort=sort)
    
    def get_top_gainers(self, index: str = '$SPX') -> Dict[str, Any]:
        """
        Get top gainers for an index (convenience method).
        
        Args:
            index: Index symbol
        
        Returns:
            List of top gainers
        
        Example:
            gainers = endpoint.get_top_gainers('$SPX')
        """
        return self.get_movers(index, sort='PERCENT_CHANGE_UP')
    
    def get_top_losers(self, index: str = '$SPX') -> Dict[str, Any]:
        """
        Get top losers for an index (convenience method).
        
        Args:
            index: Index symbol
        
        Returns:
            List of top losers
        
        Example:
            losers = endpoint.get_top_losers('$SPX')
        """
        return self.get_movers(index, sort='PERCENT_CHANGE_DOWN')
    
    def get_most_active(self, index: str = '$SPX') -> Dict[str, Any]:
        """
        Get most active by volume (convenience method).
        
        Args:
            index: Index symbol
        
        Returns:
            List of most active stocks
        
        Example:
            active = endpoint.get_most_active('$SPX')
        """
        return self.get_movers(index, sort='VOLUME')
