"""
Schwab Streamer WebSocket Client
Core WebSocket connection manager with login, heartbeat, and reconnect logic.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)


class SchwabStreamerClient:
    """
    Core Schwab WebSocket streaming client.
    
    Features:
    - WebSocket connection management
    - LOGIN/LOGOUT handling
    - Heartbeat monitoring
    - Auto-reconnect on disconnect
    - Request ID management
    - Callback system for data/response/notify events
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
        Initialize Schwab Streamer client.
        
        Args:
            access_token: OAuth access token
            schwab_client_customer_id: From GET /userPreference
            schwab_client_correl_id: From GET /userPreference
            schwab_client_channel: From GET /userPreference
            schwab_client_function_id: From GET /userPreference
            streamer_url: WebSocket URL
        """
        self.access_token = access_token
        self.schwab_client_customer_id = schwab_client_customer_id
        self.schwab_client_correl_id = schwab_client_correl_id
        self.schwab_client_channel = schwab_client_channel
        self.schwab_client_function_id = schwab_client_function_id
        self.streamer_url = streamer_url
        
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.logged_in = False
        self.request_id = 0
        
        # Callbacks
        self.on_data: Optional[Callable] = None
        self.on_response: Optional[Callable] = None
        self.on_notify: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Tasks
        self.receive_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Heartbeat tracking
        self.last_heartbeat = None
        self.heartbeat_timeout = 60  # seconds
    
    def _get_next_request_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def connect(self) -> bool:
        """
        Connect to Schwab WebSocket and login.
        
        Returns:
            True if connected and logged in successfully
        """
        try:
            logger.info(f"Connecting to {self.streamer_url}")
            self.websocket = await websockets.connect(
                self.streamer_url,
                ping_interval=20,
                ping_timeout=10
            )
            self.connected = True
            logger.info("WebSocket connected")
            
            # Start receive loop
            self.receive_task = asyncio.create_task(self._receive_loop())
            
            # Login
            login_success = await self.login()
            if not login_success:
                await self.disconnect()
                return False
            
            # Start heartbeat monitor
            self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        try:
            if self.logged_in:
                await self.logout()
            
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            if self.receive_task:
                self.receive_task.cancel()
                try:
                    await self.receive_task
                except asyncio.CancelledError:
                    pass
            
            if self.websocket:
                await self.websocket.close()
            
            self.connected = False
            self.logged_in = False
            logger.info("Disconnected from WebSocket")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def login(self) -> bool:
        """
        Send LOGIN request.
        
        Returns:
            True if login successful
        """
        request = {
            "requests": [{
                "requestid": str(self._get_next_request_id()),
                "service": "ADMIN",
                "command": "LOGIN",
                "SchwabClientCustomerId": self.schwab_client_customer_id,
                "SchwabClientCorrelId": self.schwab_client_correl_id,
                "parameters": {
                    "Authorization": self.access_token,
                    "SchwabClientChannel": self.schwab_client_channel,
                    "SchwabClientFunctionId": self.schwab_client_function_id
                }
            }]
        }
        
        try:
            await self.websocket.send(json.dumps(request))
            logger.info("LOGIN request sent")
            
            # Wait for login response (handled in receive loop)
            # For now, assume success after short delay
            await asyncio.sleep(1)
            
            if self.logged_in:
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    async def logout(self) -> bool:
        """
        Send LOGOUT request.
        
        Returns:
            True if logout successful
        """
        request = {
            "requests": [{
                "requestid": str(self._get_next_request_id()),
                "service": "ADMIN",
                "command": "LOGOUT",
                "SchwabClientCustomerId": self.schwab_client_customer_id,
                "SchwabClientCorrelId": self.schwab_client_correl_id,
                "parameters": {}
            }]
        }
        
        try:
            await self.websocket.send(json.dumps(request))
            logger.info("LOGOUT request sent")
            self.logged_in = False
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def send_request(
        self,
        service: str,
        command: str,
        parameters: Dict[str, Any]
    ) -> int:
        """
        Send a request to the streamer.
        
        Args:
            service: Service name (e.g., LEVELONE_EQUITIES)
            command: Command (SUBS, ADD, UNSUBS, VIEW)
            parameters: Request parameters
        
        Returns:
            Request ID
        """
        request_id = self._get_next_request_id()
        
        request = {
            "requests": [{
                "requestid": str(request_id),
                "service": service,
                "command": command,
                "SchwabClientCustomerId": self.schwab_client_customer_id,
                "SchwabClientCorrelId": self.schwab_client_correl_id,
                "parameters": parameters
            }]
        }
        
        try:
            await self.websocket.send(json.dumps(request))
            logger.debug(f"Sent {command} request for {service} (ID: {request_id})")
            return request_id
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return -1
    
    async def _receive_loop(self):
        """Main receive loop for WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.connected = False
            self.logged_in = False
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")
            self.connected = False
            self.logged_in = False
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        # Response messages
        if 'response' in data:
            for response in data['response']:
                await self._handle_response(response)
        
        # Data messages
        if 'data' in data:
            for data_item in data['data']:
                await self._handle_data(data_item)
        
        # Notify messages (heartbeat)
        if 'notify' in data:
            for notify in data['notify']:
                await self._handle_notify(notify)
    
    async def _handle_response(self, response: Dict[str, Any]):
        """Handle response message"""
        service = response.get('service')
        command = response.get('command')
        content = response.get('content', {})
        code = content.get('code')
        msg = content.get('msg', '')
        
        logger.debug(f"Response: {service} {command} - Code {code}: {msg}")
        
        # Handle LOGIN response
        if service == 'ADMIN' and command == 'LOGIN':
            if code == 0:
                self.logged_in = True
                logger.info(f"Login successful: {msg}")
            else:
                self.logged_in = False
                logger.error(f"Login failed: {msg}")
        
        # Call user callback
        if self.on_response:
            try:
                await self.on_response(response)
            except Exception as e:
                logger.error(f"Error in response callback: {e}")
    
    async def _handle_data(self, data: Dict[str, Any]):
        """Handle data message"""
        service = data.get('service')
        timestamp = data.get('timestamp')
        content = data.get('content', [])
        
        logger.debug(f"Data: {service} - {len(content)} items")
        
        # Call user callback
        if self.on_data:
            try:
                await self.on_data(data)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")
    
    async def _handle_notify(self, notify: Dict[str, Any]):
        """Handle notify message (heartbeat)"""
        if 'heartbeat' in notify:
            self.last_heartbeat = datetime.now()
            logger.debug(f"Heartbeat: {notify['heartbeat']}")
        
        # Call user callback
        if self.on_notify:
            try:
                await self.on_notify(notify)
            except Exception as e:
                logger.error(f"Error in notify callback: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor heartbeat and reconnect if needed"""
        try:
            while self.connected:
                await asyncio.sleep(self.heartbeat_timeout)
                
                if self.last_heartbeat:
                    elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
                    if elapsed > self.heartbeat_timeout:
                        logger.warning(f"No heartbeat for {elapsed}s, reconnecting...")
                        await self.reconnect()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in heartbeat monitor: {e}")
    
    async def reconnect(self):
        """Reconnect to WebSocket"""
        logger.info("Attempting to reconnect...")
        await self.disconnect()
        await asyncio.sleep(5)
        await self.connect()
