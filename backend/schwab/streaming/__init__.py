"""
Schwab Streaming API
Complete WebSocket streaming client for all 13 Schwab streaming services.
"""

from .client import SchwabStreamerClient
from .level_one import LevelOneStreamer
from .book import BookStreamer
from .chart import ChartStreamer
from .screener import ScreenerStreamer
from .account_activity import AccountActivityStreamer
from .fields import parse_fields


class SchwabStreamer:
    """
    Unified Schwab streaming client with all services.
    
    Usage:
        # Initialize with user preferences from GET /userPreference
        streamer = SchwabStreamer(
            access_token=token,
            schwab_client_customer_id=prefs['schwabClientCustomerId'],
            schwab_client_correl_id=prefs['schwabClientCorrelId'],
            schwab_client_channel=prefs['schwabClientChannel'],
            schwab_client_function_id=prefs['schwabClientFunctionId']
        )
        
        # Connect and login
        await streamer.connect()
        
        # Subscribe to services
        await streamer.level_one.subscribe_equities(['AAPL', 'MSFT', 'GOOGL'])
        await streamer.chart.subscribe_chart_equity(['AAPL'])
        await streamer.account_activity.subscribe_account_activity()
        
        # Set up data callback
        async def on_data(data):
            service = data['service']
            content = data['content']
            print(f"Data from {service}: {content}")
        
        streamer.client.on_data = on_data
        
        # Keep connection alive
        await asyncio.sleep(3600)
        
        # Disconnect
        await streamer.disconnect()
    """
    
    def __init__(
        self,
        access_token: str,
        schwab_client_customer_id: str,
        schwab_client_correl_id: str,
        schwab_client_channel: str,
        schwab_client_function_id: str,
        streamer_url: str = "wss://streamer-api.schwab.com/ws"
    ):
        """
        Initialize Schwab Streamer with all services.
        
        Args:
            access_token: OAuth access token
            schwab_client_customer_id: From GET /userPreference
            schwab_client_correl_id: From GET /userPreference
            schwab_client_channel: From GET /userPreference
            schwab_client_function_id: From GET /userPreference
            streamer_url: WebSocket URL
        """
        # Initialize core client
        self.client = SchwabStreamerClient(
            access_token=access_token,
            schwab_client_customer_id=schwab_client_customer_id,
            schwab_client_correl_id=schwab_client_correl_id,
            schwab_client_channel=schwab_client_channel,
            schwab_client_function_id=schwab_client_function_id,
            streamer_url=streamer_url
        )
        
        # Initialize all service streamers
        self.level_one = LevelOneStreamer(self.client)
        self.book = BookStreamer(self.client)
        self.chart = ChartStreamer(self.client)
        self.screener = ScreenerStreamer(self.client)
        self.account_activity = AccountActivityStreamer(self.client)
    
    async def connect(self) -> bool:
        """
        Connect to Schwab WebSocket and login.
        
        Returns:
            True if connected and logged in successfully
        """
        return await self.client.connect()
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        await self.client.disconnect()
    
    @property
    def connected(self) -> bool:
        """Check if connected"""
        return self.client.connected
    
    @property
    def logged_in(self) -> bool:
        """Check if logged in"""
        return self.client.logged_in


__all__ = [
    'SchwabStreamer',
    'SchwabStreamerClient',
    'LevelOneStreamer',
    'BookStreamer',
    'ChartStreamer',
    'ScreenerStreamer',
    'AccountActivityStreamer',
    'parse_fields',
]
