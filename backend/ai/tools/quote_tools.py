"""
Quote Tools - Market data access for LLM
"""

import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI


class QuoteTools:
    """
    Tools for accessing real-time quotes, market data, and market status.
    """

    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize quote tools.

        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'get_quote',
                'description': 'Get real-time quote for a single symbol. Returns bid/ask, last price, volume, change, and more.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock symbol (e.g., AAPL, TSLA, SPY). Will be uppercased automatically.'
                        },
                        'fields': {
                            'type': 'string',
                            'description': 'Comma-separated fields: quote, fundamental, extended, reference, regular (default: quote)'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_quotes_batch',
                'description': 'Get real-time quotes for multiple symbols at once. Efficient for watchlists.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbols': {
                            'type': 'string',
                            'description': 'Comma-separated symbols (e.g., "AAPL,MSFT,GOOGL"). Will be uppercased automatically.'
                        },
                        'fields': {
                            'type': 'string',
                            'description': 'Comma-separated fields: quote, fundamental, extended, reference, regular'
                        },
                        'indicative': {
                            'type': 'boolean',
                            'description': 'Include indicative symbol quotes (default: false)'
                        }
                    },
                    'required': ['symbols']
                }
            },
            {
                'name': 'get_movers',
                'description': 'Get top movers (gainers/losers/most active) for an index.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'index': {
                            'type': 'string',
                            'description': 'Index symbol: $DJI, $COMPX, $SPX, NYSE, NASDAQ, OTCBB, INDEX_ALL, EQUITY_ALL'
                        },
                        'sort': {
                            'type': 'string',
                            'description': 'Sort by: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN'
                        },
                        'frequency': {
                            'type': 'integer',
                            'description': 'Time period in minutes: 0 (all day), 1, 5, 10, 30, 60'
                        }
                    },
                    'required': ['index']
                }
            },
            {
                'name': 'check_market_hours',
                'description': 'Check if market is open and get market hours for specific markets.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'markets': {
                            'type': 'string',
                            'description': 'Comma-separated markets: equity, option, bond, future, forex'
                        },
                        'date': {
                            'type': 'string',
                            'description': 'Date in YYYY-MM-DD format (default: today)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'search_instruments',
                'description': 'Search for instruments by symbol or description. Find stocks, ETFs, options, etc.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Symbol or partial symbol to search (e.g., "AAPL" or "Apple")'
                        },
                        'projection': {
                            'type': 'string',
                            'description': 'Search type: symbol-search, symbol-regex, desc-search, desc-regex, search, fundamental'
                        }
                    },
                    'required': ['symbol', 'projection']
                }
            }
        ]

    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'get_quote':
            return self._get_quote(**args)
        elif tool_name == 'get_quotes_batch':
            return self._get_quotes_batch(**args)
        elif tool_name == 'get_movers':
            return self._get_movers(**args)
        elif tool_name == 'check_market_hours':
            return self._check_market_hours(**args)
        elif tool_name == 'search_instruments':
            return self._search_instruments(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"

    @staticmethod
    def _clean_symbol(symbol: str) -> str:
        """Normalize a symbol: uppercase, strip whitespace."""
        return symbol.strip().upper()

    def _get_quote(self, symbol: str, fields: str = 'quote') -> str:
        """Get single quote"""
        try:
            if not symbol or not symbol.strip():
                return "Error: symbol is required"
            symbol = self._clean_symbol(symbol)

            quote = self.api.quotes.get_quote(symbol, fields=fields)

            if not quote:
                return f"No quote data found for {symbol}"

            # Extract quote data
            q = quote.get('quote', {}) if 'quote' in quote else quote

            output = f"QUOTE: {symbol}\n" + "="*50 + "\n"
            output += f"Last: ${q.get('lastPrice', 0):.2f}\n"
            output += f"Bid: ${q.get('bidPrice', 0):.2f} x {q.get('bidSize', 0)}\n"
            output += f"Ask: ${q.get('askPrice', 0):.2f} x {q.get('askSize', 0)}\n"
            output += f"Change: ${q.get('netChange', 0):.2f} ({q.get('netPercentChange', 0):.2f}%)\n"
            output += f"Volume: {q.get('totalVolume', 0):,}\n"
            output += f"High: ${q.get('highPrice', 0):.2f}\n"
            output += f"Low: ${q.get('lowPrice', 0):.2f}\n"
            output += f"Open: ${q.get('openPrice', 0):.2f}\n"
            output += f"Close: ${q.get('closePrice', 0):.2f}\n"
            output += f"52W High: ${q.get('52WkHigh', 0):.2f}\n"
            output += f"52W Low: ${q.get('52WkLow', 0):.2f}\n"

            return output.strip()

        except Exception as e:
            return f"Error getting quote for {symbol}: {str(e)}"

    def _get_quotes_batch(self, symbols: str, fields: str = None, indicative: bool = False) -> str:
        """Get batch quotes"""
        try:
            if not symbols or not symbols.strip():
                return "Error: symbols is required (comma-separated, e.g. 'AAPL,MSFT')"
            # Normalize each symbol
            symbols = ','.join(s.strip().upper() for s in symbols.split(',') if s.strip())

            quotes = self.api.quotes.get_quotes(symbols, fields=fields, indicative=indicative)

            if not quotes:
                return f"No quote data found for {symbols}"

            output = f"BATCH QUOTES: {symbols}\n" + "="*80 + "\n\n"

            for symbol, data in quotes.items():
                q = data.get('quote', {}) if 'quote' in data else data

                output += f"{symbol}: ${q.get('lastPrice', 0):.2f} "
                output += f"({q.get('netPercentChange', 0):+.2f}%) "
                output += f"Vol: {q.get('totalVolume', 0):,}\n"

            return output.strip()

        except Exception as e:
            return f"Error getting batch quotes: {str(e)}"

    def _get_movers(self, index: str, sort: str = 'PERCENT_CHANGE_UP', frequency: int = 0) -> str:
        """Get market movers"""
        try:
            if not index or not index.strip():
                return "Error: index is required (e.g. $SPX, NYSE, NASDAQ)"

            movers = self.api.movers.get_movers(index, sort=sort, frequency=frequency)

            if not movers:
                return f"No movers data found for {index}"

            output = f"TOP MOVERS: {index} ({sort})\n" + "="*80 + "\n\n"

            for mover in movers[:10]:  # Top 10
                symbol = mover.get('symbol', 'N/A')
                description = mover.get('description', 'N/A')
                last = mover.get('last', 0)
                change_pct = mover.get('netPercentChange', 0)
                volume = mover.get('totalVolume', 0)

                output += f"{symbol}: ${last:.2f} ({change_pct:+.2f}%) "
                output += f"Vol: {volume:,}\n"
                output += f"  {description}\n\n"

            return output.strip()

        except Exception as e:
            return f"Error getting movers: {str(e)}"

    def _check_market_hours(self, markets: str = 'equity', date: str = None) -> str:
        """Check market hours"""
        try:
            hours = self.api.market_hours.get_market_hours(markets, date=date)

            if not hours:
                return "No market hours data available"

            output = "MARKET HOURS\n" + "="*50 + "\n\n"

            for market, data in hours.items():
                market_data = data.get(market, {})
                is_open = market_data.get('isOpen', False)
                session_hours = market_data.get('sessionHours', {})

                output += f"{market.upper()}: {'OPEN' if is_open else 'CLOSED'}\n"

                if session_hours:
                    for session, times in session_hours.items():
                        if times:
                            start = times[0].get('start', 'N/A')
                            end = times[0].get('end', 'N/A')
                            output += f"  {session}: {start} - {end}\n"

                output += "\n"

            return output.strip()

        except Exception as e:
            return f"Error checking market hours: {str(e)}"

    def _search_instruments(self, symbol: str, projection: str) -> str:
        """Search for instruments"""
        try:
            if not symbol or not symbol.strip():
                return "Error: symbol is required"

            valid_projections = {'symbol-search', 'symbol-regex', 'desc-search', 'desc-regex', 'search', 'fundamental'}
            if projection not in valid_projections:
                return f"Error: Invalid projection '{projection}'. Valid values: {sorted(valid_projections)}"

            results = self.api.instruments.search_instruments(symbol, projection)

            if not results:
                return f"No instruments found matching '{symbol}'"

            output = f"INSTRUMENT SEARCH: {symbol}\n" + "="*80 + "\n\n"

            for key, instrument in list(results.items())[:20]:  # Top 20 results
                sym = instrument.get('symbol', 'N/A')
                desc = instrument.get('description', 'N/A')
                asset_type = instrument.get('assetType', 'N/A')
                exchange = instrument.get('exchange', 'N/A')

                output += f"{sym} ({asset_type})\n"
                output += f"  {desc}\n"
                output += f"  Exchange: {exchange}\n\n"

            return output.strip()

        except Exception as e:
            return f"Error searching instruments: {str(e)}"
