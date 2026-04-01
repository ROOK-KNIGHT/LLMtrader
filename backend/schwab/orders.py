"""
Schwab Orders API Endpoints
Wrapper for order placement, management, and cancellation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .client import SchwabAPIClient


class OrdersEndpoint:
    """
    Schwab Orders API endpoints.
    
    Endpoints:
    - POST /accounts/{accountHash}/orders - Place order
    - GET /accounts/{accountHash}/orders - Get all orders
    - GET /accounts/{accountHash}/orders/{orderId} - Get specific order
    - DELETE /accounts/{accountHash}/orders/{orderId} - Cancel order
    - PUT /accounts/{accountHash}/orders/{orderId} - Replace order
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize orders endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def place_order(
        self,
        account_hash: str,
        order_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            account_hash: Account hash value
            order_payload: Order specification (see Schwab API docs for format)
        
        Returns:
            Order confirmation with order ID
        
        Example:
            order = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'price': 100.50,
                'orderLegCollection': [{
                    'instruction': 'BUY',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'AAPL',
                        'assetType': 'EQUITY'
                    }
                }]
            }
            result = endpoint.place_order('ABC123', order)
        """
        return self.client.post(f'/accounts/{account_hash}/orders', json_data=order_payload)
    
    def get_orders(
        self,
        account_hash: str,
        from_entered_time: Optional[str] = None,
        to_entered_time: Optional[str] = None,
        status: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all orders for an account.
        
        Args:
            account_hash: Account hash value
            from_entered_time: Start date (ISO 8601 format)
            to_entered_time: End date (ISO 8601 format)
            status: Order status filter (AWAITING_PARENT_ORDER, AWAITING_CONDITION, 
                   AWAITING_STOP_CONDITION, AWAITING_MANUAL_REVIEW, ACCEPTED, 
                   AWAITING_UR_OUT, PENDING_ACTIVATION, QUEUED, WORKING, REJECTED, 
                   PENDING_CANCEL, CANCELED, PENDING_REPLACE, REPLACED, FILLED, EXPIRED)
            max_results: Maximum number of results
        
        Returns:
            List of order objects
        
        Example:
            orders = endpoint.get_orders('ABC123', status='FILLED')
        """
        params = {}
        if from_entered_time:
            params['fromEnteredTime'] = from_entered_time
        if to_entered_time:
            params['toEnteredTime'] = to_entered_time
        if status:
            params['status'] = status
        if max_results:
            params['maxResults'] = max_results
        
        return self.client.get(f'/accounts/{account_hash}/orders', params=params)
    
    def get_order(
        self,
        account_hash: str,
        order_id: str
    ) -> Dict[str, Any]:
        """
        Get specific order details.
        
        Args:
            account_hash: Account hash value
            order_id: Order ID
        
        Returns:
            Order object
        
        Example:
            order = endpoint.get_order('ABC123', '12345')
        """
        return self.client.get(f'/accounts/{account_hash}/orders/{order_id}')
    
    def cancel_order(
        self,
        account_hash: str,
        order_id: str
    ) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            account_hash: Account hash value
            order_id: Order ID to cancel
        
        Returns:
            Cancellation confirmation
        
        Example:
            result = endpoint.cancel_order('ABC123', '12345')
        """
        return self.client.delete(f'/accounts/{account_hash}/orders/{order_id}')
    
    def replace_order(
        self,
        account_hash: str,
        order_id: str,
        order_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Replace an existing order.
        
        Args:
            account_hash: Account hash value
            order_id: Order ID to replace
            order_payload: New order specification
        
        Returns:
            Replacement confirmation
        
        Example:
            new_order = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'price': 105.00,  # Changed price
                'orderLegCollection': [{
                    'instruction': 'BUY',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'AAPL',
                        'assetType': 'EQUITY'
                    }
                }]
            }
            result = endpoint.replace_order('ABC123', '12345', new_order)
        """
        return self.client.put(f'/accounts/{account_hash}/orders/{order_id}', json_data=order_payload)
    
    def preview_order(
        self,
        account_hash: str,
        order_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preview an order before placing it.
        
        Validates the order and returns projected commission, fees, buying power impact,
        and validation results (accepts, rejects, warnings, alerts, reviews).
        
        Args:
            account_hash: Account hash value
            order_payload: Order specification (same format as place_order)
        
        Returns:
            Preview result with:
            - orderStrategy: Order details with projected values
            - orderValidationResult: Validation alerts/accepts/rejects/reviews/warns
            - commissionAndFee: Projected commission and fees
        
        Example:
            order = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'price': '100.50',
                'orderLegCollection': [{
                    'instruction': 'BUY',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'AAPL',
                        'assetType': 'EQUITY'
                    }
                }]
            }
            preview = endpoint.preview_order('ABC123', order)
            
            # Check validation results
            if preview['orderValidationResult']['rejects']:
                print("Order rejected:", preview['orderValidationResult']['rejects'])
            else:
                print("Projected commission:", preview['commissionAndFee']['commission'])
                print("Order value:", preview['orderStrategy']['orderValue'])
        """
        return self.client.post(f'/accounts/{account_hash}/previewOrder', json_data=order_payload)
    
    # Convenience methods for common order types
    
    def place_equity_market_order(
        self,
        account_hash: str,
        symbol: str,
        quantity: int,
        instruction: str = 'BUY',
        session: str = 'NORMAL',
        duration: str = 'DAY'
    ) -> Dict[str, Any]:
        """
        Place a market order for equity.
        
        Args:
            account_hash: Account hash value
            symbol: Stock symbol
            quantity: Number of shares
            instruction: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL, FILL_OR_KILL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'MARKET',
            'session': session,
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': symbol,
                    'assetType': 'EQUITY'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    # Advanced Order Strategies
    
    def place_oco_order(
        self,
        account_hash: str,
        order1: Dict[str, Any],
        order2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Place a One-Cancels-Other (OCO) order.
        Two orders sent simultaneously - if one fills, the other is cancelled.
        
        Args:
            account_hash: Account hash value
            order1: First order specification (without orderStrategyType)
            order2: Second order specification (without orderStrategyType)
        
        Returns:
            Order confirmation
        
        Example:
            # Sell at profit target OR stop loss
            order1 = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'price': '45.97',
                'duration': 'DAY',
                'orderLegCollection': [{
                    'instruction': 'SELL',
                    'quantity': 2,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            order2 = {
                'orderType': 'STOP_LIMIT',
                'session': 'NORMAL',
                'price': '37.00',
                'stopPrice': '37.03',
                'duration': 'DAY',
                'orderLegCollection': [{
                    'instruction': 'SELL',
                    'quantity': 2,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            result = endpoint.place_oco_order('ABC123', order1, order2)
        """
        # Add orderStrategyType to child orders
        order1['orderStrategyType'] = 'SINGLE'
        order2['orderStrategyType'] = 'SINGLE'
        
        oco_order = {
            'orderStrategyType': 'OCO',
            'childOrderStrategies': [order1, order2]
        }
        return self.place_order(account_hash, oco_order)
    
    def place_ota_order(
        self,
        account_hash: str,
        trigger_order: Dict[str, Any],
        triggered_order: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Place a One-Triggers-Another (OTA) order.
        First order triggers second order upon fill.
        
        Args:
            account_hash: Account hash value
            trigger_order: First order that triggers the second (without orderStrategyType)
            triggered_order: Order to submit after first fills (without orderStrategyType)
        
        Returns:
            Order confirmation
        
        Example:
            # Buy at limit, then sell at higher limit
            trigger = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'price': '34.97',
                'duration': 'DAY',
                'orderLegCollection': [{
                    'instruction': 'BUY',
                    'quantity': 10,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            triggered = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'price': '42.03',
                'duration': 'DAY',
                'orderLegCollection': [{
                    'instruction': 'SELL',
                    'quantity': 10,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            result = endpoint.place_ota_order('ABC123', trigger, triggered)
        """
        # Add orderStrategyType
        trigger_order['orderStrategyType'] = 'TRIGGER'
        triggered_order['orderStrategyType'] = 'SINGLE'
        
        # Add child order
        trigger_order['childOrderStrategies'] = [triggered_order]
        
        return self.place_order(account_hash, trigger_order)
    
    def place_ota_oco_order(
        self,
        account_hash: str,
        trigger_order: Dict[str, Any],
        oco_order1: Dict[str, Any],
        oco_order2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Place a One-Triggers-A-One-Cancels-Other (OTA-OCO) order.
        First order triggers two orders - if one of those fills, the other is cancelled.
        Also known as bracket order.
        
        Args:
            account_hash: Account hash value
            trigger_order: First order that triggers OCO (without orderStrategyType)
            oco_order1: First OCO order (profit target)
            oco_order2: Second OCO order (stop loss)
        
        Returns:
            Order confirmation
        
        Example:
            # Buy, then bracket with profit target and stop loss
            trigger = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'price': '14.97',
                'duration': 'DAY',
                'orderLegCollection': [{
                    'instruction': 'BUY',
                    'quantity': 5,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            profit_target = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'price': '15.27',
                'duration': 'GOOD_TILL_CANCEL',
                'orderLegCollection': [{
                    'instruction': 'SELL',
                    'quantity': 5,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            stop_loss = {
                'orderType': 'STOP',
                'session': 'NORMAL',
                'stopPrice': '11.27',
                'duration': 'GOOD_TILL_CANCEL',
                'orderLegCollection': [{
                    'instruction': 'SELL',
                    'quantity': 5,
                    'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}
                }]
            }
            result = endpoint.place_ota_oco_order('ABC123', trigger, profit_target, stop_loss)
        """
        # Add orderStrategyType
        trigger_order['orderStrategyType'] = 'TRIGGER'
        oco_order1['orderStrategyType'] = 'SINGLE'
        oco_order2['orderStrategyType'] = 'SINGLE'
        
        # Build OCO structure
        oco_structure = {
            'orderStrategyType': 'OCO',
            'childOrderStrategies': [oco_order1, oco_order2]
        }
        
        # Add OCO as child of trigger
        trigger_order['childOrderStrategies'] = [oco_structure]
        
        return self.place_order(account_hash, trigger_order)
    
    # Multi-Leg Option Strategies
    
    def place_vertical_spread(
        self,
        account_hash: str,
        long_option: str,
        short_option: str,
        quantity: int,
        price: float,
        instruction: str = 'BUY_TO_OPEN',
        session: str = 'NORMAL',
        duration: str = 'DAY'
    ) -> Dict[str, Any]:
        """
        Place a vertical spread order (call or put spread).
        
        Args:
            account_hash: Account hash value
            long_option: Long option symbol
            short_option: Short option symbol
            quantity: Number of spreads
            price: Net debit/credit price
            instruction: BUY_TO_OPEN (debit spread) or SELL_TO_OPEN (credit spread)
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        
        Example:
            # Bull call spread
            result = endpoint.place_vertical_spread(
                'ABC123',
                'AAPL  240315C00045000',  # Buy $45 call
                'AAPL  240315C00050000',  # Sell $50 call
                2,
                0.50,
                'BUY_TO_OPEN'
            )
        """
        # Determine leg instructions
        if instruction == 'BUY_TO_OPEN':
            long_instruction = 'BUY_TO_OPEN'
            short_instruction = 'SELL_TO_OPEN'
            order_type = 'NET_DEBIT'
        else:  # SELL_TO_OPEN
            long_instruction = 'SELL_TO_CLOSE'
            short_instruction = 'BUY_TO_CLOSE'
            order_type = 'NET_CREDIT'
        
        order = {
            'orderType': order_type,
            'session': session,
            'price': str(price),
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': long_instruction,
                    'quantity': quantity,
                    'instrument': {
                        'symbol': long_option,
                        'assetType': 'OPTION'
                    }
                },
                {
                    'instruction': short_instruction,
                    'quantity': quantity,
                    'instrument': {
                        'symbol': short_option,
                        'assetType': 'OPTION'
                    }
                }
            ]
        }
        return self.place_order(account_hash, order)
    
    def place_equity_limit_order(
        self,
        account_hash: str,
        symbol: str,
        quantity: int,
        price: float,
        instruction: str = 'BUY',
        session: str = 'NORMAL',
        duration: str = 'DAY'
    ) -> Dict[str, Any]:
        """
        Place a limit order for equity.
        
        Args:
            account_hash: Account hash value
            symbol: Stock symbol
            quantity: Number of shares
            price: Limit price
            instruction: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL, FILL_OR_KILL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'LIMIT',
            'session': session,
            'duration': duration,
            'price': str(price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': symbol,
                    'assetType': 'EQUITY'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_option_order(
        self,
        account_hash: str,
        option_symbol: str,
        quantity: int,
        instruction: str,
        order_type: str = 'MARKET',
        price: Optional[float] = None,
        session: str = 'NORMAL',
        duration: str = 'DAY'
    ) -> Dict[str, Any]:
        """
        Place an option order.
        
        Args:
            account_hash: Account hash value
            option_symbol: Option symbol (e.g., 'AAPL  260321C00185000')
            quantity: Number of contracts
            instruction: BUY_TO_OPEN, BUY_TO_CLOSE, SELL_TO_OPEN, SELL_TO_CLOSE
            order_type: MARKET, LIMIT, STOP, STOP_LIMIT
            price: Limit price (required for LIMIT orders)
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL, FILL_OR_KILL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': order_type,
            'session': session,
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': option_symbol,
                    'assetType': 'OPTION'
                }
            }]
        }
        
        if price is not None:
            order['price'] = str(price)
        
        return self.place_order(account_hash, order)
    
    # Stop and Stop-Limit Orders
    
    def place_equity_stop_order(
        self,
        account_hash: str,
        symbol: str,
        quantity: int,
        stop_price: float,
        instruction: str = 'SELL',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a stop order for equity.
        
        Args:
            account_hash: Account hash value
            symbol: Stock symbol
            quantity: Number of shares
            stop_price: Stop trigger price
            instruction: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'STOP',
            'session': session,
            'duration': duration,
            'stopPrice': str(stop_price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': symbol,
                    'assetType': 'EQUITY'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_equity_stop_limit_order(
        self,
        account_hash: str,
        symbol: str,
        quantity: int,
        stop_price: float,
        limit_price: float,
        instruction: str = 'SELL',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order for equity.
        
        Args:
            account_hash: Account hash value
            symbol: Stock symbol
            quantity: Number of shares
            stop_price: Stop trigger price
            limit_price: Limit price after stop is triggered
            instruction: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'STOP_LIMIT',
            'session': session,
            'duration': duration,
            'stopPrice': str(stop_price),
            'price': str(limit_price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': symbol,
                    'assetType': 'EQUITY'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_option_stop_order(
        self,
        account_hash: str,
        option_symbol: str,
        quantity: int,
        stop_price: float,
        instruction: str,
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a stop order for options.
        
        Args:
            account_hash: Account hash value
            option_symbol: Option symbol
            quantity: Number of contracts
            stop_price: Stop trigger price
            instruction: BUY_TO_OPEN, BUY_TO_CLOSE, SELL_TO_OPEN, SELL_TO_CLOSE
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'STOP',
            'session': session,
            'duration': duration,
            'stopPrice': str(stop_price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': option_symbol,
                    'assetType': 'OPTION'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_option_stop_limit_order(
        self,
        account_hash: str,
        option_symbol: str,
        quantity: int,
        stop_price: float,
        limit_price: float,
        instruction: str,
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order for options.
        
        Args:
            account_hash: Account hash value
            option_symbol: Option symbol
            quantity: Number of contracts
            stop_price: Stop trigger price
            limit_price: Limit price after stop is triggered
            instruction: BUY_TO_OPEN, BUY_TO_CLOSE, SELL_TO_OPEN, SELL_TO_CLOSE
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'STOP_LIMIT',
            'session': session,
            'duration': duration,
            'stopPrice': str(stop_price),
            'price': str(limit_price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': option_symbol,
                    'assetType': 'OPTION'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    # Trailing Stop Orders
    
    def place_equity_trailing_stop_order(
        self,
        account_hash: str,
        symbol: str,
        quantity: int,
        trailing_stop_value: float,
        trailing_stop_type: str = 'PERCENT',
        instruction: str = 'SELL',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a trailing stop order for equity.
        
        Args:
            account_hash: Account hash value
            symbol: Stock symbol
            quantity: Number of shares
            trailing_stop_value: Trailing amount (percentage or dollar amount)
            trailing_stop_type: PERCENT or AMOUNT
            instruction: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        
        Example:
            # 5% trailing stop
            endpoint.place_equity_trailing_stop_order('ABC123', 'AAPL', 100, 5.0, 'PERCENT')
            
            # $2 trailing stop
            endpoint.place_equity_trailing_stop_order('ABC123', 'AAPL', 100, 2.0, 'AMOUNT')
        """
        order = {
            'orderType': 'TRAILING_STOP',
            'session': session,
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': symbol,
                    'assetType': 'EQUITY'
                }
            }]
        }
        
        if trailing_stop_type == 'PERCENT':
            order['stopPriceLinkBasis'] = 'BID'
            order['stopPriceLinkType'] = 'PERCENT'
            order['stopPriceOffset'] = str(trailing_stop_value)
        else:  # AMOUNT
            order['stopPriceLinkBasis'] = 'BID'
            order['stopPriceLinkType'] = 'VALUE'
            order['stopPriceOffset'] = str(trailing_stop_value)
        
        return self.place_order(account_hash, order)
    
    def place_option_trailing_stop_order(
        self,
        account_hash: str,
        option_symbol: str,
        quantity: int,
        trailing_stop_value: float,
        trailing_stop_type: str = 'PERCENT',
        instruction: str = 'SELL_TO_CLOSE',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a trailing stop order for options.
        
        Args:
            account_hash: Account hash value
            option_symbol: Option symbol
            quantity: Number of contracts
            trailing_stop_value: Trailing amount (percentage or dollar amount)
            trailing_stop_type: PERCENT or AMOUNT
            instruction: BUY_TO_OPEN, BUY_TO_CLOSE, SELL_TO_OPEN, SELL_TO_CLOSE
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'TRAILING_STOP',
            'session': session,
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': option_symbol,
                    'assetType': 'OPTION'
                }
            }]
        }
        
        if trailing_stop_type == 'PERCENT':
            order['stopPriceLinkBasis'] = 'BID'
            order['stopPriceLinkType'] = 'PERCENT'
            order['stopPriceOffset'] = str(trailing_stop_value)
        else:  # AMOUNT
            order['stopPriceLinkBasis'] = 'BID'
            order['stopPriceLinkType'] = 'VALUE'
            order['stopPriceOffset'] = str(trailing_stop_value)
        
        return self.place_order(account_hash, order)
    
    def place_futures_trailing_stop_order(
        self,
        account_hash: str,
        futures_symbol: str,
        quantity: int,
        trailing_stop_value: float,
        trailing_stop_type: str = 'PERCENT',
        instruction: str = 'SELL',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a trailing stop order for futures.
        
        Args:
            account_hash: Account hash value
            futures_symbol: Futures symbol (e.g., '/ESH24')
            quantity: Number of contracts
            trailing_stop_value: Trailing amount (percentage or dollar amount)
            trailing_stop_type: PERCENT or AMOUNT
            instruction: BUY, SELL
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'TRAILING_STOP',
            'session': session,
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': futures_symbol,
                    'assetType': 'FUTURE'
                }
            }]
        }
        
        if trailing_stop_type == 'PERCENT':
            order['stopPriceLinkBasis'] = 'BID'
            order['stopPriceLinkType'] = 'PERCENT'
            order['stopPriceOffset'] = str(trailing_stop_value)
        else:  # AMOUNT
            order['stopPriceLinkBasis'] = 'BID'
            order['stopPriceLinkType'] = 'VALUE'
            order['stopPriceOffset'] = str(trailing_stop_value)
        
        return self.place_order(account_hash, order)
    
    # Futures Orders
    
    def place_futures_market_order(
        self,
        account_hash: str,
        futures_symbol: str,
        quantity: int,
        instruction: str = 'BUY',
        session: str = 'NORMAL',
        duration: str = 'DAY'
    ) -> Dict[str, Any]:
        """
        Place a market order for futures.
        
        Args:
            account_hash: Account hash value
            futures_symbol: Futures symbol (e.g., '/ESH24')
            quantity: Number of contracts
            instruction: BUY, SELL
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL, FILL_OR_KILL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'MARKET',
            'session': session,
            'duration': duration,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': futures_symbol,
                    'assetType': 'FUTURE'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_futures_limit_order(
        self,
        account_hash: str,
        futures_symbol: str,
        quantity: int,
        price: float,
        instruction: str = 'BUY',
        session: str = 'NORMAL',
        duration: str = 'DAY'
    ) -> Dict[str, Any]:
        """
        Place a limit order for futures.
        
        Args:
            account_hash: Account hash value
            futures_symbol: Futures symbol (e.g., '/ESH24')
            quantity: Number of contracts
            price: Limit price
            instruction: BUY, SELL
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL, FILL_OR_KILL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'LIMIT',
            'session': session,
            'duration': duration,
            'price': str(price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': futures_symbol,
                    'assetType': 'FUTURE'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_futures_stop_order(
        self,
        account_hash: str,
        futures_symbol: str,
        quantity: int,
        stop_price: float,
        instruction: str = 'SELL',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a stop order for futures.
        
        Args:
            account_hash: Account hash value
            futures_symbol: Futures symbol (e.g., '/ESH24')
            quantity: Number of contracts
            stop_price: Stop trigger price
            instruction: BUY, SELL
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'STOP',
            'session': session,
            'duration': duration,
            'stopPrice': str(stop_price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': futures_symbol,
                    'assetType': 'FUTURE'
                }
            }]
        }
        return self.place_order(account_hash, order)
    
    def place_futures_stop_limit_order(
        self,
        account_hash: str,
        futures_symbol: str,
        quantity: int,
        stop_price: float,
        limit_price: float,
        instruction: str = 'SELL',
        session: str = 'NORMAL',
        duration: str = 'GOOD_TILL_CANCEL'
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order for futures.
        
        Args:
            account_hash: Account hash value
            futures_symbol: Futures symbol (e.g., '/ESH24')
            quantity: Number of contracts
            stop_price: Stop trigger price
            limit_price: Limit price after stop is triggered
            instruction: BUY, SELL
            session: NORMAL, AM, PM, SEAMLESS
            duration: DAY, GOOD_TILL_CANCEL
        
        Returns:
            Order confirmation
        """
        order = {
            'orderType': 'STOP_LIMIT',
            'session': session,
            'duration': duration,
            'stopPrice': str(stop_price),
            'price': str(limit_price),
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': instruction,
                'quantity': quantity,
                'instrument': {
                    'symbol': futures_symbol,
                    'assetType': 'FUTURE'
                }
            }]
        }
        return self.place_order(account_hash, order)
