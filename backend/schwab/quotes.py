"""
Schwab Quotes API Endpoints
Wrapper for real-time and batch quote endpoints.
"""

from typing import Dict, Any, List, Optional, Union
from .client import SchwabAPIClient


class QuotesEndpoint:
    """
    Schwab Quotes API endpoints.
    
    Endpoints:
    - GET /quotes - Get quotes for multiple symbols (batch)
    - GET /quotes/{symbol} - Get quote for single symbol
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize quotes endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_quote(
        self,
        symbol: str,
        fields: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get real-time quote for a single symbol.

        Note: Schwab's GET /quotes/{symbol} endpoint returns 404.
        We use GET /quotes?symbols={symbol} instead and return the symbol's data directly.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', '$SPX', '/ES')
            fields: Optional fields to include (quote, fundamental, extended, reference, regular)

        Returns:
            Quote object with price, volume, bid/ask, etc.

        Example:
            quote = endpoint.get_quote('AAPL')
            price = quote['AAPL']['quote']['lastPrice']
        """
        params = {'symbols': symbol.upper().strip()}
        if fields:
            params['fields'] = fields

        result = self.client.get('/quotes', params=params)
        # Return the symbol's data directly (unwrap from batch response)
        return result.get(symbol.upper().strip(), result)
    
    def get_quotes(
        self,
        symbols: Union[List[str], str],
        fields: Optional[str] = None,
        indicative: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get real-time quotes for multiple symbols (batch request).
        
        Args:
            symbols: List of symbols or comma-separated string (max 500)
            fields: Optional fields to include (quote, fundamental, extended, reference, regular)
            indicative: Include indicative symbol quotes
        
        Returns:
            Dictionary mapping symbols to quote objects
        
        Example:
            quotes = endpoint.get_quotes(['AAPL', 'MSFT', 'GOOGL'])
            aapl_price = quotes['AAPL']['quote']['lastPrice']
        """
        # Convert list to comma-separated string
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        params = {'symbols': symbols}
        if fields:
            params['fields'] = fields
        if indicative:
            params['indicative'] = 'true'
        
        return self.client.get('/quotes', params=params)
    
    def get_equity_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get equity quote (convenience method).
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Quote object
        
        Example:
            quote = endpoint.get_equity_quote('AAPL')
        """
        return self.get_quote(symbol, fields='quote,fundamental')
    
    def get_option_quote(self, option_symbol: str) -> Dict[str, Any]:
        """
        Get option quote (convenience method).
        
        Args:
            option_symbol: Option symbol (e.g., 'AAPL  260321C00185000')
        
        Returns:
            Quote object with Greeks
        
        Example:
            quote = endpoint.get_option_quote('AAPL  260321C00185000')
        """
        return self.get_quote(option_symbol, fields='quote')
    
    def get_index_quote(self, index_symbol: str) -> Dict[str, Any]:
        """
        Get index quote (convenience method).
        
        Args:
            index_symbol: Index symbol (e.g., '$SPX', '$DJI', '$COMPX')
        
        Returns:
            Quote object
        
        Example:
            quote = endpoint.get_index_quote('$SPX')
        """
        return self.get_quote(index_symbol, fields='quote')
    
    def get_futures_quote(self, futures_symbol: str) -> Dict[str, Any]:
        """
        Get futures quote (convenience method).
        
        Args:
            futures_symbol: Futures symbol (e.g., '/ES', '/NQ')
        
        Returns:
            Quote object
        
        Example:
            quote = endpoint.get_futures_quote('/ES')
        """
        return self.get_quote(futures_symbol, fields='quote')
