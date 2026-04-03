"""
Alpha Vantage API Client
Direct HTTP client for economic indicators and fundamental data
API Key: configured via ALPHA_VANTAGE_API_KEY environment variable
"""

import os
import requests
from typing import Dict, Any, Optional


class AlphaVantageClient:
    """
    Lightweight HTTP client for the Alpha Vantage REST API.
    Handles economic indicators and fundamental data endpoints.
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str = None):
        """
        Initialize the Alpha Vantage client.

        Args:
            api_key: Alpha Vantage API key. Falls back to ALPHA_VANTAGE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key not found. "
                "Set ALPHA_VANTAGE_API_KEY environment variable."
            )

    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a GET request to the Alpha Vantage API.

        Args:
            params: Query parameters (function, symbol, etc.)

        Returns:
            Parsed JSON response

        Raises:
            RuntimeError: On HTTP errors or API error messages
        """
        params["apikey"] = self.api_key
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Alpha Vantage returns errors as JSON fields
            if "Error Message" in data:
                raise RuntimeError(f"Alpha Vantage API error: {data['Error Message']}")
            if "Note" in data:
                raise RuntimeError(
                    f"Alpha Vantage rate limit reached: {data['Note']}"
                )
            if "Information" in data:
                raise RuntimeError(
                    f"Alpha Vantage API info: {data['Information']}"
                )

            return data

        except requests.exceptions.Timeout:
            raise RuntimeError("Alpha Vantage API request timed out (15s)")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Alpha Vantage HTTP error: {str(e)}")

    # ─────────────────────────────────────────────────────────────────────────
    # ECONOMIC INDICATORS
    # ─────────────────────────────────────────────────────────────────────────

    def get_real_gdp(self, interval: str = "quarterly") -> Dict[str, Any]:
        """Real Gross Domestic Product. interval: annual | quarterly"""
        return self._get({"function": "REAL_GDP", "interval": interval})

    def get_real_gdp_per_capita(self) -> Dict[str, Any]:
        """Real GDP per capita (quarterly)"""
        return self._get({"function": "REAL_GDP_PER_CAPITA"})

    def get_treasury_yield(self, interval: str = "daily", maturity: str = "10year") -> Dict[str, Any]:
        """
        Daily/weekly/monthly treasury yield rates.
        interval: daily | weekly | monthly
        maturity: 3month | 2year | 5year | 7year | 10year | 30year
        """
        return self._get({
            "function": "TREASURY_YIELD",
            "interval": interval,
            "maturity": maturity
        })

    def get_federal_funds_rate(self, interval: str = "monthly") -> Dict[str, Any]:
        """Federal funds (interest) rate. interval: daily | weekly | monthly"""
        return self._get({"function": "FEDERAL_FUNDS_RATE", "interval": interval})

    def get_cpi(self, interval: str = "monthly") -> Dict[str, Any]:
        """Consumer Price Index. interval: monthly | semiannual"""
        return self._get({"function": "CPI", "interval": interval})

    def get_inflation(self) -> Dict[str, Any]:
        """Annual inflation rates"""
        return self._get({"function": "INFLATION"})

    def get_retail_sales(self) -> Dict[str, Any]:
        """Monthly retail sales data"""
        return self._get({"function": "RETAIL_SALES"})

    def get_durables(self) -> Dict[str, Any]:
        """Monthly durable goods orders"""
        return self._get({"function": "DURABLES"})

    def get_unemployment(self) -> Dict[str, Any]:
        """Monthly unemployment rate"""
        return self._get({"function": "UNEMPLOYMENT"})

    def get_nonfarm_payroll(self) -> Dict[str, Any]:
        """Monthly non-farm payroll data"""
        return self._get({"function": "NONFARM_PAYROLL"})

    # ─────────────────────────────────────────────────────────────────────────
    # FUNDAMENTAL DATA
    # ─────────────────────────────────────────────────────────────────────────

    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Company information, financial ratios, and key metrics"""
        return self._get({"function": "OVERVIEW", "symbol": symbol.upper()})

    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Annual and quarterly income statements"""
        return self._get({"function": "INCOME_STATEMENT", "symbol": symbol.upper()})

    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """Annual and quarterly balance sheets"""
        return self._get({"function": "BALANCE_SHEET", "symbol": symbol.upper()})

    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """Annual and quarterly cash flow statements"""
        return self._get({"function": "CASH_FLOW", "symbol": symbol.upper()})

    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """Annual and quarterly earnings (EPS) data"""
        return self._get({"function": "EARNINGS", "symbol": symbol.upper()})

    def get_listing_status(
        self,
        date: Optional[str] = None,
        state: str = "active"
    ) -> str:
        """
        Listing and delisting data for equities (returns CSV).
        state: active | delisted
        date: YYYY-MM-DD (optional, defaults to latest)
        """
        params: Dict[str, Any] = {
            "function": "LISTING_STATUS",
            "state": state,
            "apikey": self.api_key
        }
        if date:
            params["date"] = date

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.text  # Returns CSV
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Alpha Vantage HTTP error: {str(e)}")

    def get_earnings_calendar(
        self,
        symbol: Optional[str] = None,
        horizon: str = "3month"
    ) -> str:
        """
        Upcoming earnings calendar (returns CSV).
        horizon: 3month | 6month | 12month
        symbol: optional filter by ticker
        """
        params: Dict[str, Any] = {
            "function": "EARNINGS_CALENDAR",
            "horizon": horizon,
            "apikey": self.api_key
        }
        if symbol:
            params["symbol"] = symbol.upper()

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.text  # Returns CSV
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Alpha Vantage HTTP error: {str(e)}")

    def get_ipo_calendar(self) -> str:
        """
        Upcoming IPO calendar (returns CSV).
        """
        params: Dict[str, Any] = {
            "function": "IPO_CALENDAR",
            "apikey": self.api_key
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.text  # Returns CSV
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Alpha Vantage HTTP error: {str(e)}")
