"""
Schwab Level Two Book Streaming Services
NYSE_BOOK, NASDAQ_BOOK, OPTIONS_BOOK
"""

from typing import List, Optional, Union
from .client import SchwabStreamerClient
from .fields import BOOK_FIELDS


class BookStreamer:
    """
    Level Two book streaming for NYSE, NASDAQ, and OPTIONS.
    """
    
    def __init__(self, client: SchwabStreamerClient):
        """
        Initialize Book streamer.
        
        Args:
            client: SchwabStreamerClient instance
        """
        self.client = client
    
    async def subscribe_nyse_book(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to NYSE Level 2 book data.
        
        Args:
            symbols: List of symbols or comma-separated string
            fields: List of field IDs or comma-separated string (default: all fields)
        
        Returns:
            Request ID
        
        Example:
            await streamer.subscribe_nyse_book(['AAPL', 'MSFT'])
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in BOOK_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='NYSE_BOOK',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_nyse_book(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing NYSE book subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in BOOK_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='NYSE_BOOK',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_nyse_book(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from NYSE book data"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='NYSE_BOOK',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_nasdaq_book(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to NASDAQ Level 2 book data.
        
        Args:
            symbols: List of symbols or comma-separated string
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in BOOK_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='NASDAQ_BOOK',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_nasdaq_book(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing NASDAQ book subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in BOOK_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='NASDAQ_BOOK',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_nasdaq_book(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from NASDAQ book data"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='NASDAQ_BOOK',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_options_book(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to OPTIONS Level 2 book data.
        
        Args:
            symbols: List of option symbols or comma-separated string
                    Format: 'AAPL  260321C00185000'
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in BOOK_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='OPTIONS_BOOK',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_options_book(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing OPTIONS book subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in BOOK_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='OPTIONS_BOOK',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_options_book(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from OPTIONS book data"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='OPTIONS_BOOK',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
