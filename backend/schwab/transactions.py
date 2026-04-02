"""
Schwab Transactions API Endpoints
Wrapper for transaction history endpoints.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .client import SchwabAPIClient


def _normalize_schwab_date(date_str: Optional[str], end_of_day: bool = False) -> Optional[str]:
    """
    Normalize a date string to Schwab's required ISO 8601 format: YYYY-MM-DDTHH:MM:SS.000Z

    Accepts: 'YYYY-MM-DD', 'YYYY-MM-DDTHH:MM:SS', 'YYYY-MM-DDTHH:MM:SS.sssZ'
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    if date_str.endswith('Z') and 'T' in date_str and '.' in date_str:
        return date_str

    try:
        if 'T' in date_str:
            clean = date_str.rstrip('Z').split('+')[0]
            if '.' in clean:
                clean = clean.split('.')[0]
            dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
        else:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)

        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    except ValueError:
        return date_str


class TransactionsEndpoint:
    """
    Schwab Transactions API endpoints.
    
    Endpoints:
    - GET /accounts/{accountHash}/transactions - Get all transactions
    - GET /accounts/{accountHash}/transactions/{transactionId} - Get specific transaction
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize transactions endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_transactions(
        self,
        account_hash: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        types: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history for an account.
        
        Args:
            account_hash: Account hash value
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            types: Transaction types (comma-separated): TRADE, RECEIVE_AND_DELIVER, 
                   DIVIDEND_OR_INTEREST, ACH_RECEIPT, ACH_DISBURSEMENT, CASH_RECEIPT, 
                   CASH_DISBURSEMENT, ELECTRONIC_FUND, WIRE_OUT, WIRE_IN, JOURNAL, 
                   MEMORANDUM, MARGIN_CALL, MONEY_MARKET, SMA_ADJUSTMENT
            symbol: Filter by symbol
        
        Returns:
            List of transaction objects
        
        Example:
            transactions = endpoint.get_transactions(
                'ABC123',
                start_date='2024-01-01',
                end_date='2024-12-31',
                types='TRADE'
            )
        """
        params = {}
        if start_date:
            params['startDate'] = _normalize_schwab_date(start_date)
        if end_date:
            params['endDate'] = _normalize_schwab_date(end_date, end_of_day=True)
        if types:
            params['types'] = types
        if symbol:
            params['symbol'] = symbol

        return self.client.get(f'/accounts/{account_hash}/transactions', params=params)
    
    def get_transaction(
        self,
        account_hash: str,
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        Get specific transaction details.
        
        Args:
            account_hash: Account hash value
            transaction_id: Transaction ID
        
        Returns:
            Transaction object
        
        Example:
            transaction = endpoint.get_transaction('ABC123', '12345')
        """
        return self.client.get(f'/accounts/{account_hash}/transactions/{transaction_id}')
    
    def get_trade_transactions(
        self,
        account_hash: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get only trade transactions (convenience method).
        
        Args:
            account_hash: Account hash value
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            symbol: Filter by symbol
        
        Returns:
            List of trade transaction objects
        
        Example:
            trades = endpoint.get_trade_transactions('ABC123', symbol='AAPL')
        """
        return self.get_transactions(
            account_hash=account_hash,
            start_date=start_date,
            end_date=end_date,
            types='TRADE',
            symbol=symbol
        )
