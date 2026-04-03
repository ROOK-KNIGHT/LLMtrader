"""
Economic Indicator Tools - Macroeconomic data via Alpha Vantage
"""

import sys
import os
import csv
import io
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from alphavantage import AlphaVantageClient


class EconomicTools:
    """
    Tools for accessing macroeconomic indicators via Alpha Vantage.
    Covers GDP, inflation, interest rates, employment, and more.
    """

    def __init__(self, av_client: AlphaVantageClient = None):
        """
        Initialize economic tools.

        Args:
            av_client: AlphaVantageClient instance (will create if not provided)
        """
        self.av = av_client or AlphaVantageClient()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'get_real_gdp',
                'description': (
                    'Get Real Gross Domestic Product (GDP) data. '
                    'Shows the inflation-adjusted value of all goods and services produced. '
                    'Use to assess overall economic growth and recession risk.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'interval': {
                            'type': 'string',
                            'description': 'Data frequency: quarterly (default) or annual'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_real_gdp_per_capita',
                'description': (
                    'Get Real GDP per capita data (quarterly). '
                    'Measures economic output per person — useful for comparing living standards over time.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_treasury_yield',
                'description': (
                    'Get US Treasury yield rates. '
                    'Critical for bond pricing, discount rates, and yield curve analysis. '
                    'The 10-year yield is the benchmark for mortgage rates and equity valuations.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'interval': {
                            'type': 'string',
                            'description': 'Data frequency: daily (default), weekly, or monthly'
                        },
                        'maturity': {
                            'type': 'string',
                            'description': 'Maturity: 3month, 2year, 5year, 7year, 10year (default), or 30year'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_federal_funds_rate',
                'description': (
                    'Get the Federal Funds Rate (Fed interest rate). '
                    'The primary monetary policy tool — directly impacts borrowing costs, '
                    'equity valuations, and currency strength.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'interval': {
                            'type': 'string',
                            'description': 'Data frequency: daily, weekly, or monthly (default)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_cpi',
                'description': (
                    'Get Consumer Price Index (CPI) data. '
                    'Measures inflation from the consumer perspective. '
                    'Key input for Fed policy decisions and real return calculations.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'interval': {
                            'type': 'string',
                            'description': 'Data frequency: monthly (default) or semiannual'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_inflation',
                'description': (
                    'Get annual inflation rate data. '
                    'Shows year-over-year price change percentage. '
                    'Use to assess purchasing power erosion and real returns.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_retail_sales',
                'description': (
                    'Get monthly retail sales data. '
                    'Leading indicator of consumer spending and economic health. '
                    'Strong retail sales signal economic expansion.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_durable_goods',
                'description': (
                    'Get monthly durable goods orders data. '
                    'Measures new orders for manufactured goods expected to last 3+ years. '
                    'Leading indicator of manufacturing activity and business investment.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_unemployment',
                'description': (
                    'Get monthly unemployment rate data. '
                    'Key labor market indicator watched by the Fed. '
                    'Low unemployment supports consumer spending; high unemployment signals recession.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_nonfarm_payroll',
                'description': (
                    'Get monthly non-farm payroll (NFP) data. '
                    'The most closely watched jobs report — measures new jobs added outside agriculture. '
                    'Major market-moving event released first Friday of each month.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        ]

    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        dispatch = {
            'get_real_gdp': self._get_real_gdp,
            'get_real_gdp_per_capita': self._get_real_gdp_per_capita,
            'get_treasury_yield': self._get_treasury_yield,
            'get_federal_funds_rate': self._get_federal_funds_rate,
            'get_cpi': self._get_cpi,
            'get_inflation': self._get_inflation,
            'get_retail_sales': self._get_retail_sales,
            'get_durable_goods': self._get_durable_goods,
            'get_unemployment': self._get_unemployment,
            'get_nonfarm_payroll': self._get_nonfarm_payroll,
        }
        if tool_name not in dispatch:
            return f"Error: Unknown tool '{tool_name}'"
        return dispatch[tool_name](**args)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _format_series(data: Dict[str, Any], title: str, unit: str = "", limit: int = 12) -> str:
        """Format a time-series response from Alpha Vantage economic endpoints."""
        name = data.get("name", title)
        interval = data.get("interval", "")
        unit_str = data.get("unit", unit)
        series = data.get("data", [])

        header = f"{name}"
        if interval:
            header += f" ({interval})"
        output = header + "\n" + "=" * len(header) + "\n"
        if unit_str:
            output += f"Unit: {unit_str}\n"
        output += "\n"

        for entry in series[:limit]:
            date = entry.get("date", "N/A")
            value = entry.get("value", "N/A")
            output += f"  {date}: {value}\n"

        if len(series) > limit:
            output += f"\n  ... ({len(series) - limit} more data points available)\n"

        return output.strip()

    # ─────────────────────────────────────────────────────────────────────────
    # IMPLEMENTATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def _get_real_gdp(self, interval: str = "quarterly") -> str:
        try:
            data = self.av.get_real_gdp(interval=interval)
            return self._format_series(data, "Real GDP", limit=12)
        except Exception as e:
            return f"Error fetching Real GDP: {str(e)}"

    def _get_real_gdp_per_capita(self) -> str:
        try:
            data = self.av.get_real_gdp_per_capita()
            return self._format_series(data, "Real GDP Per Capita", limit=12)
        except Exception as e:
            return f"Error fetching Real GDP Per Capita: {str(e)}"

    def _get_treasury_yield(self, interval: str = "daily", maturity: str = "10year") -> str:
        try:
            data = self.av.get_treasury_yield(interval=interval, maturity=maturity)
            title = f"Treasury Yield ({maturity})"
            return self._format_series(data, title, unit="%", limit=20)
        except Exception as e:
            return f"Error fetching Treasury Yield: {str(e)}"

    def _get_federal_funds_rate(self, interval: str = "monthly") -> str:
        try:
            data = self.av.get_federal_funds_rate(interval=interval)
            return self._format_series(data, "Federal Funds Rate", unit="%", limit=24)
        except Exception as e:
            return f"Error fetching Federal Funds Rate: {str(e)}"

    def _get_cpi(self, interval: str = "monthly") -> str:
        try:
            data = self.av.get_cpi(interval=interval)
            return self._format_series(data, "Consumer Price Index (CPI)", limit=24)
        except Exception as e:
            return f"Error fetching CPI: {str(e)}"

    def _get_inflation(self) -> str:
        try:
            data = self.av.get_inflation()
            return self._format_series(data, "Annual Inflation Rate", unit="%", limit=20)
        except Exception as e:
            return f"Error fetching Inflation: {str(e)}"

    def _get_retail_sales(self) -> str:
        try:
            data = self.av.get_retail_sales()
            return self._format_series(data, "Retail Sales", limit=24)
        except Exception as e:
            return f"Error fetching Retail Sales: {str(e)}"

    def _get_durable_goods(self) -> str:
        try:
            data = self.av.get_durables()
            return self._format_series(data, "Durable Goods Orders", limit=24)
        except Exception as e:
            return f"Error fetching Durable Goods: {str(e)}"

    def _get_unemployment(self) -> str:
        try:
            data = self.av.get_unemployment()
            return self._format_series(data, "Unemployment Rate", unit="%", limit=24)
        except Exception as e:
            return f"Error fetching Unemployment: {str(e)}"

    def _get_nonfarm_payroll(self) -> str:
        try:
            data = self.av.get_nonfarm_payroll()
            return self._format_series(data, "Non-Farm Payroll", limit=24)
        except Exception as e:
            return f"Error fetching Non-Farm Payroll: {str(e)}"
