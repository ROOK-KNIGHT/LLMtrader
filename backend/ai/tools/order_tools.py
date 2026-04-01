"""
Order Tools - Order execution and management for LLM
"""

import sys
import os
import json
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class OrderTools:
    """
    Tools for order execution, preview, cancellation, and management.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize order tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'preview_order',
                'description': 'Preview an order before placing it. Shows commission, fees, buying power impact, and validation results. ALWAYS preview before placing orders.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        },
                        'order_payload': {
                            'type': 'object',
                            'description': 'Order specification (same format as place_order)'
                        }
                    },
                    'required': ['order_payload']
                }
            },
            {
                'name': 'place_order',
                'description': 'Place an order (equity, option, spread, bracket, etc.). Supports all order types and strategies. MUST preview first.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        },
                        'order_payload': {
                            'type': 'object',
                            'description': 'Complete order specification with orderType, session, duration, orderLegCollection, etc.'
                        }
                    },
                    'required': ['order_payload']
                }
            },
            {
                'name': 'cancel_order',
                'description': 'Cancel an open order by order ID.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        },
                        'order_id': {
                            'type': 'string',
                            'description': 'Order ID to cancel'
                        }
                    },
                    'required': ['order_id']
                }
            },
            {
                'name': 'replace_order',
                'description': 'Replace/modify an existing order (change price, quantity, etc.).',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        },
                        'order_id': {
                            'type': 'string',
                            'description': 'Order ID to replace'
                        },
                        'order_payload': {
                            'type': 'object',
                            'description': 'New order specification'
                        }
                    },
                    'required': ['order_id', 'order_payload']
                }
            },
            {
                'name': 'get_orders',
                'description': 'Get orders (open, filled, cancelled, all). Filter by status, date range, etc.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        },
                        'from_entered_time': {
                            'type': 'string',
                            'description': 'Start date (ISO 8601 format)'
                        },
                        'to_entered_time': {
                            'type': 'string',
                            'description': 'End date (ISO 8601 format)'
                        },
                        'status': {
                            'type': 'string',
                            'description': 'Order status: WORKING, FILLED, CANCELED, REJECTED, etc.'
                        },
                        'max_results': {
                            'type': 'integer',
                            'description': 'Maximum number of results (default: 100)'
                        }
                    },
                    'required': []
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'preview_order':
            return self._preview_order(**args)
        elif tool_name == 'place_order':
            return self._place_order(**args)
        elif tool_name == 'cancel_order':
            return self._cancel_order(**args)
        elif tool_name == 'replace_order':
            return self._replace_order(**args)
        elif tool_name == 'get_orders':
            return self._get_orders(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    def _get_account_hash(self, account_hash: str = None) -> str:
        """Get account hash (use provided or fetch default)"""
        if account_hash:
            return account_hash
        
        # Get first account
        accounts = self.api.accounts.get_all_accounts()
        if not accounts:
            raise Exception("No accounts found")
        return accounts[0]['securitiesAccount']['accountNumber']
    
    def _preview_order(self, order_payload: Dict[str, Any], account_hash: str = None) -> str:
        """Preview order"""
        try:
            account_hash = self._get_account_hash(account_hash)
            
            preview = self.api.orders.preview_order(account_hash, order_payload)
            
            if not preview:
                return "Error: No preview data returned"
            
            # Extract key info
            order_strategy = preview.get('orderStrategy', {})
            validation = preview.get('orderValidationResult', {})
            commission_fee = preview.get('commissionAndFee', {})
            
            output = "ORDER PREVIEW\n"
            output += "="*80 + "\n\n"
            
            # Order details
            output += "ORDER DETAILS:\n"
            output += f"  Type: {order_strategy.get('orderType', 'N/A')}\n"
            output += f"  Duration: {order_strategy.get('duration', 'N/A')}\n"
            output += f"  Session: {order_strategy.get('session', 'N/A')}\n"
            output += f"  Quantity: {order_strategy.get('quantity', 0)}\n"
            output += f"  Price: ${order_strategy.get('price', 0)}\n"
            output += f"  Order Value: ${order_strategy.get('orderValue', 0):,.2f}\n\n"
            
            # Financial impact
            order_balance = order_strategy.get('orderBalance', {})
            output += "FINANCIAL IMPACT:\n"
            output += f"  Projected Commission: ${order_balance.get('projectedCommission', 0):.2f}\n"
            output += f"  Projected Available Funds: ${order_balance.get('projectedAvailableFund', 0):,.2f}\n"
            output += f"  Projected Buying Power: ${order_balance.get('projectedBuyingPower', 0):,.2f}\n\n"
            
            # Validation results
            output += "VALIDATION:\n"
            
            accepts = validation.get('accepts', [])
            if accepts:
                output += "  ✅ ACCEPTS:\n"
                for accept in accepts:
                    output += f"    - {accept.get('message', 'N/A')}\n"
            
            warns = validation.get('warns', [])
            if warns:
                output += "  ⚠️  WARNINGS:\n"
                for warn in warns:
                    output += f"    - {warn.get('message', 'N/A')}\n"
            
            rejects = validation.get('rejects', [])
            if rejects:
                output += "  ❌ REJECTS:\n"
                for reject in rejects:
                    output += f"    - {reject.get('message', 'N/A')}\n"
            
            alerts = validation.get('alerts', [])
            if alerts:
                output += "  🔔 ALERTS:\n"
                for alert in alerts:
                    output += f"    - {alert.get('message', 'N/A')}\n"
            
            if not accepts and not warns and not rejects and not alerts:
                output += "  No validation messages\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error previewing order: {str(e)}"
    
    def _place_order(self, order_payload: Dict[str, Any], account_hash: str = None) -> str:
        """Place order"""
        try:
            account_hash = self._get_account_hash(account_hash)
            
            result = self.api.orders.place_order(account_hash, order_payload)
            
            output = "✅ ORDER PLACED SUCCESSFULLY\n"
            output += "="*80 + "\n\n"
            output += f"Account: {account_hash}\n"
            output += f"Order Type: {order_payload.get('orderType', 'N/A')}\n"
            output += f"Duration: {order_payload.get('duration', 'N/A')}\n"
            output += f"Session: {order_payload.get('session', 'N/A')}\n\n"
            output += "Order submitted to Schwab. Check order status with get_orders tool.\n"
            
            return output.strip()
            
        except Exception as e:
            return f"❌ Error placing order: {str(e)}"
    
    def _cancel_order(self, order_id: str, account_hash: str = None) -> str:
        """Cancel order"""
        try:
            account_hash = self._get_account_hash(account_hash)
            
            result = self.api.orders.cancel_order(account_hash, order_id)
            
            return f"✅ Order {order_id} cancelled successfully"
            
        except Exception as e:
            return f"❌ Error cancelling order {order_id}: {str(e)}"
    
    def _replace_order(self, order_id: str, order_payload: Dict[str, Any], 
                      account_hash: str = None) -> str:
        """Replace order"""
        try:
            account_hash = self._get_account_hash(account_hash)
            
            result = self.api.orders.replace_order(account_hash, order_id, order_payload)
            
            return f"✅ Order {order_id} replaced successfully"
            
        except Exception as e:
            return f"❌ Error replacing order {order_id}: {str(e)}"
    
    def _get_orders(self, account_hash: str = None, from_entered_time: str = None,
                   to_entered_time: str = None, status: str = None, 
                   max_results: int = 100) -> str:
        """Get orders"""
        try:
            account_hash = self._get_account_hash(account_hash)
            
            orders = self.api.orders.get_orders(
                account_hash=account_hash,
                from_entered_time=from_entered_time,
                to_entered_time=to_entered_time,
                status=status,
                max_results=max_results
            )
            
            if not orders:
                return "No orders found"
            
            output = f"ORDERS ({len(orders)} found)\n"
            output += "="*120 + "\n\n"
            
            for order in orders[:20]:  # Limit to 20
                order_id = order.get('orderId', 'N/A')
                status = order.get('status', 'N/A')
                order_type = order.get('orderType', 'N/A')
                quantity = order.get('quantity', 0)
                filled_qty = order.get('filledQuantity', 0)
                remaining_qty = order.get('remainingQuantity', 0)
                entered_time = order.get('enteredTime', 'N/A')
                
                # Get symbol from order legs
                legs = order.get('orderLegCollection', [])
                symbol = legs[0].get('instrument', {}).get('symbol', 'N/A') if legs else 'N/A'
                instruction = legs[0].get('instruction', 'N/A') if legs else 'N/A'
                
                output += f"Order #{order_id} - {status}\n"
                output += f"  {instruction} {quantity} x {symbol}\n"
                output += f"  Type: {order_type} | Filled: {filled_qty}/{quantity}\n"
                output += f"  Entered: {entered_time}\n\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting orders: {str(e)}"
