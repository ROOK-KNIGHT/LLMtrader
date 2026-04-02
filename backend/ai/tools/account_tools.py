"""
Account Tools - Account data access for LLM
"""

import sys
import os
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class AccountTools:
    """
    Tools for accessing account data, positions, and transaction history.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize account tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'get_account_summary',
                'description': 'Get account summary including balances, buying power, and equity. Returns current cash, margin, and total account value.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_positions',
                'description': 'Get all current positions with market values, P&L, and Greeks (for options). Shows what you currently own.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_transaction_history',
                'description': 'Get transaction history (trades, dividends, fees). Filter by date range, symbol, or transaction type.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'account_hash': {
                            'type': 'string',
                            'description': 'Account hash (optional - uses default if not provided)'
                        },
                        'start_date': {
                            'type': 'string',
                            'description': 'Start date in ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)'
                        },
                        'end_date': {
                            'type': 'string',
                            'description': 'End date in ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)'
                        },
                        'symbol': {
                            'type': 'string',
                            'description': 'Filter by symbol (optional)'
                        },
                        'types': {
                            'type': 'string',
                            'description': 'Transaction type: TRADE, DIVIDEND_OR_INTEREST, ACH_RECEIPT, etc.'
                        }
                    },
                    'required': ['start_date', 'end_date']
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'get_account_summary':
            return self._get_account_summary(**args)
        elif tool_name == 'get_positions':
            return self._get_positions(**args)
        elif tool_name == 'get_transaction_history':
            return self._get_transaction_history(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"

    def _resolve_account_hash(self, account_hash: str = None) -> str:
        """
        Resolve account hash — auto-resolves via cached client method if not provided
        or if the value looks like an account number (too short to be a hash).
        """
        if account_hash and len(account_hash) >= 20:
            return account_hash
        return self.api.client.get_default_account_hash()

    def _get_account_summary(self, account_hash: str = None) -> str:
        """Get account summary"""
        try:
            if account_hash:
                result = self.api.accounts.get_account(account_hash)
            else:
                # Get all accounts and use first one
                accounts = self.api.accounts.get_all_accounts()
                if not accounts:
                    return "Error: No accounts found"
                result = accounts[0]
            
            # Extract key info
            account_number = result.get('securitiesAccount', {}).get('accountNumber', 'N/A')
            account_type = result.get('securitiesAccount', {}).get('type', 'N/A')
            
            balances = result.get('securitiesAccount', {}).get('currentBalances', {})
            
            summary = f"""
ACCOUNT SUMMARY
===============
Account: {account_number} ({account_type})

BALANCES:
- Cash: ${balances.get('cashBalance', 0):,.2f}
- Equity: ${balances.get('equity', 0):,.2f}
- Buying Power: ${balances.get('buyingPower', 0):,.2f}
- Margin Balance: ${balances.get('marginBalance', 0):,.2f}
- Available Funds: ${balances.get('availableFunds', 0):,.2f}

MARGIN INFO:
- Maintenance Requirement: ${balances.get('maintenanceRequirement', 0):,.2f}
- Maintenance Call: ${balances.get('maintenanceCall', 0):,.2f}
"""
            return summary.strip()
            
        except Exception as e:
            return f"Error getting account summary: {str(e)}"
    
    def _get_positions(self, account_hash: str = None) -> str:
        """Get all positions"""
        try:
            if account_hash:
                result = self.api.accounts.get_account(account_hash, fields='positions')
            else:
                accounts = self.api.accounts.get_all_accounts(fields='positions')
                if not accounts:
                    return "Error: No accounts found"
                result = accounts[0]
            
            positions = result.get('securitiesAccount', {}).get('positions', [])
            
            if not positions:
                return "No open positions"
            
            output = "CURRENT POSITIONS\n" + "="*80 + "\n\n"
            
            for pos in positions:
                instrument = pos.get('instrument', {})
                symbol = instrument.get('symbol', 'N/A')
                asset_type = instrument.get('assetType', 'N/A')
                
                quantity = pos.get('longQuantity', 0) - pos.get('shortQuantity', 0)
                market_value = pos.get('marketValue', 0)
                avg_price = pos.get('averagePrice', 0)
                current_price = pos.get('currentDayProfitLoss', 0) / quantity if quantity != 0 else 0
                
                pnl = market_value - (avg_price * abs(quantity))
                pnl_pct = (pnl / (avg_price * abs(quantity)) * 100) if avg_price * abs(quantity) != 0 else 0
                
                output += f"{symbol} ({asset_type})\n"
                output += f"  Quantity: {quantity:,.0f}\n"
                output += f"  Avg Price: ${avg_price:,.2f}\n"
                output += f"  Market Value: ${market_value:,.2f}\n"
                output += f"  P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)\n"
                
                # Add Greeks for options
                if asset_type == 'OPTION':
                    output += f"  Delta: {pos.get('delta', 'N/A')}\n"
                    output += f"  Gamma: {pos.get('gamma', 'N/A')}\n"
                    output += f"  Theta: {pos.get('theta', 'N/A')}\n"
                    output += f"  Vega: {pos.get('vega', 'N/A')}\n"
                
                output += "\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting positions: {str(e)}"
    
    def _get_transaction_history(self, start_date: str, end_date: str,
                                 account_hash: str = None, symbol: str = None,
                                 types: str = None) -> str:
        """Get transaction history with date validation and auto account hash resolution"""
        try:
            if not start_date or not end_date:
                return "Error: start_date and end_date are required (e.g. '2026-04-01' or '2026-04-01T00:00:00.000Z')"

            # Auto-resolve account hash (always use hashValue, not account number)
            account_hash = self._resolve_account_hash(account_hash)

            transactions = self.api.transactions.get_transactions(
                account_hash=account_hash,
                start_date=start_date,
                end_date=end_date,
                symbol=symbol,
                types=types
            )
            
            if not transactions:
                return "No transactions found for the specified period"
            
            output = f"TRANSACTION HISTORY ({start_date} to {end_date})\n"
            output += "="*80 + "\n\n"
            
            for txn in transactions:
                txn_type = txn.get('type', 'N/A')
                description = txn.get('description', 'N/A')
                net_amount = txn.get('netAmount', 0)
                trade_date = txn.get('tradeDate', 'N/A')
                
                output += f"{trade_date} | {txn_type}\n"
                output += f"  {description}\n"
                output += f"  Amount: ${net_amount:,.2f}\n\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting transaction history: {str(e)}"
