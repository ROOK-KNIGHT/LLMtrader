"""
Schwab Accounts API Endpoints
Wrapper for account and position endpoints.
"""

from typing import Dict, Any, List, Optional
from .client import SchwabAPIClient


class AccountsEndpoint:
    """
    Schwab Accounts API endpoints.
    
    Endpoints:
    - GET /accounts - Get all linked accounts
    - GET /accounts/accountNumbers - Get account numbers
    - GET /accounts/{accountHash} - Get specific account details
    """
    
    def __init__(self, client: SchwabAPIClient):
        """
        Initialize accounts endpoint.
        
        Args:
            client: SchwabAPIClient instance
        """
        self.client = client
    
    def get_all_accounts(self, fields: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all linked accounts.
        
        Args:
            fields: Optional fields to include (e.g., 'positions')
        
        Returns:
            List of account objects
        
        Example:
            accounts = endpoint.get_all_accounts(fields='positions')
        """
        params = {}
        if fields:
            params['fields'] = fields
        
        return self.client.get('/accounts', params=params)
    
    def get_account(
        self,
        account_hash: str,
        fields: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get specific account details.
        
        Args:
            account_hash: Account hash value
            fields: Optional fields to include (e.g., 'positions')
        
        Returns:
            Account object with details
        
        Example:
            account = endpoint.get_account('ABC123', fields='positions')
        """
        params = {}
        if fields:
            params['fields'] = fields
        
        return self.client.get(f'/accounts/{account_hash}', params=params)
    
    def get_account_numbers(self) -> List[Dict[str, str]]:
        """
        Get account numbers for all linked accounts.
        
        Returns:
            List of account number objects with hashValue and accountNumber
        
        Example:
            numbers = endpoint.get_account_numbers()
            # [{'hashValue': 'ABC123', 'accountNumber': '12345678'}]
        """
        return self.client.get('/accounts/accountNumbers')
    
    def get_positions(self, account_hash: str) -> Dict[str, Any]:
        """
        Get current positions for an account.
        Convenience method that calls get_account with fields='positions'.
        
        Args:
            account_hash: Account hash value
        
        Returns:
            Account object with positions
        
        Example:
            positions = endpoint.get_positions('ABC123')
        """
        return self.get_account(account_hash, fields='positions')
    
    def get_balances(self, account_hash: str) -> Dict[str, Any]:
        """
        Get account balances and buying power.
        
        Args:
            account_hash: Account hash value
        
        Returns:
            Account object with balance details
        
        Example:
            balances = endpoint.get_balances('ABC123')
        """
        account = self.get_account(account_hash)
        
        # Extract relevant balance info
        if 'securitiesAccount' in account:
            sec_account = account['securitiesAccount']
            return {
                'accountType': sec_account.get('type'),
                'currentBalances': sec_account.get('currentBalances', {}),
                'initialBalances': sec_account.get('initialBalances', {}),
                'projectedBalances': sec_account.get('projectedBalances', {})
            }
        
        return account
