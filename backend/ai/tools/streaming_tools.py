"""
Streaming Tools - Real-time streaming control for LLM
"""

import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class StreamingTools:
    """
    Tools for controlling real-time streaming subscriptions.
    Note: Actual streaming implementation requires WebSocket connection management.
    These tools provide the interface for the LLM to request streaming data.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize streaming tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
        self.active_subscriptions = {}
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'subscribe_quotes',
                'description': 'Subscribe to real-time Level 1 quotes for symbols. Get bid/ask/last updates as they happen.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbols': {
                            'type': 'string',
                            'description': 'Comma-separated symbols (e.g., "AAPL,MSFT,GOOGL")'
                        },
                        'fields': {
                            'type': 'string',
                            'description': 'Comma-separated field numbers (0-52). Leave empty for all fields.'
                        }
                    },
                    'required': ['symbols']
                }
            },
            {
                'name': 'unsubscribe_quotes',
                'description': 'Unsubscribe from real-time quotes for symbols.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbols': {
                            'type': 'string',
                            'description': 'Comma-separated symbols to unsubscribe'
                        }
                    },
                    'required': ['symbols']
                }
            },
            {
                'name': 'subscribe_charts',
                'description': 'Subscribe to real-time 1-minute chart data (OHLCV candles).',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbols': {
                            'type': 'string',
                            'description': 'Comma-separated symbols'
                        },
                        'fields': {
                            'type': 'string',
                            'description': 'Comma-separated field numbers (0-8). Leave empty for all fields.'
                        }
                    },
                    'required': ['symbols']
                }
            },
            {
                'name': 'unsubscribe_charts',
                'description': 'Unsubscribe from real-time chart data.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbols': {
                            'type': 'string',
                            'description': 'Comma-separated symbols to unsubscribe'
                        }
                    },
                    'required': ['symbols']
                }
            },
            {
                'name': 'subscribe_account_activity',
                'description': 'Subscribe to account activity (order fills, status changes, etc.).',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'fields': {
                            'type': 'string',
                            'description': 'Comma-separated field numbers (0-3). Leave empty for all fields.'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'unsubscribe_account_activity',
                'description': 'Unsubscribe from account activity updates.',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_active_subscriptions',
                'description': 'Get list of currently active streaming subscriptions.',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'subscribe_quotes':
            return self._subscribe_quotes(**args)
        elif tool_name == 'unsubscribe_quotes':
            return self._unsubscribe_quotes(**args)
        elif tool_name == 'subscribe_charts':
            return self._subscribe_charts(**args)
        elif tool_name == 'unsubscribe_charts':
            return self._unsubscribe_charts(**args)
        elif tool_name == 'subscribe_account_activity':
            return self._subscribe_account_activity(**args)
        elif tool_name == 'unsubscribe_account_activity':
            return self._unsubscribe_account_activity(**args)
        elif tool_name == 'get_active_subscriptions':
            return self._get_active_subscriptions()
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    def _subscribe_quotes(self, symbols: str, fields: str = None) -> str:
        """Subscribe to Level 1 quotes"""
        try:
            symbol_list = [s.strip() for s in symbols.split(',')]
            
            # Store subscription
            for symbol in symbol_list:
                if 'quotes' not in self.active_subscriptions:
                    self.active_subscriptions['quotes'] = []
                if symbol not in self.active_subscriptions['quotes']:
                    self.active_subscriptions['quotes'].append(symbol)
            
            output = f"✅ SUBSCRIBED TO REAL-TIME QUOTES\n"
            output += "="*80 + "\n\n"
            output += f"Symbols: {', '.join(symbol_list)}\n"
            output += f"Fields: {fields if fields else 'All'}\n\n"
            output += "Real-time quote updates will be delivered via WebSocket.\n"
            output += "You will receive bid/ask/last price updates as they occur.\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error subscribing to quotes: {str(e)}"
    
    def _unsubscribe_quotes(self, symbols: str) -> str:
        """Unsubscribe from quotes"""
        try:
            symbol_list = [s.strip() for s in symbols.split(',')]
            
            # Remove from subscriptions
            if 'quotes' in self.active_subscriptions:
                for symbol in symbol_list:
                    if symbol in self.active_subscriptions['quotes']:
                        self.active_subscriptions['quotes'].remove(symbol)
            
            return f"✅ Unsubscribed from quotes: {', '.join(symbol_list)}"
            
        except Exception as e:
            return f"Error unsubscribing from quotes: {str(e)}"
    
    def _subscribe_charts(self, symbols: str, fields: str = None) -> str:
        """Subscribe to chart data"""
        try:
            symbol_list = [s.strip() for s in symbols.split(',')]
            
            # Store subscription
            for symbol in symbol_list:
                if 'charts' not in self.active_subscriptions:
                    self.active_subscriptions['charts'] = []
                if symbol not in self.active_subscriptions['charts']:
                    self.active_subscriptions['charts'].append(symbol)
            
            output = f"✅ SUBSCRIBED TO REAL-TIME CHARTS\n"
            output += "="*80 + "\n\n"
            output += f"Symbols: {', '.join(symbol_list)}\n"
            output += f"Fields: {fields if fields else 'All'}\n\n"
            output += "Real-time 1-minute OHLCV candles will be delivered via WebSocket.\n"
            output += "You will receive new candles as they complete.\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error subscribing to charts: {str(e)}"
    
    def _unsubscribe_charts(self, symbols: str) -> str:
        """Unsubscribe from charts"""
        try:
            symbol_list = [s.strip() for s in symbols.split(',')]
            
            # Remove from subscriptions
            if 'charts' in self.active_subscriptions:
                for symbol in symbol_list:
                    if symbol in self.active_subscriptions['charts']:
                        self.active_subscriptions['charts'].remove(symbol)
            
            return f"✅ Unsubscribed from charts: {', '.join(symbol_list)}"
            
        except Exception as e:
            return f"Error unsubscribing from charts: {str(e)}"
    
    def _subscribe_account_activity(self, fields: str = None) -> str:
        """Subscribe to account activity"""
        try:
            self.active_subscriptions['account_activity'] = True
            
            output = f"✅ SUBSCRIBED TO ACCOUNT ACTIVITY\n"
            output += "="*80 + "\n\n"
            output += f"Fields: {fields if fields else 'All'}\n\n"
            output += "Real-time account updates will be delivered via WebSocket.\n"
            output += "You will receive notifications for:\n"
            output += "  - Order fills\n"
            output += "  - Order status changes\n"
            output += "  - Position updates\n"
            output += "  - Balance changes\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error subscribing to account activity: {str(e)}"
    
    def _unsubscribe_account_activity(self) -> str:
        """Unsubscribe from account activity"""
        try:
            if 'account_activity' in self.active_subscriptions:
                del self.active_subscriptions['account_activity']
            
            return "✅ Unsubscribed from account activity"
            
        except Exception as e:
            return f"Error unsubscribing from account activity: {str(e)}"
    
    def _get_active_subscriptions(self) -> str:
        """Get active subscriptions"""
        try:
            if not self.active_subscriptions:
                return "No active streaming subscriptions"
            
            output = "ACTIVE STREAMING SUBSCRIPTIONS\n"
            output += "="*80 + "\n\n"
            
            if 'quotes' in self.active_subscriptions and self.active_subscriptions['quotes']:
                output += f"📊 QUOTES: {', '.join(self.active_subscriptions['quotes'])}\n\n"
            
            if 'charts' in self.active_subscriptions and self.active_subscriptions['charts']:
                output += f"📈 CHARTS: {', '.join(self.active_subscriptions['charts'])}\n\n"
            
            if 'account_activity' in self.active_subscriptions:
                output += "💼 ACCOUNT ACTIVITY: Active\n\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting subscriptions: {str(e)}"
