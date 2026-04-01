"""
Options Tools - Options chain and analysis for LLM
"""

import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class OptionsTools:
    """
    Tools for accessing options chains, Greeks, and options analysis.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize options tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'get_options_chain',
                'description': 'Get full options chain with Greeks for a symbol. Filter by strike, expiration, contract type, etc.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Underlying symbol (e.g., AAPL, TSLA, SPY)'
                        },
                        'contract_type': {
                            'type': 'string',
                            'description': 'Contract type: CALL, PUT, ALL (default: ALL)'
                        },
                        'strike_count': {
                            'type': 'integer',
                            'description': 'Number of strikes above/below ATM (default: 10)'
                        },
                        'include_quotes': {
                            'type': 'boolean',
                            'description': 'Include underlying quote (default: true)'
                        },
                        'strategy': {
                            'type': 'string',
                            'description': 'Strategy: SINGLE, ANALYTICAL, COVERED, VERTICAL, CALENDAR, STRANGLE, STRADDLE, BUTTERFLY, CONDOR, DIAGONAL, COLLAR, ROLL'
                        },
                        'interval': {
                            'type': 'number',
                            'description': 'Strike interval (e.g., 5 for $5 strikes)'
                        },
                        'strike': {
                            'type': 'number',
                            'description': 'Specific strike price'
                        },
                        'range': {
                            'type': 'string',
                            'description': 'Range: ITM, NTM, OTM, SAK, SBK, SNK, ALL'
                        },
                        'from_date': {
                            'type': 'string',
                            'description': 'Start date for expiration range (YYYY-MM-DD)'
                        },
                        'to_date': {
                            'type': 'string',
                            'description': 'End date for expiration range (YYYY-MM-DD)'
                        },
                        'expiration_month': {
                            'type': 'string',
                            'description': 'Expiration month: JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC, ALL'
                        },
                        'option_type': {
                            'type': 'string',
                            'description': 'Option type: S (Standard), NS (Non-Standard), ALL'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_option_expiration_dates',
                'description': 'Get all available expiration dates for options on a symbol.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Underlying symbol (e.g., AAPL, TSLA, SPY)'
                        }
                    },
                    'required': ['symbol']
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'get_options_chain':
            return self._get_options_chain(**args)
        elif tool_name == 'get_option_expiration_dates':
            return self._get_option_expiration_dates(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    def _get_options_chain(self, symbol: str, contract_type: str = 'ALL',
                          strike_count: int = 10, include_quotes: bool = True,
                          **kwargs) -> str:
        """Get options chain"""
        try:
            chain = self.api.options_chain.get_options_chain(
                symbol=symbol,
                contract_type=contract_type,
                strike_count=strike_count,
                include_quotes=include_quotes,
                **kwargs
            )
            
            if not chain:
                return f"No options chain found for {symbol}"
            
            # Extract underlying info
            underlying = chain.get('underlying', {})
            underlying_price = underlying.get('last', 0)
            
            output = f"OPTIONS CHAIN: {symbol}\n"
            output += f"Underlying Price: ${underlying_price:.2f}\n"
            output += "="*120 + "\n\n"
            
            # Process calls
            if 'callExpDateMap' in chain and chain['callExpDateMap']:
                output += "CALLS:\n"
                output += f"{'Exp':<12} {'Strike':>8} {'Bid':>8} {'Ask':>8} {'Last':>8} {'Vol':>8} {'OI':>10} {'IV':>8} {'Delta':>8} {'Gamma':>8} {'Theta':>8}\n"
                output += "-"*120 + "\n"
                
                call_count = 0
                for exp_date, strikes in sorted(chain['callExpDateMap'].items())[:3]:  # First 3 expirations
                    exp_str = exp_date.split(':')[0]
                    for strike_price, contracts in sorted(strikes.items()):
                        if call_count >= 15:  # Limit output
                            break
                        contract = contracts[0]
                        
                        output += f"{exp_str:<12} "
                        output += f"{contract.get('strikePrice', 0):>8.2f} "
                        output += f"{contract.get('bid', 0):>8.2f} "
                        output += f"{contract.get('ask', 0):>8.2f} "
                        output += f"{contract.get('last', 0):>8.2f} "
                        output += f"{contract.get('totalVolume', 0):>8} "
                        output += f"{contract.get('openInterest', 0):>10} "
                        output += f"{contract.get('volatility', 0):>8.1f} "
                        output += f"{contract.get('delta', 0):>8.3f} "
                        output += f"{contract.get('gamma', 0):>8.4f} "
                        output += f"{contract.get('theta', 0):>8.3f}\n"
                        
                        call_count += 1
                
                output += "\n"
            
            # Process puts
            if 'putExpDateMap' in chain and chain['putExpDateMap']:
                output += "PUTS:\n"
                output += f"{'Exp':<12} {'Strike':>8} {'Bid':>8} {'Ask':>8} {'Last':>8} {'Vol':>8} {'OI':>10} {'IV':>8} {'Delta':>8} {'Gamma':>8} {'Theta':>8}\n"
                output += "-"*120 + "\n"
                
                put_count = 0
                for exp_date, strikes in sorted(chain['putExpDateMap'].items())[:3]:  # First 3 expirations
                    exp_str = exp_date.split(':')[0]
                    for strike_price, contracts in sorted(strikes.items()):
                        if put_count >= 15:  # Limit output
                            break
                        contract = contracts[0]
                        
                        output += f"{exp_str:<12} "
                        output += f"{contract.get('strikePrice', 0):>8.2f} "
                        output += f"{contract.get('bid', 0):>8.2f} "
                        output += f"{contract.get('ask', 0):>8.2f} "
                        output += f"{contract.get('last', 0):>8.2f} "
                        output += f"{contract.get('totalVolume', 0):>8} "
                        output += f"{contract.get('openInterest', 0):>10} "
                        output += f"{contract.get('volatility', 0):>8.1f} "
                        output += f"{contract.get('delta', 0):>8.3f} "
                        output += f"{contract.get('gamma', 0):>8.4f} "
                        output += f"{contract.get('theta', 0):>8.3f}\n"
                        
                        put_count += 1
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting options chain for {symbol}: {str(e)}"
    
    def _get_option_expiration_dates(self, symbol: str) -> str:
        """Get option expiration dates"""
        try:
            # Get chain with minimal data to extract expirations
            chain = self.api.options_chain.get_options_chain(
                symbol=symbol,
                contract_type='CALL',
                strike_count=1
            )
            
            if not chain or 'callExpDateMap' not in chain:
                return f"No expiration dates found for {symbol}"
            
            expirations = sorted(chain['callExpDateMap'].keys())
            
            output = f"OPTION EXPIRATION DATES: {symbol}\n"
            output += "="*50 + "\n\n"
            
            for exp in expirations:
                exp_date = exp.split(':')[0]
                days_to_exp = exp.split(':')[1] if ':' in exp else 'N/A'
                output += f"{exp_date} ({days_to_exp} days)\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting expiration dates for {symbol}: {str(e)}"
