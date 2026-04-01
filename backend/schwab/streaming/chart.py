"""
Schwab Chart Streaming Services
CHART_EQUITY, CHART_FUTURES
"""

from typing import List, Optional, Union
from .client import SchwabStreamerClient
from .fields import CHART_EQUITY_FIELDS, CHART_FUTURES_FIELDS


class ChartStreamer:
    """
    Chart streaming for equities and futures (1-minute OHLCV candles).
    """
    
    def __init__(self, client: SchwabStreamerClient):
        """
        Initialize Chart streamer.
        
        Args:
            client: SchwabStreamerClient instance
        """
        self.client = client
    
    async def subscribe_chart_equity(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to equity chart data (1-minute candles).
        
        Args:
            symbols: List of symbols or comma-separated string
            fields: List of field IDs or comma-separated string (default: all fields)
        
        Returns:
            Request ID
        
        Example:
            await streamer.subscribe_chart_equity(['AAPL', 'MSFT'])
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in CHART_EQUITY_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='CHART_EQUITY',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_chart_equity(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing equity chart subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in CHART_EQUITY_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='CHART_EQUITY',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_chart_equity(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from equity chart data"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='CHART_EQUITY',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
    
    async def subscribe_chart_futures(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to futures chart data (1-minute candles).
        
        Args:
            symbols: List of futures symbols or comma-separated string
                    Format: '/ESH24' (E-Mini S&P 500 March 2024)
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        
        Example:
            await streamer.subscribe_chart_futures(['/ES', '/NQ'])
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in CHART_FUTURES_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='CHART_FUTURES',
            command='SUBS',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def add_chart_futures(
        self,
        symbols: Union[List[str], str],
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """Add symbols to existing futures chart subscription"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        if fields is None:
            fields = ','.join(str(i) for i in CHART_FUTURES_FIELDS.keys())
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='CHART_FUTURES',
            command='ADD',
            parameters={'keys': symbols, 'fields': fields}
        )
    
    async def unsubscribe_chart_futures(self, symbols: Union[List[str], str]) -> int:
        """Unsubscribe from futures chart data"""
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        
        return await self.client.send_request(
            service='CHART_FUTURES',
            command='UNSUBS',
            parameters={'keys': symbols}
        )
