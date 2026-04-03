"""
Fundamental Data Tools - Company financials and market data via Alpha Vantage
"""

import sys
import os
import csv
import io
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from alphavantage import AlphaVantageClient


class FundamentalTools:
    """
    Tools for accessing company fundamental data via Alpha Vantage.
    Covers financial statements, earnings, and market calendars.
    """

    def __init__(self, av_client: AlphaVantageClient = None):
        """
        Initialize fundamental tools.

        Args:
            av_client: AlphaVantageClient instance (will create if not provided)
        """
        self.av = av_client or AlphaVantageClient()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for LLM"""
        return [
            {
                'name': 'get_company_overview',
                'description': (
                    'Get comprehensive company overview including financial ratios and key metrics. '
                    'Returns P/E ratio, EPS, market cap, dividend yield, 52-week range, beta, '
                    'profit margins, revenue, sector, industry, and analyst targets. '
                    'Use for fundamental analysis and stock screening.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock ticker symbol (e.g., AAPL, MSFT, TSLA)'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_income_statement',
                'description': (
                    'Get annual and quarterly income statements for a company. '
                    'Shows revenue, gross profit, operating income, net income, EPS, and EBITDA. '
                    'Use to analyze revenue growth, profit margins, and earnings trends.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock ticker symbol (e.g., AAPL, MSFT)'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_balance_sheet',
                'description': (
                    'Get annual and quarterly balance sheets for a company. '
                    'Shows total assets, liabilities, equity, cash, debt, and working capital. '
                    'Use to assess financial health, leverage, and liquidity.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock ticker symbol (e.g., AAPL, MSFT)'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_cash_flow',
                'description': (
                    'Get annual and quarterly cash flow statements for a company. '
                    'Shows operating cash flow, capital expenditures, free cash flow, '
                    'and financing activities. Use to assess cash generation quality.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock ticker symbol (e.g., AAPL, MSFT)'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_earnings',
                'description': (
                    'Get annual and quarterly earnings (EPS) data for a company. '
                    'Shows reported EPS, estimated EPS, and surprise percentage. '
                    'Use to track earnings beats/misses and growth trajectory.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Stock ticker symbol (e.g., AAPL, MSFT)'
                        }
                    },
                    'required': ['symbol']
                }
            },
            {
                'name': 'get_listing_status',
                'description': (
                    'Get listing and delisting data for equities. '
                    'Shows active or delisted stocks with exchange and IPO date. '
                    'Use to verify if a symbol is actively traded.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'state': {
                            'type': 'string',
                            'description': 'Filter by status: active (default) or delisted'
                        },
                        'date': {
                            'type': 'string',
                            'description': 'As-of date in YYYY-MM-DD format (optional, defaults to latest)'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_earnings_calendar',
                'description': (
                    'Get upcoming earnings release calendar. '
                    'Shows scheduled earnings dates, estimated EPS, and fiscal quarter. '
                    'Use to plan around earnings events and avoid surprise risk.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'symbol': {
                            'type': 'string',
                            'description': 'Filter by ticker symbol (optional — omit for all upcoming earnings)'
                        },
                        'horizon': {
                            'type': 'string',
                            'description': 'Lookahead window: 3month (default), 6month, or 12month'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'get_ipo_calendar',
                'description': (
                    'Get upcoming IPO (Initial Public Offering) calendar. '
                    'Shows company name, symbol, exchange, IPO date, price range, and shares offered. '
                    'Use to identify new listing opportunities.'
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
            'get_company_overview': self._get_company_overview,
            'get_income_statement': self._get_income_statement,
            'get_balance_sheet': self._get_balance_sheet,
            'get_cash_flow': self._get_cash_flow,
            'get_earnings': self._get_earnings,
            'get_listing_status': self._get_listing_status,
            'get_earnings_calendar': self._get_earnings_calendar,
            'get_ipo_calendar': self._get_ipo_calendar,
        }
        if tool_name not in dispatch:
            return f"Error: Unknown tool '{tool_name}'"
        return dispatch[tool_name](**args)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt(value: Any, prefix: str = "", suffix: str = "") -> str:
        """Format a value, returning 'N/A' for None/empty."""
        if value is None or value == "" or value == "None":
            return "N/A"
        return f"{prefix}{value}{suffix}"

    @staticmethod
    def _fmt_large(value: Any) -> str:
        """Format large numbers with B/M/K suffixes."""
        try:
            v = float(value)
            if abs(v) >= 1e12:
                return f"${v/1e12:.2f}T"
            elif abs(v) >= 1e9:
                return f"${v/1e9:.2f}B"
            elif abs(v) >= 1e6:
                return f"${v/1e6:.2f}M"
            elif abs(v) >= 1e3:
                return f"${v/1e3:.2f}K"
            else:
                return f"${v:.2f}"
        except (TypeError, ValueError):
            return str(value) if value else "N/A"

    @staticmethod
    def _parse_csv(csv_text: str, limit: int = 20) -> List[Dict[str, str]]:
        """Parse CSV text into list of dicts."""
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = []
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(dict(row))
        return rows

    @staticmethod
    def _format_statement_report(reports: List[Dict], title: str, key_fields: List[str], limit: int = 4) -> str:
        """Format financial statement reports (income, balance, cash flow)."""
        output = title + "\n" + "=" * len(title) + "\n\n"
        for report in reports[:limit]:
            date = report.get("fiscalDateEnding", "N/A")
            output += f"Period: {date}\n"
            output += "-" * 40 + "\n"
            for field, label in key_fields:
                raw = report.get(field, "N/A")
                output += f"  {label}: {FundamentalTools._fmt_large(raw) if raw != 'N/A' else 'N/A'}\n"
            output += "\n"
        return output.strip()

    # ─────────────────────────────────────────────────────────────────────────
    # IMPLEMENTATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def _get_company_overview(self, symbol: str) -> str:
        try:
            d = self.av.get_company_overview(symbol)
            if not d or "Symbol" not in d:
                return f"No company overview data found for {symbol.upper()}"

            output = f"COMPANY OVERVIEW: {d.get('Symbol', symbol.upper())}\n"
            output += "=" * 60 + "\n\n"

            output += f"Name:            {self._fmt(d.get('Name'))}\n"
            output += f"Sector:          {self._fmt(d.get('Sector'))}\n"
            output += f"Industry:        {self._fmt(d.get('Industry'))}\n"
            output += f"Exchange:        {self._fmt(d.get('Exchange'))}\n"
            output += f"Country:         {self._fmt(d.get('Country'))}\n"
            output += f"Currency:        {self._fmt(d.get('Currency'))}\n\n"

            output += "VALUATION\n"
            output += f"  Market Cap:    {self._fmt_large(d.get('MarketCapitalization'))}\n"
            output += f"  P/E Ratio:     {self._fmt(d.get('PERatio'))}\n"
            output += f"  Forward P/E:   {self._fmt(d.get('ForwardPE'))}\n"
            output += f"  PEG Ratio:     {self._fmt(d.get('PEGRatio'))}\n"
            output += f"  P/B Ratio:     {self._fmt(d.get('PriceToBookRatio'))}\n"
            output += f"  P/S Ratio:     {self._fmt(d.get('PriceToSalesRatioTTM'))}\n"
            output += f"  EV/EBITDA:     {self._fmt(d.get('EVToEBITDA'))}\n\n"

            output += "EARNINGS & DIVIDENDS\n"
            output += f"  EPS (TTM):     {self._fmt(d.get('EPS'), prefix='$')}\n"
            output += f"  EPS (Diluted): {self._fmt(d.get('DilutedEPSTTM'), prefix='$')}\n"
            output += f"  Div/Share:     {self._fmt(d.get('DividendPerShare'), prefix='$')}\n"
            output += f"  Div Yield:     {self._fmt(d.get('DividendYield'), suffix='%')}\n"
            output += f"  Payout Ratio:  {self._fmt(d.get('PayoutRatio'))}\n\n"

            output += "FINANCIALS (TTM)\n"
            output += f"  Revenue:       {self._fmt_large(d.get('RevenueTTM'))}\n"
            output += f"  Gross Profit:  {self._fmt_large(d.get('GrossProfitTTM'))}\n"
            output += f"  EBITDA:        {self._fmt_large(d.get('EBITDA'))}\n"
            output += f"  Profit Margin: {self._fmt(d.get('ProfitMargin'))}\n"
            output += f"  Op. Margin:    {self._fmt(d.get('OperatingMarginTTM'))}\n"
            output += f"  ROE:           {self._fmt(d.get('ReturnOnEquityTTM'))}\n"
            output += f"  ROA:           {self._fmt(d.get('ReturnOnAssetsTTM'))}\n\n"

            output += "PRICE DATA\n"
            output += f"  52W High:      {self._fmt(d.get('52WeekHigh'), prefix='$')}\n"
            output += f"  52W Low:       {self._fmt(d.get('52WeekLow'), prefix='$')}\n"
            output += f"  50D MA:        {self._fmt(d.get('50DayMovingAverage'), prefix='$')}\n"
            output += f"  200D MA:       {self._fmt(d.get('200DayMovingAverage'), prefix='$')}\n"
            output += f"  Beta:          {self._fmt(d.get('Beta'))}\n"
            output += f"  Analyst Target:{self._fmt(d.get('AnalystTargetPrice'), prefix='$')}\n"

            return output.strip()
        except Exception as e:
            return f"Error fetching company overview for {symbol}: {str(e)}"

    def _get_income_statement(self, symbol: str) -> str:
        try:
            data = self.av.get_income_statement(symbol)
            annual = data.get("annualReports", [])
            quarterly = data.get("quarterlyReports", [])

            key_fields = [
                ("totalRevenue", "Total Revenue"),
                ("grossProfit", "Gross Profit"),
                ("operatingIncome", "Operating Income"),
                ("ebitda", "EBITDA"),
                ("netIncome", "Net Income"),
                ("reportedEPS", "EPS (Reported)"),
            ]

            output = f"INCOME STATEMENT: {symbol.upper()}\n"
            output += "=" * 50 + "\n\n"
            output += "ANNUAL (last 4 years)\n"
            output += self._format_statement_report(annual, "", key_fields, limit=4) + "\n\n"
            output += "QUARTERLY (last 4 quarters)\n"
            output += self._format_statement_report(quarterly, "", key_fields, limit=4)
            return output.strip()
        except Exception as e:
            return f"Error fetching income statement for {symbol}: {str(e)}"

    def _get_balance_sheet(self, symbol: str) -> str:
        try:
            data = self.av.get_balance_sheet(symbol)
            annual = data.get("annualReports", [])
            quarterly = data.get("quarterlyReports", [])

            key_fields = [
                ("totalAssets", "Total Assets"),
                ("totalCurrentAssets", "Current Assets"),
                ("cashAndCashEquivalentsAtCarryingValue", "Cash & Equivalents"),
                ("totalLiabilities", "Total Liabilities"),
                ("totalCurrentLiabilities", "Current Liabilities"),
                ("longTermDebt", "Long-Term Debt"),
                ("totalShareholderEquity", "Shareholder Equity"),
            ]

            output = f"BALANCE SHEET: {symbol.upper()}\n"
            output += "=" * 50 + "\n\n"
            output += "ANNUAL (last 4 years)\n"
            output += self._format_statement_report(annual, "", key_fields, limit=4) + "\n\n"
            output += "QUARTERLY (last 4 quarters)\n"
            output += self._format_statement_report(quarterly, "", key_fields, limit=4)
            return output.strip()
        except Exception as e:
            return f"Error fetching balance sheet for {symbol}: {str(e)}"

    def _get_cash_flow(self, symbol: str) -> str:
        try:
            data = self.av.get_cash_flow(symbol)
            annual = data.get("annualReports", [])
            quarterly = data.get("quarterlyReports", [])

            key_fields = [
                ("operatingCashflow", "Operating Cash Flow"),
                ("capitalExpenditures", "Capital Expenditures"),
                ("cashflowFromInvestment", "Cash from Investing"),
                ("cashflowFromFinancing", "Cash from Financing"),
                ("dividendPayout", "Dividend Payout"),
                ("netIncome", "Net Income"),
            ]

            output = f"CASH FLOW STATEMENT: {symbol.upper()}\n"
            output += "=" * 50 + "\n\n"
            output += "ANNUAL (last 4 years)\n"
            output += self._format_statement_report(annual, "", key_fields, limit=4) + "\n\n"
            output += "QUARTERLY (last 4 quarters)\n"
            output += self._format_statement_report(quarterly, "", key_fields, limit=4)
            return output.strip()
        except Exception as e:
            return f"Error fetching cash flow for {symbol}: {str(e)}"

    def _get_earnings(self, symbol: str) -> str:
        try:
            data = self.av.get_earnings(symbol)
            annual = data.get("annualEarnings", [])
            quarterly = data.get("quarterlyEarnings", [])

            output = f"EARNINGS: {symbol.upper()}\n"
            output += "=" * 50 + "\n\n"

            output += "ANNUAL EPS (last 5 years)\n"
            output += "-" * 40 + "\n"
            for r in annual[:5]:
                date = r.get("fiscalDateEnding", "N/A")
                eps = r.get("reportedEPS", "N/A")
                output += f"  {date}: EPS ${eps}\n"

            output += "\nQUARTERLY EPS (last 8 quarters)\n"
            output += "-" * 40 + "\n"
            for r in quarterly[:8]:
                date = r.get("fiscalDateEnding", "N/A")
                reported = r.get("reportedEPS", "N/A")
                estimated = r.get("estimatedEPS", "N/A")
                surprise = r.get("surprisePercentage", "N/A")
                output += f"  {date}: Reported ${reported} | Est ${estimated} | Surprise {surprise}%\n"

            return output.strip()
        except Exception as e:
            return f"Error fetching earnings for {symbol}: {str(e)}"

    def _get_listing_status(self, state: str = "active", date: Optional[str] = None) -> str:
        try:
            csv_text = self.av.get_listing_status(date=date, state=state)
            rows = self._parse_csv(csv_text, limit=30)
            if not rows:
                return f"No listing status data found (state={state})"

            output = f"LISTING STATUS ({state.upper()})\n"
            output += "=" * 50 + "\n\n"
            for row in rows:
                sym = row.get("symbol", "N/A")
                name = row.get("name", "N/A")
                exchange = row.get("exchange", "N/A")
                ipo_date = row.get("ipoDate", "N/A")
                output += f"  {sym} | {name} | {exchange} | IPO: {ipo_date}\n"

            return output.strip()
        except Exception as e:
            return f"Error fetching listing status: {str(e)}"

    def _get_earnings_calendar(self, symbol: Optional[str] = None, horizon: str = "3month") -> str:
        try:
            csv_text = self.av.get_earnings_calendar(symbol=symbol, horizon=horizon)
            rows = self._parse_csv(csv_text, limit=30)
            if not rows:
                return "No upcoming earnings found"

            title = "EARNINGS CALENDAR"
            if symbol:
                title += f": {symbol.upper()}"
            title += f" ({horizon})"
            output = title + "\n" + "=" * len(title) + "\n\n"

            for row in rows:
                sym = row.get("symbol", "N/A")
                name = row.get("name", "N/A")
                report_date = row.get("reportDate", "N/A")
                fiscal_end = row.get("fiscalDateEnding", "N/A")
                estimate = row.get("estimate", "N/A")
                currency = row.get("currency", "USD")
                output += f"  {report_date} | {sym} | {name}\n"
                output += f"    Fiscal End: {fiscal_end} | EPS Est: {estimate} {currency}\n\n"

            return output.strip()
        except Exception as e:
            return f"Error fetching earnings calendar: {str(e)}"

    def _get_ipo_calendar(self) -> str:
        try:
            csv_text = self.av.get_ipo_calendar()
            rows = self._parse_csv(csv_text, limit=30)
            if not rows:
                return "No upcoming IPOs found"

            output = "IPO CALENDAR\n"
            output += "=" * 50 + "\n\n"

            for row in rows:
                sym = row.get("symbol", "N/A")
                name = row.get("name", "N/A")
                ipo_date = row.get("ipoDate", "N/A")
                price_range = row.get("priceRangeLow", "N/A")
                price_high = row.get("priceRangeHigh", "")
                exchange = row.get("exchange", "N/A")
                shares = row.get("shares", "N/A")
                status = row.get("status", "N/A")

                price_str = f"${price_range}"
                if price_high:
                    price_str += f" - ${price_high}"

                output += f"  {ipo_date} | {sym} | {name}\n"
                output += f"    Exchange: {exchange} | Price: {price_str} | Shares: {shares} | Status: {status}\n\n"

            return output.strip()
        except Exception as e:
            return f"Error fetching IPO calendar: {str(e)}"
