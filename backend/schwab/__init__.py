"""
Schwab API Client
Complete wrapper for all Schwab API endpoints.
"""

from .client import SchwabAPIClient
from .accounts import AccountsEndpoint
from .orders import OrdersEndpoint
from .transactions import TransactionsEndpoint
from .quotes import QuotesEndpoint
from .price_history import PriceHistoryEndpoint
from .options_chain import OptionsChainEndpoint
from .movers import MoversEndpoint
from .market_hours import MarketHoursEndpoint
from .instruments import InstrumentsEndpoint
from .user_preferences import UserPreferencesEndpoint


class SchwabAPI:
    """
    Unified Schwab API client with all endpoints.
    
    Usage:
        api = SchwabAPI()
        
        # Accounts
        accounts = api.accounts.get_all_accounts()
        positions = api.accounts.get_positions('account_hash')
        
        # Orders
        api.orders.place_equity_market_order('account_hash', 'AAPL', 10, 'BUY')
        orders = api.orders.get_orders('account_hash')
        
        # Quotes
        quote = api.quotes.get_quote('AAPL')
        quotes = api.quotes.get_quotes(['AAPL', 'MSFT', 'GOOGL'])
        
        # Price History
        history = api.price_history.get_daily_history('AAPL', period=1, period_type='year')
        
        # Options Chain
        chain = api.options_chain.get_option_chain('AAPL', strike_count=10)
        
        # Market Movers
        gainers = api.movers.get_top_gainers('$SPX')
        
        # Market Hours
        hours = api.market_hours.get_equity_hours()
        
        # Instruments
        results = api.instruments.search_by_symbol('AAPL')
        
        # Transactions
        transactions = api.transactions.get_transactions('account_hash')
        
        # User Preferences
        prefs = api.user_preferences.get_user_preferences()
    """
    
    def __init__(
        self,
        aws_region: str = None,
        credentials_secret_name: str = "production/schwab-api/credentials",
        tokens_secret_name: str = "production/schwab-api/tokens",
        max_retries: int = 3,
        rate_limit_delay: float = 0.5
    ):
        """
        Initialize Schwab API client with all endpoints.
        
        Args:
            aws_region: AWS region for Secrets Manager
            credentials_secret_name: Secret name for API credentials
            tokens_secret_name: Secret name for access/refresh tokens
            max_retries: Max retry attempts for failed requests
            rate_limit_delay: Delay between requests (seconds)
        """
        # Initialize core client
        self.client = SchwabAPIClient(
            aws_region=aws_region,
            credentials_secret_name=credentials_secret_name,
            tokens_secret_name=tokens_secret_name,
            max_retries=max_retries,
            rate_limit_delay=rate_limit_delay
        )
        
        # Initialize all endpoints
        self.accounts = AccountsEndpoint(self.client)
        self.orders = OrdersEndpoint(self.client)
        self.transactions = TransactionsEndpoint(self.client)
        self.quotes = QuotesEndpoint(self.client)
        self.price_history = PriceHistoryEndpoint(self.client)
        self.options_chain = OptionsChainEndpoint(self.client)
        self.movers = MoversEndpoint(self.client)
        self.market_hours = MarketHoursEndpoint(self.client)
        self.instruments = InstrumentsEndpoint(self.client)
        self.user_preferences = UserPreferencesEndpoint(self.client)


__all__ = [
    'SchwabAPI',
    'SchwabAPIClient',
    'AccountsEndpoint',
    'OrdersEndpoint',
    'TransactionsEndpoint',
    'QuotesEndpoint',
    'PriceHistoryEndpoint',
    'OptionsChainEndpoint',
    'MoversEndpoint',
    'MarketHoursEndpoint',
    'InstrumentsEndpoint',
    'UserPreferencesEndpoint',
]
