"""
Schwab Account Activity Streaming Service
ACCT_ACTIVITY
"""

from typing import Optional, Union, List
from .client import SchwabStreamerClient
from .fields import ACCT_ACTIVITY_FIELDS


class AccountActivityStreamer:
    """
    Account activity streaming for order fills, status changes, etc.
    """
    
    def __init__(self, client: SchwabStreamerClient):
        """
        Initialize Account Activity streamer.
        
        Args:
            client: SchwabStreamerClient instance
        """
        self.client = client
    
    async def subscribe_account_activity(
        self,
        key: str = "Account Activity",
        fields: Optional[Union[List[int], str]] = None
    ) -> int:
        """
        Subscribe to account activity stream.
        
        Args:
            key: Client-provided string (default: "Account Activity")
                Only first key is used if multiple are provided
            fields: List of field IDs or comma-separated string
        
        Returns:
            Request ID
        
        Example:
            await streamer.subscribe_account_activity()
        
        Response Format:
            {
                "seq": 123,  # Sequence number (for duplicate detection)
                "key": "Account Activity",
                "1": "12345678",  # Account number
                "2": "OrderFill",  # Message type
                "3": "{...}"  # JSON message data or plain text
            }
        """
        if fields is None:
            fields = "0,1,2,3"
        elif isinstance(fields, list):
            fields = ','.join(str(f) for f in fields)
        
        return await self.client.send_request(
            service='ACCT_ACTIVITY',
            command='SUBS',
            parameters={'keys': key, 'fields': fields}
        )
    
    async def unsubscribe_account_activity(self) -> int:
        """
        Unsubscribe from account activity stream.
        
        Returns:
            Request ID
        """
        return await self.client.send_request(
            service='ACCT_ACTIVITY',
            command='UNSUBS',
            parameters={'keys': "Account Activity"}
        )
