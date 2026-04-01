"""
Schwab Options Chain API Endpoints
Wrapper for options chain and expiration data.
"""

from typing import Dict, Any, Optional
from .client import SchwabAPIClient


class OptionsChainEndpoint:
    """
    Schwab Options Chain API endpoints.
    
    Endpoints:
    - GET /chains - Get options chain with Greeks
    - GET /expirationchain - Get available expiration dates
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize options chain endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_option_chain(
        self,
        symbol: str,
        contract_type: Optional[str] = None,
        strike_count: Optional[int] = None,
        include_underlying_quote: bool = True,
        strategy: Optional[str] = None,
        interval: Optional[float] = None,
        strike: Optional[float] = None,
        range: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        volatility: Optional[float] = None,
        underlying_price: Optional[float] = None,
        interest_rate: Optional[float] = None,
        days_to_expiration: Optional[int] = None,
        exp_month: Optional[str] = None,
        option_type: Optional[str] = None,
        entitlement: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get options chain with Greeks.
        
        Args:
            symbol: Underlying symbol
            contract_type: CALL, PUT, or ALL
            strike_count: Number of strikes above/below ATM
            include_underlying_quote: Include underlying quote
            strategy: SINGLE, ANALYTICAL, COVERED, VERTICAL, CALENDAR, STRANGLE, 
                     STRADDLE, BUTTERFLY, CONDOR, DIAGONAL, COLLAR, ROLL
            interval: Strike interval
            strike: Specific strike price
            range: ITM, NTM, OTM, SAK, SBK, SNK, ALL
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            volatility: Volatility to use in calculations
            underlying_price: Underlying price to use
            interest_rate: Interest rate to use
            days_to_expiration: Days to expiration
            exp_month: Expiration month (JAN, FEB, etc.)
            option_type: S (Standard), NS (Non-Standard), ALL
            entitlement: PN, NP, PP
        
        Returns:
            Options chain object with calls and puts
        
        Example:
            chain = endpoint.get_option_chain(
                'AAPL',
                contract_type='ALL',
                strike_count=10,
                range='NTM'
            )
        """
        params = {'symbol': symbol}
        
        if contract_type:
            params['contractType'] = contract_type
        if strike_count:
            params['strikeCount'] = strike_count
        if include_underlying_quote:
            params['includeUnderlyingQuote'] = 'true'
        if strategy:
            params['strategy'] = strategy
        if interval:
            params['interval'] = interval
        if strike:
            params['strike'] = strike
        if range:
            params['range'] = range
        if from_date:
            params['fromDate'] = from_date
        if to_date:
            params['toDate'] = to_date
        if volatility:
            params['volatility'] = volatility
        if underlying_price:
            params['underlyingPrice'] = underlying_price
        if interest_rate:
            params['interestRate'] = interest_rate
        if days_to_expiration:
            params['daysToExpiration'] = days_to_expiration
        if exp_month:
            params['expMonth'] = exp_month
        if option_type:
            params['optionType'] = option_type
        if entitlement:
            params['entitlement'] = entitlement
        
        return self.client.get('/chains', params=params)
    
    def get_expiration_chain(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Get available expiration dates for options.
        
        Args:
            symbol: Underlying symbol
        
        Returns:
            Expiration chain object with available dates
        
        Example:
            expirations = endpoint.get_expiration_chain('AAPL')
        """
        return self.client.get('/expirationchain', params={'symbol': symbol})
    
    def get_atm_options(
        self,
        symbol: str,
        strike_count: int = 5,
        contract_type: str = 'ALL'
    ) -> Dict[str, Any]:
        """
        Get at-the-money options (convenience method).
        
        Args:
            symbol: Underlying symbol
            strike_count: Number of strikes above/below ATM
            contract_type: CALL, PUT, or ALL
        
        Returns:
            Options chain focused on ATM strikes
        
        Example:
            atm_options = endpoint.get_atm_options('AAPL', strike_count=5)
        """
        return self.get_option_chain(
            symbol=symbol,
            contract_type=contract_type,
            strike_count=strike_count,
            range='NTM'
        )
    
    def get_weekly_options(
        self,
        symbol: str,
        days_to_expiration: int = 7
    ) -> Dict[str, Any]:
        """
        Get weekly options (convenience method).
        
        Args:
            symbol: Underlying symbol
            days_to_expiration: Max days to expiration
        
        Returns:
            Options chain for weekly expirations
        
        Example:
            weeklies = endpoint.get_weekly_options('SPY')
        """
        return self.get_option_chain(
            symbol=symbol,
            days_to_expiration=days_to_expiration,
            contract_type='ALL'
        )
    
    def get_monthly_options(
        self,
        symbol: str,
        exp_month: str
    ) -> Dict[str, Any]:
        """
        Get monthly options for specific month (convenience method).
        
        Args:
            symbol: Underlying symbol
            exp_month: Expiration month (JAN, FEB, MAR, etc.)
        
        Returns:
            Options chain for specified month
        
        Example:
            monthly = endpoint.get_monthly_options('AAPL', 'APR')
        """
        return self.get_option_chain(
            symbol=symbol,
            exp_month=exp_month,
            contract_type='ALL'
        )
