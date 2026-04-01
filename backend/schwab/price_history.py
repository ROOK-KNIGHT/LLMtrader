"""
Schwab Price History API Endpoints
Wrapper for historical OHLCV candle data.
"""

from typing import Dict, Any, Optional
from .client import SchwabAPIClient


class PriceHistoryEndpoint:
    """
    Schwab Price History API endpoints.
    
    Endpoints:
    - GET /pricehistory - Get historical price data (OHLCV candles)
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize price history endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_price_history(
        self,
        symbol: str,
        period_type: Optional[str] = None,
        period: Optional[int] = None,
        frequency_type: Optional[str] = None,
        frequency: Optional[int] = None,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        need_extended_hours_data: bool = False,
        need_previous_close: bool = False
    ) -> Dict[str, Any]:
        """
        Get historical price data (OHLCV candles).
        
        Args:
            symbol: Stock symbol
            period_type: day, month, year, ytd
            period: Number of periods (depends on period_type)
            frequency_type: minute, daily, weekly, monthly
            frequency: Frequency interval (1, 5, 10, 15, 30 for minute; 1 for others)
            start_date: Start date (epoch milliseconds)
            end_date: End date (epoch milliseconds)
            need_extended_hours_data: Include extended hours data
            need_previous_close: Include previous close
        
        Returns:
            Price history object with candles array
        
        Example:
            # Get 1 year of daily data
            history = endpoint.get_price_history(
                'AAPL',
                period_type='year',
                period=1,
                frequency_type='daily',
                frequency=1
            )
            
            # Get 5-minute intraday data for last 5 days
            history = endpoint.get_price_history(
                'AAPL',
                period_type='day',
                period=5,
                frequency_type='minute',
                frequency=5
            )
        """
        params = {'symbol': symbol}
        
        if period_type:
            params['periodType'] = period_type
        if period:
            params['period'] = period
        if frequency_type:
            params['frequencyType'] = frequency_type
        if frequency:
            params['frequency'] = frequency
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if need_extended_hours_data:
            params['needExtendedHoursData'] = 'true'
        if need_previous_close:
            params['needPreviousClose'] = 'true'
        
        return self.client.get('/pricehistory', params=params)
    
    def get_daily_history(
        self,
        symbol: str,
        period: int = 1,
        period_type: str = 'year'
    ) -> Dict[str, Any]:
        """
        Get daily price history (convenience method).
        
        Args:
            symbol: Stock symbol
            period: Number of periods
            period_type: day, month, year, ytd
        
        Returns:
            Price history with daily candles
        
        Example:
            history = endpoint.get_daily_history('AAPL', period=1, period_type='year')
        """
        return self.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type='daily',
            frequency=1
        )
    
    def get_intraday_history(
        self,
        symbol: str,
        frequency: int = 5,
        period: int = 1,
        extended_hours: bool = False
    ) -> Dict[str, Any]:
        """
        Get intraday price history (convenience method).
        
        Args:
            symbol: Stock symbol
            frequency: Minute frequency (1, 5, 10, 15, 30)
            period: Number of days
            extended_hours: Include extended hours data
        
        Returns:
            Price history with minute candles
        
        Example:
            history = endpoint.get_intraday_history('AAPL', frequency=5, period=1)
        """
        return self.get_price_history(
            symbol=symbol,
            period_type='day',
            period=period,
            frequency_type='minute',
            frequency=frequency,
            need_extended_hours_data=extended_hours
        )
    
    def get_weekly_history(
        self,
        symbol: str,
        period: int = 1,
        period_type: str = 'year'
    ) -> Dict[str, Any]:
        """
        Get weekly price history (convenience method).
        
        Args:
            symbol: Stock symbol
            period: Number of periods
            period_type: month, year, ytd
        
        Returns:
            Price history with weekly candles
        
        Example:
            history = endpoint.get_weekly_history('AAPL', period=2, period_type='year')
        """
        return self.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type='weekly',
            frequency=1
        )
    
    def get_monthly_history(
        self,
        symbol: str,
        period: int = 1,
        period_type: str = 'year'
    ) -> Dict[str, Any]:
        """
        Get monthly price history (convenience method).
        
        Args:
            symbol: Stock symbol
            period: Number of periods
            period_type: year, ytd
        
        Returns:
            Price history with monthly candles
        
        Example:
            history = endpoint.get_monthly_history('AAPL', period=5, period_type='year')
        """
        return self.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type='monthly',
            frequency=1
        )
