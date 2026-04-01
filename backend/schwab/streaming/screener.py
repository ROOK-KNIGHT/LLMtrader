"""
Schwab Screener Streaming Services
SCREENER_EQUITY, SCREENER_OPTION
"""

from typing import List, Optional, Union
from .client import SchwabStreamerClient
from .fields import SCREENER_FIELDS


class ScreenerStreamer:
    """
    Screener streaming for equities and options (advances/decliners).
    """
    
    def __init__(self, client: SchwabStreamerClient):
        """
        Initialize Screener streamer.
        
        Args:
            client: SchwabStreamerClient instance
        """
        self.client = client
    
    async def subscribe_screener_equity(
        self,
        keys: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to equity screener data.
        
        Args:
            keys: List of screener keys or comma-separated string
                 Format: (PREFIX)_(SORTFIELD)_(FREQUENCY)
                 PREFIX: $COMPX, $DJI, $SPX, INDEX_ALL, NYSE, NASDAQ, OTCBB, EQUITY_ALL
                 SORTFIELD: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME
                 FREQUENCY: 0, 1, 5, 10, 30, 60 (minutes, 0 = all day)
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        
        Example:
            # Top gainers on S&P 500 for the day
            await streamer.subscribe_screener_equity('$SPX_PERCENT_CHANGE_UP_0')
            
            # Most active on NASDAQ in last 5 minutes
            await streamer.subscribe_screener_equity('NASDAQ_VOLUME_5')
        """
        if isinstance(keys, list):
            keys = ','.join(keys)
        
        if fields is None:
            fields = ','.join(str(i) for i in SCREENER_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='SCREENER_EQUITY',
            command='SUBS',
            parameters={'keys': keys, 'fields': fields}
        )
    
    async def add_screener_equity(
        self,
        keys: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add keys to existing equity screener subscription"""
        if isinstance(keys, list):
            keys = ','.join(keys)
        
        if fields is None:
            fields = ','.join(str(i) for i in SCREENER_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='SCREENER_EQUITY',
            command='ADD',
            parameters={'keys': keys, 'fields': fields}
        )
    
    async def unsubscribe_screener_equity(self, keys: Union[List[str], str]) -> int:
        """Unsubscribe from equity screener data"""
        if isinstance(keys, list):
            keys = ','.join(keys)
        
        return await self.client.send_request(
            service='SCREENER_EQUITY',
            command='UNSUBS',
            parameters={'keys': keys}
        )
    
    async def subscribe_screener_option(
        self,
        keys: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to option screener data.
        
        Args:
            keys: List of screener keys or comma-separated string
                 Format: (PREFIX)_(SORTFIELD)_(FREQUENCY)
                 PREFIX: OPTION_PUT, OPTION_CALL, OPTION_ALL
                 SORTFIELD: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME
                 FREQUENCY: 0, 1, 5, 10, 30, 60 (minutes, 0 = all day)
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        
        Example:
            # Most active calls for the day
            await streamer.subscribe_screener_option('OPTION_CALL_VOLUME_0')
            
            # Top gaining puts in last 30 minutes
            await streamer.subscribe_screener_option('OPTION_PUT_PERCENT_CHANGE_UP_30')
        """
        if isinstance(keys, list):
            keys = ','.join(keys)
        
        if fields is None:
            fields = ','.join(str(i) for i in SCREENER_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='SCREENER_OPTION',
            command='SUBS',
            parameters={'keys': keys, 'fields': fields}
        )
    
    async def add_screener_option(
        self,
        keys: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add keys to existing option screener subscription"""
        if isinstance(keys, list):
            keys = ','.join(keys)
        
        if fields is None:
            fields = ','.join(str(i) for i in SCREENER_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='SCREENER_OPTION',
            command='ADD',
            parameters={'keys': keys, 'fields': fields}
        )
    
    async def unsubscribe_screener_option(self, keys: Union[List[str], str]) -> int:
        """Unsubscribe from option screener data"""
        if isinstance(keys, list):
            keys = ','.join(keys)
        
        return await self.client.send_request(
            service='SCREENER_OPTION',
            command='UNSUBS',
            parameters={'keys': keys}
        )
