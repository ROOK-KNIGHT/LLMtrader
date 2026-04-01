"""
Schwab Level One Streaming Services
LEVELONE_EQUITIES, LEVELONE_OPTIONS, LEVELONE_FUTURES, LEVELONE_FUTURES_OPTIONS, LEVELONE_FOREX
"""

from typing import List, Optional, Union
from .client import SchwabStreamerClient
from .fields import (
    LEVELONE_EQUITIES_FIELDS,
    LEVELONE_OPTIONS_FIELDS,
    LEVELONE_FUTURES_FIELDS,
    LEVELONE_FUTURES_OPTIONS_FIELDS,
    LEVELONE_FOREX_FIELDS,
    parse_fields
)


class LevelOneStreamer:
    """
    Level One streaming for equities, options, futures, futures options, and forex.
    """
    
    def __init__(self, client: SchwabStreamerClient):
        """
        Initialize Level One streamer.
        
        Args:
            client: SchwabStreamerClient instance
        """
        self.client = client
    
    async def subscribe_equities(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to Level 1 equity quotes.
        
        Args:
            symbols: List of symbols or comma-separated string
            fields: List of field IDs or comma-separated string (default: all fields)
        
        Returns:
            Request ID
        
        Example:
            await streamer.subscribe_equities(['AAPL', 'MSFT', 'GOOGL'])
            await streamer.subscribe_equities('AAPL,MSFT', fields='0,1,2,3,8')
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_EQUITIES_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_EQUITIES',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_equities(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing equity subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_EQUITIES_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_EQUITIES',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_equities(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from equity quotes"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='LEVELONE_EQUITIES',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_options(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to Level 1 option quotes.
        
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
            fields = ','.join(str(i) for i in LEVELONE_OPTIONS_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_OPTIONS',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_options(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing options subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_OPTIONS_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_OPTIONS',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_options(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from option quotes"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='LEVELONE_OPTIONS',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_futures(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to Level 1 futures quotes.
        
        Args:
            symbols: List of futures symbols or comma-separated string
                    Format: '/ESH24' (E-Mini S&P 500 March 2024)
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_FUTURES_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_FUTURES',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_futures(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing futures subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_FUTURES_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_FUTURES',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_futures(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from futures quotes"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='LEVELONE_FUTURES',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_futures_options(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to Level 1 futures options quotes.
        
        Args:
            symbols: List of futures option symbols or comma-separated string
                    Format: './OZCZ23C565'
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_FUTURES_OPTIONS_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_FUTURES_OPTIONS',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_futures_options(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing futures options subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_FUTURES_OPTIONS_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_FUTURES_OPTIONS',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_futures_options(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from futures options quotes"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='LEVELONE_FUTURES_OPTIONS',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_forex(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to Level 1 forex quotes.
        
        Args:
            symbols: List of forex symbols or comma-separated string
                    Format: 'EUR/USD', 'USD/JPY'
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_FOREX_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_FOREX',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_forex(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing forex subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in LEVELONE_FOREX_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='LEVELONE_FOREX',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_forex(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from forex quotes"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='LEVELONE_FOREX',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
