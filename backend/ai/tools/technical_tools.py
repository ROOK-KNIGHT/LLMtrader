"""
Technical Tools - TA-Lib indicator calculations for LLM
"""

import sys
import os
import numpy as np
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from schwab import SchwabAPI

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False


class TechnicalTools:
    """
    Tools for calculating technical indicators using TA-Lib.
    Fetches price history and computes indicators on demand.
    """
    
    def __init__(self, schwab_api: SchwabAPI = None):
        """
        Initialize technical tools.
        
        Args:
            schwab_api: SchwabAPI instance (will create if not provided)
        """
        self.api = schwab_api or SchwabAPI()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'calculate_indicator',
                'description': 'Calculate ANY TA-Lib technical indicator on demand. Fetches price history and computes the indicator. Supports: RSI, MACD, SMA, EMA, BBANDS, ATR, ADX, STOCH, OBV, CCI, WILLR, MFI, ROC, MOM, TRIX, ULTOSC, AROON, PLUS_DI, MINUS_DI, SAR, and 100+ more.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock symbol (e.g., AAPL, TSLA, SPY)'
                        },
                        'indicator': {
                            'type': 'string',
                            'description': 'Indicator name (e.g., RSI, MACD, SMA, EMA, BBANDS, ATR, ADX, STOCH, OBV, CCI, WILLR, MFI, etc.)'
                        },
                        'period_type': {
                            'type': 'string',
                            'description': 'Period type for price history: day, month, year (default: day)'
                        },
                        'period': {
                            'type': 'integer',
                            'description': 'Number of periods (default: 30 days)'
                        },
                        'frequency_type': {
                            'type': 'string',
                            'description': 'Frequency: minute, daily, weekly (default: daily)'
                        },
                        'frequency': {
                            'type': 'integer',
                            'description': 'Frequency value (e.g., 1, 5, 15, 30 for minutes, 1 for daily)'
                        },
                        'timeperiod': {
                            'type': 'integer',
                            'description': 'Indicator period (e.g., 14 for RSI(14), 20 for SMA(20))'
                        },
                        'fastperiod': {
                            'type': 'integer',
                            'description': 'Fast period for indicators like MACD (default: 12)'
                        },
                        'slowperiod': {
                            'type': 'integer',
                            'description': 'Slow period for indicators like MACD (default: 26)'
                        },
                        'signalperiod': {
                            'type': 'integer',
                            'description': 'Signal period for indicators like MACD (default: 9)'
                        },
                        'nbdevup': {
                            'type': 'number',
                            'description': 'Number of standard deviations up for Bollinger Bands (default: 2)'
                        },
                        'nbdevdn': {
                            'type': 'number',
                            'description': 'Number of standard deviations down for Bollinger Bands (default: 2)'
                        },
                        'matype': {
                            'type': 'integer',
                            'description': 'Moving average type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3'
                        }
                    },
                    'required': ['symbol', 'indicator']
                }
            }
        ]
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name == 'calculate_indicator':
            return self._calculate_indicator(**args)
        else:
            return f"Error: Unknown tool '{tool_name}'"
    
    def _calculate_indicator(self, symbol: str, indicator: str, 
                            period_type: str = 'day', period: int = 30,
                            frequency_type: str = 'daily', frequency: int = 1,
                            **kwargs) -> str:
        """Calculate technical indicator"""
        try:
            if not TALIB_AVAILABLE:
                return "Error: TA-Lib not installed. Install with: pip install TA-Lib"
            
            # Fetch price history
            history = self.api.price_history.get_price_history(
                symbol=symbol,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequency=frequency
            )
            
            if not history or 'candles' not in history:
                return f"No price history found for {symbol}"
            
            candles = history['candles']
            
            if len(candles) < 2:
                return f"Insufficient data for {symbol} (need at least 2 candles)"
            
            # Extract OHLCV arrays
            opens = np.array([c['open'] for c in candles])
            highs = np.array([c['high'] for c in candles])
            lows = np.array([c['low'] for c in candles])
            closes = np.array([c['close'] for c in candles])
            volumes = np.array([c['volume'] for c in candles])
            
            # Calculate indicator
            indicator_upper = indicator.upper()
            result = None
            
            # Momentum Indicators
            if indicator_upper == 'RSI':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.RSI(closes, timeperiod=timeperiod)
                result_name = f"RSI({timeperiod})"
                
            elif indicator_upper == 'MACD':
                fastperiod = kwargs.get('fastperiod', 12)
                slowperiod = kwargs.get('slowperiod', 26)
                signalperiod = kwargs.get('signalperiod', 9)
                macd, signal, hist = talib.MACD(closes, fastperiod=fastperiod, 
                                               slowperiod=slowperiod, signalperiod=signalperiod)
                result = (macd, signal, hist)
                result_name = f"MACD({fastperiod},{slowperiod},{signalperiod})"
                
            elif indicator_upper == 'STOCH':
                fastk_period = kwargs.get('fastk_period', 5)
                slowk_period = kwargs.get('slowk_period', 3)
                slowd_period = kwargs.get('slowd_period', 3)
                slowk, slowd = talib.STOCH(highs, lows, closes, 
                                          fastk_period=fastk_period,
                                          slowk_period=slowk_period,
                                          slowd_period=slowd_period)
                result = (slowk, slowd)
                result_name = "STOCH"
                
            elif indicator_upper == 'CCI':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.CCI(highs, lows, closes, timeperiod=timeperiod)
                result_name = f"CCI({timeperiod})"
                
            elif indicator_upper == 'WILLR':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.WILLR(highs, lows, closes, timeperiod=timeperiod)
                result_name = f"WILLR({timeperiod})"
                
            elif indicator_upper == 'MFI':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.MFI(highs, lows, closes, volumes, timeperiod=timeperiod)
                result_name = f"MFI({timeperiod})"
                
            elif indicator_upper == 'ROC':
                timeperiod = kwargs.get('timeperiod', 10)
                result = talib.ROC(closes, timeperiod=timeperiod)
                result_name = f"ROC({timeperiod})"
                
            elif indicator_upper == 'MOM':
                timeperiod = kwargs.get('timeperiod', 10)
                result = talib.MOM(closes, timeperiod=timeperiod)
                result_name = f"MOM({timeperiod})"
                
            # Moving Averages
            elif indicator_upper == 'SMA':
                timeperiod = kwargs.get('timeperiod', 20)
                result = talib.SMA(closes, timeperiod=timeperiod)
                result_name = f"SMA({timeperiod})"
                
            elif indicator_upper == 'EMA':
                timeperiod = kwargs.get('timeperiod', 20)
                result = talib.EMA(closes, timeperiod=timeperiod)
                result_name = f"EMA({timeperiod})"
                
            elif indicator_upper == 'WMA':
                timeperiod = kwargs.get('timeperiod', 20)
                result = talib.WMA(closes, timeperiod=timeperiod)
                result_name = f"WMA({timeperiod})"
                
            elif indicator_upper == 'DEMA':
                timeperiod = kwargs.get('timeperiod', 20)
                result = talib.DEMA(closes, timeperiod=timeperiod)
                result_name = f"DEMA({timeperiod})"
                
            elif indicator_upper == 'TEMA':
                timeperiod = kwargs.get('timeperiod', 20)
                result = talib.TEMA(closes, timeperiod=timeperiod)
                result_name = f"TEMA({timeperiod})"
                
            # Volatility Indicators
            elif indicator_upper == 'BBANDS':
                timeperiod = kwargs.get('timeperiod', 20)
                nbdevup = kwargs.get('nbdevup', 2)
                nbdevdn = kwargs.get('nbdevdn', 2)
                upper, middle, lower = talib.BBANDS(closes, timeperiod=timeperiod,
                                                    nbdevup=nbdevup, nbdevdn=nbdevdn)
                result = (upper, middle, lower)
                result_name = f"BBANDS({timeperiod},{nbdevup},{nbdevdn})"
                
            elif indicator_upper == 'ATR':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.ATR(highs, lows, closes, timeperiod=timeperiod)
                result_name = f"ATR({timeperiod})"
                
            elif indicator_upper == 'NATR':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.NATR(highs, lows, closes, timeperiod=timeperiod)
                result_name = f"NATR({timeperiod})"
                
            # Trend Indicators
            elif indicator_upper == 'ADX':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.ADX(highs, lows, closes, timeperiod=timeperiod)
                result_name = f"ADX({timeperiod})"
                
            elif indicator_upper == 'ADXR':
                timeperiod = kwargs.get('timeperiod', 14)
                result = talib.ADXR(highs, lows, closes, timeperiod=timeperiod)
                result_name = f"ADXR({timeperiod})"
                
            elif indicator_upper == 'AROON':
                timeperiod = kwargs.get('timeperiod', 14)
                aroondown, aroonup = talib.AROON(highs, lows, timeperiod=timeperiod)
                result = (aroondown, aroonup)
                result_name = f"AROON({timeperiod})"
                
            elif indicator_upper == 'SAR':
                acceleration = kwargs.get('acceleration', 0.02)
                maximum = kwargs.get('maximum', 0.2)
                result = talib.SAR(highs, lows, acceleration=acceleration, maximum=maximum)
                result_name = "SAR"
                
            # Volume Indicators
            elif indicator_upper == 'OBV':
                result = talib.OBV(closes, volumes)
                result_name = "OBV"
                
            elif indicator_upper == 'AD':
                result = talib.AD(highs, lows, closes, volumes)
                result_name = "AD (Chaikin A/D)"
                
            elif indicator_upper == 'ADOSC':
                fastperiod = kwargs.get('fastperiod', 3)
                slowperiod = kwargs.get('slowperiod', 10)
                result = talib.ADOSC(highs, lows, closes, volumes, 
                                    fastperiod=fastperiod, slowperiod=slowperiod)
                result_name = f"ADOSC({fastperiod},{slowperiod})"
                
            else:
                return f"Error: Indicator '{indicator}' not supported. Supported: RSI, MACD, SMA, EMA, BBANDS, ATR, ADX, STOCH, OBV, CCI, WILLR, MFI, ROC, MOM, AROON, SAR, AD, ADOSC, and more."
            
            # Format output
            output = f"TECHNICAL INDICATOR: {result_name} for {symbol}\n"
            output += f"Period: {period_type} {period} | Frequency: {frequency_type} {frequency}\n"
            output += "="*80 + "\n\n"
            
            # Handle different result types
            if isinstance(result, tuple):
                # Multiple outputs (e.g., MACD, BBANDS, STOCH)
                if indicator_upper == 'MACD':
                    macd, signal, hist = result
                    output += f"{'Date':<20} {'Price':>10} {'MACD':>10} {'Signal':>10} {'Hist':>10}\n"
                    output += "-"*80 + "\n"
                    for i in range(max(0, len(closes) - 10), len(closes)):
                        from datetime import datetime
                        dt = datetime.fromtimestamp(candles[i]['datetime'] / 1000)
                        output += f"{dt.strftime('%Y-%m-%d %H:%M'):<20} "
                        output += f"{closes[i]:>10.2f} "
                        output += f"{macd[i]:>10.4f} " if not np.isnan(macd[i]) else f"{'N/A':>10} "
                        output += f"{signal[i]:>10.4f} " if not np.isnan(signal[i]) else f"{'N/A':>10} "
                        output += f"{hist[i]:>10.4f}\n" if not np.isnan(hist[i]) else f"{'N/A':>10}\n"
                    
                    output += f"\nCurrent: MACD={macd[-1]:.4f}, Signal={signal[-1]:.4f}, Hist={hist[-1]:.4f}\n"
                    
                elif indicator_upper == 'BBANDS':
                    upper, middle, lower = result
                    output += f"{'Date':<20} {'Price':>10} {'Upper':>10} {'Middle':>10} {'Lower':>10}\n"
                    output += "-"*80 + "\n"
                    for i in range(max(0, len(closes) - 10), len(closes)):
                        from datetime import datetime
                        dt = datetime.fromtimestamp(candles[i]['datetime'] / 1000)
                        output += f"{dt.strftime('%Y-%m-%d %H:%M'):<20} "
                        output += f"{closes[i]:>10.2f} "
                        output += f"{upper[i]:>10.2f} " if not np.isnan(upper[i]) else f"{'N/A':>10} "
                        output += f"{middle[i]:>10.2f} " if not np.isnan(middle[i]) else f"{'N/A':>10} "
                        output += f"{lower[i]:>10.2f}\n" if not np.isnan(lower[i]) else f"{'N/A':>10}\n"
                    
                    output += f"\nCurrent: Upper=${upper[-1]:.2f}, Middle=${middle[-1]:.2f}, Lower=${lower[-1]:.2f}\n"
                    
                elif indicator_upper == 'STOCH':
                    slowk, slowd = result
                    output += f"{'Date':<20} {'Price':>10} {'%K':>10} {'%D':>10}\n"
                    output += "-"*80 + "\n"
                    for i in range(max(0, len(closes) - 10), len(closes)):
                        from datetime import datetime
                        dt = datetime.fromtimestamp(candles[i]['datetime'] / 1000)
                        output += f"{dt.strftime('%Y-%m-%d %H:%M'):<20} "
                        output += f"{closes[i]:>10.2f} "
                        output += f"{slowk[i]:>10.2f} " if not np.isnan(slowk[i]) else f"{'N/A':>10} "
                        output += f"{slowd[i]:>10.2f}\n" if not np.isnan(slowd[i]) else f"{'N/A':>10}\n"
                    
                    output += f"\nCurrent: %K={slowk[-1]:.2f}, %D={slowd[-1]:.2f}\n"
                    
                elif indicator_upper == 'AROON':
                    aroondown, aroonup = result
                    output += f"{'Date':<20} {'Price':>10} {'AroonUp':>10} {'AroonDown':>10}\n"
                    output += "-"*80 + "\n"
                    for i in range(max(0, len(closes) - 10), len(closes)):
                        from datetime import datetime
                        dt = datetime.fromtimestamp(candles[i]['datetime'] / 1000)
                        output += f"{dt.strftime('%Y-%m-%d %H:%M'):<20} "
                        output += f"{closes[i]:>10.2f} "
                        output += f"{aroonup[i]:>10.2f} " if not np.isnan(aroonup[i]) else f"{'N/A':>10} "
                        output += f"{aroondown[i]:>10.2f}\n" if not np.isnan(aroondown[i]) else f"{'N/A':>10}\n"
                    
                    output += f"\nCurrent: AroonUp={aroonup[-1]:.2f}, AroonDown={aroondown[-1]:.2f}\n"
            else:
                # Single output (e.g., RSI, SMA, ATR)
                output += f"{'Date':<20} {'Price':>10} {result_name:>15}\n"
                output += "-"*80 + "\n"
                
                # Show last 10 values
                for i in range(max(0, len(closes) - 10), len(closes)):
                    from datetime import datetime
                    dt = datetime.fromtimestamp(candles[i]['datetime'] / 1000)
                    output += f"{dt.strftime('%Y-%m-%d %H:%M'):<20} "
                    output += f"{closes[i]:>10.2f} "
                    if not np.isnan(result[i]):
                        output += f"{result[i]:>15.2f}\n"
                    else:
                        output += f"{'N/A':>15}\n"
                
                output += f"\nCurrent {result_name}: {result[-1]:.2f}\n"
            
            return output.strip()
            
        except Exception as e:
            import traceback
            return f"Error calculating {indicator} for {symbol}: {str(e)}\n{traceback.format_exc()}"
