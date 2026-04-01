"""
Schwab Instruments API Endpoints
Wrapper for instrument search and lookup.
"""

from typing import Dict, Any, Optional
from .client import SchwabAPIClient


class InstrumentsEndpoint:
    """
    Schwab Instruments API endpoints.
    
    Endpoints:
    - GET /instruments - Search instruments
    - GET /instruments/{cusip} - Get instrument by CUSIP
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize instruments endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def search_instruments(
        self,
        symbol: str,
        projection: str = 'symbol-search'
    ) -> Dict[str, Any]:
        """
        Search for instruments.
        
        Args:
            symbol: Search query (symbol, name, or description)
            projection: Search type:
                - symbol-search: Search by symbol (default)
                - symbol-regex: Regex search by symbol
                - desc-search: Search by description
                - desc-regex: Regex search by description
                - fundamental: Get fundamental data
        
        Returns:
            Dictionary of matching instruments
        
        Example:
            results = endpoint.search_instruments('AAPL', projection='symbol-search')
        """
        params = {
            'symbol': symbol,
            'projection': projection
        }
        
        return self.client.get('/instruments', params=params)
    
    def get_instrument_by_cusip(
        self,
        cusip: str
    ) -> Dict[str, Any]:
        """
        Get instrument details by CUSIP.
        
        Args:
            cusip: CUSIP identifier
        
        Returns:
            Instrument object
        
        Example:
            instrument = endpoint.get_instrument_by_cusip('037833100')
        """
        return self.client.get(f'/instruments/{cusip}')
    
    def search_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Search instruments by symbol (convenience method).
        
        Args:
            symbol: Symbol to search
        
        Returns:
            Matching instruments
        
        Example:
            results = endpoint.search_by_symbol('AAPL')
        """
        return self.search_instruments(symbol, projection='symbol-search')
    
    def search_by_description(self, description: str) -> Dict[str, Any]:
        """
        Search instruments by description (convenience method).
        
        Args:
            description: Description to search
        
        Returns:
            Matching instruments
        
        Example:
            results = endpoint.search_by_description('Apple Inc')
        """
        return self.search_instruments(description, projection='desc-search')
    
    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get fundamental data for a symbol (convenience method).
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Fundamental data (P/E, EPS, dividend yield, etc.)
        
        Example:
            fundamentals = endpoint.get_fundamental_data('AAPL')
        """
        return self.search_instruments(symbol, projection='fundamental')
    
    def search_regex(
        self,
        pattern: str,
        search_type: str = 'symbol'
    ) -> Dict[str, Any]:
        """
        Search instruments using regex (convenience method).
        
        Args:
            pattern: Regex pattern
            search_type: 'symbol' or 'description'
        
        Returns:
            Matching instruments
        
        Example:
            # Find all symbols starting with 'AA'
            results = endpoint.search_regex('^AA.*', search_type='symbol')
        """
        projection = 'symbol-regex' if search_type == 'symbol' else 'desc-regex'
        return self.search_instruments(pattern, projection=projection)
