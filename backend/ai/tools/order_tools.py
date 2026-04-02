"""
Order Tools - Order execution and management for LLM
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


# Valid values for order field validation
_VALID_ORDER_TYPES = {'MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT', 'TRAILING_STOP', 'NET_DEBIT', 'NET_CREDIT', 'NET_ZERO'}
_VALID_SESSIONS = {'NORMAL', 'AM', 'PM', 'SEAMLESS'}
_VALID_DURATIONS = {'DAY', 'GOOD_TILL_CANCEL', 'FILL_OR_KILL', 'IMMEDIATE_OR_CANCEL', 'END_OF_WEEK', 'END_OF_MONTH', 'NEXT_END_OF_MONTH', 'UNKNOWN'}
_VALID_INSTRUCTIONS = {'BUY', 'SELL', 'BUY_TO_COVER', 'SELL_SHORT', 'BUY_TO_OPEN', 'BUY_TO_CLOSE', 'SELL_TO_OPEN', 'SELL_TO_CLOSE', 'EXCHANGE'}
_VALID_ASSET_TYPES = {'EQUITY', 'OPTION', 'FUTURE', 'FOREX', 'INDEX', 'CASH_EQUIVALENT', 'FIXED_INCOME', 'PRODUCT'}
_VALID_STATUSES = {'AWAITING_PARENT_ORDER', 'AWAITING_CONDITION', 'AWAITING_STOP_CONDITION', 'AWAITING_MANUAL_REVIEW',
                   'ACCEPTED', 'AWAITING_UR_OUT', 'PENDING_ACTIVATION', 'QUEUED', 'WORKING', 'REJECTED',
                   'PENDING_CANCEL', 'CANCELED', 'PENDING_REPLACE', 'REPLACED', 'FILLED', 'EXPIRED', 'NEW',
                   'AWAITING_RELEASE_TIME', 'PENDING_ACKNOWLEDGEMENT', 'PENDING_RECALL', 'UNKNOWN'}


def _normalize_datetime(dt_str: Optional[str], end_of_day: bool = False) -> Optional[str]:
    """Normalize date string to Schwab's required ISO 8601 format: YYYY-MM-DDTHH:MM:SS.000Z"""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    if dt_str.endswith('Z') and 'T' in dt_str and '.' in dt_str:
        return dt_str
    try:
        if 'T' in dt_str:
            clean = dt_str.rstrip('Z').split('+')[0]
            if '.' in clean:
                clean = clean.split('.')[0]
            dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
        else:
            dt = datetime.strptime(dt_str[:10], '%Y-%m-%d')
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    except ValueError:
        return dt_str


def _validate_order_payload(order_payload: Dict[str, Any]) -> Optional[str]:
    """
    Validate an order payload before sending to Schwab.
    Returns an error message string if invalid, or None if valid.
    """
    if not isinstance(order_payload, dict):
        return "order_payload must be a JSON object/dict"

    # Required top-level fields
    required = ['orderType', 'session', 'duration', 'orderStrategyType', 'orderLegCollection']
    missing = [f for f in required if f not in order_payload]
    if missing:
        return f"order_payload is missing required fields: {missing}. Required: {required}"

    # Validate enum values
    order_type = order_payload.get('orderType', '').upper()
    if order_type not in _VALID_ORDER_TYPES:
        return f"Invalid orderType '{order_type}'. Valid values: {sorted(_VALID_ORDER_TYPES)}"

    session = order_payload.get('session', '').upper()
    if session not in _VALID_SESSIONS:
        return f"Invalid session '{session}'. Valid values: {sorted(_VALID_SESSIONS)}"

    duration = order_payload.get('duration', '').upper()
    if duration not in _VALID_DURATIONS:
        return f"Invalid duration '{duration}'. Valid values: {sorted(_VALID_DURATIONS)}"

    # LIMIT orders require a price
    if order_type == 'LIMIT' and 'price' not in order_payload:
        return "LIMIT orders require a 'price' field"

    # STOP orders require a stopPrice
    if order_type in ('STOP', 'STOP_LIMIT') and 'stopPrice' not in order_payload:
        return f"{order_type} orders require a 'stopPrice' field"

    # Validate order legs
    legs = order_payload.get('orderLegCollection', [])
    if not legs:
        return "orderLegCollection must contain at least one leg"

    for i, leg in enumerate(legs):
        instruction = leg.get('instruction', '').upper()
        if instruction not in _VALID_INSTRUCTIONS:
            return f"Leg {i+1}: Invalid instruction '{instruction}'. Valid values: {sorted(_VALID_INSTRUCTIONS)}"

        qty = leg.get('quantity')
        if qty is None or (isinstance(qty, (int, float)) and qty <= 0):
            return f"Leg {i+1}: quantity must be a positive number, got '{qty}'"

        instrument = leg.get('instrument', {})
        if not instrument.get('symbol'):
            return f"Leg {i+1}: instrument.symbol is required"

        asset_type = instrument.get('assetType', '').upper()
        if asset_type and asset_type not in _VALID_ASSET_TYPES:
            return f"Leg {i+1}: Invalid assetType '{asset_type}'. Valid values: {sorted(_VALID_ASSET_TYPES)}"

    return None  # Valid


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
                            'description': 'Account hash (optional - auto-resolved if not provided)'
                        },
                        'order_payload': {
                            'type': 'object',
                            'description': 'Order specification. Required fields: orderType (MARKET/LIMIT/STOP/STOP_LIMIT), session (NORMAL/AM/PM/SEAMLESS), duration (DAY/GOOD_TILL_CANCEL), orderStrategyType (SINGLE/OCO/TRIGGER), orderLegCollection (array with instruction, quantity, instrument.symbol, instrument.assetType). LIMIT orders also need price. STOP/STOP_LIMIT orders also need stopPrice.'
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
                            'description': 'Account hash (optional - auto-resolved if not provided)'
                        },
                        'order_payload': {
                            'type': 'object',
                            'description': 'Complete order specification. Required fields: orderType (MARKET/LIMIT/STOP/STOP_LIMIT), session (NORMAL/AM/PM/SEAMLESS), duration (DAY/GOOD_TILL_CANCEL), orderStrategyType (SINGLE), orderLegCollection (array with instruction BUY/SELL/BUY_TO_OPEN/etc, quantity, instrument.symbol, instrument.assetType EQUITY/OPTION). LIMIT orders also need price. STOP orders also need stopPrice.'
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
                            'description': 'Account hash (optional - auto-resolved if not provided)'
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
                            'description': 'Account hash (optional - auto-resolved if not provided)'
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
                'description': 'Get orders (open, filled, cancelled, all). Filter by status, date range, etc. Dates default to today if not provided.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - auto-resolved if not provided)'
                        },
                        'from_entered_time': {
                            'type': 'string',
                            'description': 'Start date. Accepts YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.000Z format. Defaults to start of today.'
                        },
                        'to_entered_time': {
                            'type': 'string',
                            'description': 'End date. Accepts YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.000Z format. Defaults to end of today.'
                        },
                        'status': {
                            'type': 'string',
                            'description': 'Order status: WORKING, FILLED, CANCELED, REJECTED, PENDING_ACTIVATION, REPLACED, EXPIRED'
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
        """
        Get account hash — uses provided value or auto-resolves via the cached
        get_default_account_hash() method on the client (always returns hashValue).
        """
        if account_hash:
            # Validate it looks like a hash (64 hex chars), not an account number
            if len(account_hash) < 20:
                # Looks like an account number, not a hash — auto-resolve instead
                return self.api.client.get_default_account_hash()
            return account_hash
        return self.api.client.get_default_account_hash()

    def _check_market_open(self) -> Optional[str]:
        """
        Check if equity market is currently open.
        Returns a warning string if closed, or None if open.
        """
        try:
            hours = self.api.market_hours.get_markets(markets='equity')
            equity = hours.get('equity', {})
            eq_data = equity.get('EQ', equity.get('equity', {}))
            is_open = eq_data.get('isOpen', True)  # Default to True to avoid blocking
            if not is_open:
                session_hours = eq_data.get('sessionHours', {})
                pre = session_hours.get('preMarket', [])
                post = session_hours.get('postMarket', [])
                msg = "⚠️  WARNING: Equity market is currently CLOSED."
                if pre:
                    msg += f" Pre-market: {pre[0].get('start', '?')} - {pre[0].get('end', '?')}."
                if post:
                    msg += f" After-hours: {post[0].get('start', '?')} - {post[0].get('end', '?')}."
                msg += " Order will be queued for next session unless session=AM/PM/SEAMLESS."
                return msg
        except Exception:
            pass  # Don't block orders if market hours check fails
        return None

    def _preview_order(self, order_payload: Dict[str, Any], account_hash: str = None) -> str:
        """Preview order with validation"""
        try:
            # Validate payload
            error = _validate_order_payload(order_payload)
            if error:
                return f"❌ Order validation failed: {error}"

            account_hash = self._get_account_hash(account_hash)

            preview = self.api.orders.preview_order(account_hash, order_payload)

            if not preview:
                return "Error: No preview data returned"

            order_strategy = preview.get('orderStrategy', {})
            validation = preview.get('orderValidationResult', {})

            output = "ORDER PREVIEW\n"
            output += "="*80 + "\n\n"

            output += "ORDER DETAILS:\n"
            output += f"  Type: {order_strategy.get('orderType', 'N/A')}\n"
            output += f"  Duration: {order_strategy.get('duration', 'N/A')}\n"
            output += f"  Session: {order_strategy.get('session', 'N/A')}\n"
            output += f"  Quantity: {order_strategy.get('quantity', 0)}\n"
            output += f"  Price: ${order_strategy.get('price', 0)}\n"
            output += f"  Order Value: ${order_strategy.get('orderValue', 0):,.2f}\n\n"

            order_balance = order_strategy.get('orderBalance', {})
            output += "FINANCIAL IMPACT:\n"
            output += f"  Projected Commission: ${order_balance.get('projectedCommission', 0):.2f}\n"
            output += f"  Projected Available Funds: ${order_balance.get('projectedAvailableFund', 0):,.2f}\n"
            output += f"  Projected Buying Power: ${order_balance.get('projectedBuyingPower', 0):,.2f}\n\n"

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
        """Place order with validation and market hours check"""
        try:
            # Validate payload first
            error = _validate_order_payload(order_payload)
            if error:
                return f"❌ Order validation failed: {error}\n\nPlease fix the order payload and try again."

            account_hash = self._get_account_hash(account_hash)

            # Market hours check (warning only, doesn't block)
            market_warning = self._check_market_open()

            result = self.api.orders.place_order(account_hash, order_payload)

            output = "✅ ORDER PLACED SUCCESSFULLY\n"
            output += "="*80 + "\n\n"
            output += f"Account: {account_hash[:8]}...{account_hash[-8:]}\n"
            output += f"Order Type: {order_payload.get('orderType', 'N/A')}\n"
            output += f"Duration: {order_payload.get('duration', 'N/A')}\n"
            output += f"Session: {order_payload.get('session', 'N/A')}\n\n"

            # Show leg details
            legs = order_payload.get('orderLegCollection', [])
            for leg in legs:
                instr = leg.get('instruction', 'N/A')
                qty = leg.get('quantity', 'N/A')
                sym = leg.get('instrument', {}).get('symbol', 'N/A')
                asset = leg.get('instrument', {}).get('assetType', 'N/A')
                output += f"  {instr} {qty} x {sym} ({asset})\n"

            output += "\nOrder submitted to Schwab. Use get_orders tool to check status.\n"

            if market_warning:
                output += f"\n{market_warning}\n"

            return output.strip()

        except Exception as e:
            return f"❌ Error placing order: {str(e)}"

    def _cancel_order(self, order_id: str, account_hash: str = None) -> str:
        """Cancel order"""
        try:
            if not order_id or not str(order_id).strip():
                return "❌ Error: order_id is required"

            account_hash = self._get_account_hash(account_hash)
            self.api.orders.cancel_order(account_hash, str(order_id))
            return f"✅ Order {order_id} cancelled successfully"

        except Exception as e:
            return f"❌ Error cancelling order {order_id}: {str(e)}"

    def _replace_order(self, order_id: str, order_payload: Dict[str, Any],
                       account_hash: str = None) -> str:
        """Replace order with validation"""
        try:
            if not order_id or not str(order_id).strip():
                return "❌ Error: order_id is required"

            error = _validate_order_payload(order_payload)
            if error:
                return f"❌ Order validation failed: {error}"

            account_hash = self._get_account_hash(account_hash)
            self.api.orders.replace_order(account_hash, str(order_id), order_payload)
            return f"✅ Order {order_id} replaced successfully"

        except Exception as e:
            return f"❌ Error replacing order {order_id}: {str(e)}"

    def _get_orders(self, account_hash: str = None, from_entered_time: str = None,
                    to_entered_time: str = None, status: str = None,
                    max_results: int = 100) -> str:
        """Get orders with date normalization and status validation"""
        try:
            # Validate status if provided
            if status and status.upper() not in _VALID_STATUSES:
                return (f"❌ Invalid status '{status}'. "
                        f"Valid values: WORKING, FILLED, CANCELED, REJECTED, PENDING_ACTIVATION, "
                        f"REPLACED, EXPIRED, QUEUED, AWAITING_CONDITION, PENDING_CANCEL")

            account_hash = self._get_account_hash(account_hash)

            # Normalize dates (orders.py also normalizes, but do it here for clarity)
            from_dt = _normalize_datetime(from_entered_time) if from_entered_time else None
            to_dt = _normalize_datetime(to_entered_time, end_of_day=True) if to_entered_time else None

            orders = self.api.orders.get_orders(
                account_hash=account_hash,
                from_entered_time=from_dt,
                to_entered_time=to_dt,
                status=status.upper() if status else None,
                max_results=max_results
            )

            if not orders:
                return "No orders found for the specified criteria"

            output = f"ORDERS ({len(orders)} found)\n"
            output += "="*120 + "\n\n"

            for order in orders[:20]:
                order_id = order.get('orderId', 'N/A')
                order_status = order.get('status', 'N/A')
                order_type = order.get('orderType', 'N/A')
                quantity = order.get('quantity', 0)
                filled_qty = order.get('filledQuantity', 0)
                entered_time = order.get('enteredTime', 'N/A')

                legs = order.get('orderLegCollection', [])
                symbol = legs[0].get('instrument', {}).get('symbol', 'N/A') if legs else 'N/A'
                instruction = legs[0].get('instruction', 'N/A') if legs else 'N/A'

                output += f"Order #{order_id} - {order_status}\n"
                output += f"  {instruction} {quantity} x {symbol}\n"
                output += f"  Type: {order_type} | Filled: {filled_qty}/{quantity}\n"
                output += f"  Entered: {entered_time}\n\n"

            return output.strip()

        except Exception as e:
            return f"Error getting orders: {str(e)}"
