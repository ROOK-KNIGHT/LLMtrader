"""
History Tools - Price history data access for LLM
"""

import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class HistoryTools:
    """
    Tools for accessing historical price data (OHLCV candles).
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize history tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'get_price_history',
                'description': 'Get historical OHLCV price data (candles) for any symbol. Supports multiple timeframes from 1-minute to monthly.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock symbol (e.g., AAPL, TSLA, SPY)'
                        },
                        'period_type': {
                            'type': 'string',
                            'description': 'Period type: day, month, year, ytd'
                        },
                        'period': {
                            'type': 'integer',
                            'description': 'Number of periods (e.g., 10 days, 6 months, 1 year)'
                        },
                        'frequency_type': {
                            'type': 'string',
                            'description': 'Frequency type: minute, daily, weekly, monthly'
                        },
                        'frequency': {
                            'type': 'integer',
                            'description': 'Frequency value (e.g., 1, 5, 15, 30 for minutes)'
                        },
                        'start_date': {
                            'type': 'integer',
                            'description': 'Start date as Unix timestamp in milliseconds'
                        },
                        'end_date': {
                            'type': 'integer',
                            'description': 'End date as Unix timestamp in milliseconds'
                        },
                        'need_extended_hours_data': {
                            'type': 'boolean',
                            'description': 'Include extended hours data (default: false)'
                        },
                        'need_previous_close': {
                            'type': 'boolean',
                            'description': 'Include previous close (default: false)'
                        }
                    },
                    'required': ['symbol']
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'get_price_history':
            return self._get_price_history(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    def _get_price_history(self, symbol: str, period_type: str = None, period: int = None,
                          frequency_type: str = None, frequency: int = None,
                          start_date: int = None, end_date: int = None,
                          need_extended_hours_data: bool = False,
                          need_previous_close: bool = False) -> str:
        """Get price history"""
        try:
            history = self.api.price_history.get_price_history(
                symbol=symbol,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequency=frequency,
                start_date=start_date,
                end_date=end_date,
                need_extended_hours_data=need_extended_hours_data,
                need_previous_close=need_previous_close
            )
            
            if not history or 'candles' not in history:
                return f"No price history found for {symbol}"
            
            candles = history['candles']
            
            if not candles:
                return f"No candles found for {symbol}"
            
            # Format output
            output = f"PRICE HISTORY: {symbol}\n"
            output += f"Period: {period_type or 'custom'} | Frequency: {frequency_type or 'N/A'}\n"
            output += f"Candles: {len(candles)}\n"
            output += "="*80 + "\n\n"
            
            # Show first 5 and last 5 candles
            display_candles = []
            if len(candles) <= 10:
                display_candles = candles
            else:
                display_candles = candles[:5] + [None] + candles[-5:]
            
            output += f"{'Date':<20} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}\n"
            output += "-"*80 + "\n"
            
            for candle in display_candles:
                if candle is None:
                    output += "...\n"
                    continue
                
                from datetime import datetime
                dt = datetime.fromtimestamp(candle['datetime'] / 1000)
                date_str = dt.strftime('%Y-%m-%d %H:%M')
                
                output += f"{date_str:<20} "
                output += f"{candle['open']:>10.2f} "
                output += f"{candle['high']:>10.2f} "
                output += f"{candle['low']:>10.2f} "
                output += f"{candle['close']:>10.2f} "
                output += f"{candle['volume']:>12,}\n"
            
            # Summary stats
            closes = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            
            output += "\n" + "="*80 + "\n"
            output += "SUMMARY:\n"
            output += f"  First Close: ${closes[0]:.2f}\n"
            output += f"  Last Close: ${closes[-1]:.2f}\n"
            output += f"  Change: ${closes[-1] - closes[0]:.2f} ({(closes[-1] - closes[0]) / closes[0] * 100:+.2f}%)\n"
            output += f"  High: ${max(c['high'] for c in candles):.2f}\n"
            output += f"  Low: ${min(c['low'] for c in candles):.2f}\n"
            output += f"  Avg Volume: {sum(volumes) / len(volumes):,.0f}\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error getting price history for {symbol}: {str(e)}"
