"""
Tools Registry - Central registry for all AI tools
Collects tool definitions and dispatches execution
"""

import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from schwab import SchwabAPI
from .tools.account_tools import AccountTools
from .tools.quote_tools import QuoteTools
from .tools.history_tools import HistoryTools
from .tools.options_tools import OptionsTools
from .tools.order_tools import OrderTools
from .tools.technical_tools import TechnicalTools
from .tools.streaming_tools import StreamingTools
from .tools.position_tools import PositionTools


class ToolsRegistry:
    """
    Central registry for all tools available to the AI.
    Collects tool definitions from all tool modules and dispatches execution.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize tools registry.
        
        Args:
            schwab_api: SchwabAPI instance (shared across all tools)
        """
        self.api = schwab_api or SchwabAPI()
        
        # Initialize all tool modules
        self.account_tools = AccountTools(self.api)
        self.quote_tools = QuoteTools(self.api)
        self.history_tools = HistoryTools(self.api)
        self.options_tools = OptionsTools(self.api)
        self.order_tools = OrderTools(self.api)
        self.technical_tools = TechnicalTools(self.api)
        self.streaming_tools = StreamingTools(self.api)
        self.position_tools = PositionTools(self.api)
        
        # Map tool names to modules
        self.tool_modules = {
            # Account tools
            'get_account_summary': self.account_tools,
            'get_positions': self.account_tools,
            'get_transaction_history': self.account_tools,
            
            # Quote tools
            'get_quote': self.quote_tools,
            'get_quotes_batch': self.quote_tools,
            'get_movers': self.quote_tools,
            'check_market_hours': self.quote_tools,
            'search_instruments': self.quote_tools,
            
            # History tools
            'get_price_history': self.history_tools,
            
            # Options tools
            'get_options_chain': self.options_tools,
            'get_option_expiration_dates': self.options_tools,
            
            # Order tools
            'preview_order': self.order_tools,
            'place_order': self.order_tools,
            'cancel_order': self.order_tools,
            'replace_order': self.order_tools,
            'get_orders': self.order_tools,
            
            # Technical tools
            'calculate_indicator': self.technical_tools,
            
            # Streaming tools
            'subscribe_quotes': self.streaming_tools,
            'unsubscribe_quotes': self.streaming_tools,
            'subscribe_charts': self.streaming_tools,
            'unsubscribe_charts': self.streaming_tools,
            'subscribe_account_activity': self.streaming_tools,
            'unsubscribe_account_activity': self.streaming_tools,
            'get_active_subscriptions': self.streaming_tools,
            
            # Position tools
            'register_position': self.position_tools,
            'update_triggers': self.position_tools,
            'submit_decision': self.position_tools,
            'get_managed_positions': self.position_tools,
            'close_position': self.position_tools,
        }
    
    def get_all_tools_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all tool definitions for the LLM.
        Returns a list of tool schemas in the format expected by LLM APIs.
        """
        tools = []
        
        # Collect from all tool modules
        tools.extend(self.account_tools.get_tool_definitions())
        tools.extend(self.quote_tools.get_tool_definitions())
        tools.extend(self.history_tools.get_tool_definitions())
        tools.extend(self.options_tools.get_tool_definitions())
        tools.extend(self.order_tools.get_tool_definitions())
        tools.extend(self.technical_tools.get_tool_definitions())
        tools.extend(self.streaming_tools.get_tool_definitions())
        tools.extend(self.position_tools.get_tool_definitions())
        
        return tools
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        Execute a tool by name with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            args: Dictionary of arguments for the tool
        
        Returns:
            Tool execution result as string
        """
        # Find the module that handles this tool
        if tool_name not in self.tool_modules:
            return f"Error: Unknown tool '{tool_name}'"
        
        module = self.tool_modules[tool_name]
        
        try:
            # Execute the tool
            result = module.execute(tool_name, args)
            return result
        except Exception as e:
            import traceback
            error_msg = f"Error executing tool '{tool_name}': {str(e)}\n"
            error_msg += traceback.format_exc()
            return error_msg
    
    def get_tool_count(self) -> int:
        """Get total number of available tools"""
        return len(self.tool_modules)
    
    def get_tool_names(self) -> List[str]:
        """Get list of all available tool names"""
        return sorted(self.tool_modules.keys())
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Get tools organized by category"""
        return {
            'Account': [
                'get_account_summary',
                'get_positions',
                'get_transaction_history'
            ],
            'Market Data': [
                'get_quote',
                'get_quotes_batch',
                'get_movers',
                'check_market_hours',
                'search_instruments'
            ],
            'Price History': [
                'get_price_history'
            ],
            'Options': [
                'get_options_chain',
                'get_option_expiration_dates'
            ],
            'Orders': [
                'preview_order',
                'place_order',
                'cancel_order',
                'replace_order',
                'get_orders'
            ],
            'Technical Analysis': [
                'calculate_indicator'
            ],
            'Streaming': [
                'subscribe_quotes',
                'unsubscribe_quotes',
                'subscribe_charts',
                'unsubscribe_charts',
                'subscribe_account_activity',
                'unsubscribe_account_activity',
                'get_active_subscriptions'
            ],
            'Position Management': [
                'register_position',
                'update_triggers',
                'submit_decision',
                'get_managed_positions',
                'close_position'
            ]
        }
