"""
Schwab Streamer Field Definitions
Maps numeric field IDs to readable field names for all streaming services.
"""

# LEVELONE_EQUITIES Field Definitions
LEVELONE_EQUITIES_FIELDS = {
    0: 'symbol',
    1: 'bidPrice',
    2: 'askPrice',
    3: 'lastPrice',
    4: 'bidSize',
    5: 'askSize',
    6: 'askId',
    7: 'bidId',
    8: 'totalVolume',
    9: 'lastSize',
    10: 'highPrice',
    11: 'lowPrice',
    12: 'closePrice',
    13: 'exchangeId',
    14: 'marginable',
    15: 'description',
    16: 'lastId',
    17: 'openPrice',
    18: 'netChange',
    19: '52WeekHigh',
    20: '52WeekLow',
    21: 'peRatio',
    22: 'annualDividendAmount',
    23: 'dividendYield',
    24: 'nav',
    25: 'exchangeName',
    26: 'dividendDate',
    27: 'regularMarketQuote',
    28: 'regularMarketTrade',
    29: 'regularMarketLastPrice',
    30: 'regularMarketLastSize',
    31: 'regularMarketNetChange',
    32: 'securityStatus',
    33: 'markPrice',
    34: 'quoteTimeInLong',
    35: 'tradeTimeInLong',
    36: 'regularMarketTradeTimeInLong',
    37: 'bidTime',
    38: 'askTime',
    39: 'askMICId',
    40: 'bidMICId',
    41: 'lastMICId',
    42: 'netPercentChange',
    43: 'regularMarketPercentChange',
    44: 'markPriceNetChange',
    45: 'markPricePercentChange',
    46: 'hardToBorrowQuantity',
    47: 'hardToBorrowRate',
    48: 'hardToBorrow',
    49: 'shortable',
    50: 'postMarketNetChange',
    51: 'postMarketPercentChange',
}

# LEVELONE_OPTIONS Field Definitions
LEVELONE_OPTIONS_FIELDS = {
    0: 'symbol',
    1: 'description',
    2: 'bidPrice',
    3: 'askPrice',
    4: 'lastPrice',
    5: 'highPrice',
    6: 'lowPrice',
    7: 'closePrice',
    8: 'totalVolume',
    9: 'openInterest',
    10: 'volatility',
    11: 'moneyIntrinsicValue',
    12: 'expirationYear',
    13: 'multiplier',
    14: 'digits',
    15: 'openPrice',
    16: 'bidSize',
    17: 'askSize',
    18: 'lastSize',
    19: 'netChange',
    20: 'strikePrice',
    21: 'contractType',
    22: 'underlying',
    23: 'expirationMonth',
    24: 'deliverables',
    25: 'timeValue',
    26: 'expirationDay',
    27: 'daysToExpiration',
    28: 'delta',
    29: 'gamma',
    30: 'theta',
    31: 'vega',
    32: 'rho',
    33: 'securityStatus',
    34: 'theoreticalOptionValue',
    35: 'underlyingPrice',
    36: 'uvExpirationType',
    37: 'markPrice',
    38: 'quoteTimeInLong',
    39: 'tradeTimeInLong',
    40: 'exchange',
    41: 'exchangeName',
    42: 'lastTradingDay',
    43: 'settlementType',
    44: 'netPercentChange',
    45: 'markPriceNetChange',
    46: 'markPricePercentChange',
    47: 'impliedYield',
    48: 'isPennyPilot',
    49: 'optionRoot',
    50: '52WeekHigh',
    51: '52WeekLow',
    52: 'indicativeAskPrice',
    53: 'indicativeBidPrice',
    54: 'indicativeQuoteTime',
    55: 'exerciseType',
}

# LEVELONE_FUTURES Field Definitions
LEVELONE_FUTURES_FIELDS = {
    0: 'symbol',
    1: 'bidPrice',
    2: 'askPrice',
    3: 'lastPrice',
    4: 'bidSize',
    5: 'askSize',
    6: 'bidId',
    7: 'askId',
    8: 'totalVolume',
    9: 'lastSize',
    10: 'quoteTime',
    11: 'tradeTime',
    12: 'highPrice',
    13: 'lowPrice',
    14: 'closePrice',
    15: 'exchangeId',
    16: 'description',
    17: 'lastId',
    18: 'openPrice',
    19: 'netChange',
    20: 'futurePercentChange',
    21: 'exchangeName',
    22: 'securityStatus',
    23: 'openInterest',
    24: 'mark',
    25: 'tick',
    26: 'tickAmount',
    27: 'product',
    28: 'futurePriceFormat',
    29: 'futureTradingHours',
    30: 'futureIsTradable',
    31: 'futureMultiplier',
    32: 'futureIsActive',
    33: 'futureSettlementPrice',
    34: 'futureActiveSymbol',
    35: 'futureExpirationDate',
    36: 'expirationStyle',
    37: 'askTime',
    38: 'bidTime',
    39: 'quotedInSession',
    40: 'settlementDate',
}

# LEVELONE_FUTURES_OPTIONS Field Definitions
LEVELONE_FUTURES_OPTIONS_FIELDS = {
    0: 'symbol',
    1: 'bidPrice',
    2: 'askPrice',
    3: 'lastPrice',
    4: 'bidSize',
    5: 'askSize',
    6: 'bidId',
    7: 'askId',
    8: 'totalVolume',
    9: 'lastSize',
    10: 'quoteTime',
    11: 'tradeTime',
    12: 'highPrice',
    13: 'lowPrice',
    14: 'closePrice',
    15: 'lastId',
    16: 'description',
    17: 'openPrice',
    18: 'openInterest',
    19: 'mark',
    20: 'tick',
    21: 'tickAmount',
    22: 'futureMultiplier',
    23: 'futureSettlementPrice',
    24: 'underlyingSymbol',
    25: 'strikePrice',
    26: 'futureExpirationDate',
    27: 'expirationStyle',
    28: 'contractType',
    29: 'securityStatus',
    30: 'exchange',
    31: 'exchangeName',
}

# LEVELONE_FOREX Field Definitions
LEVELONE_FOREX_FIELDS = {
    0: 'symbol',
    1: 'bidPrice',
    2: 'askPrice',
    3: 'lastPrice',
    4: 'bidSize',
    5: 'askSize',
    6: 'totalVolume',
    7: 'lastSize',
    8: 'quoteTime',
    9: 'tradeTime',
    10: 'highPrice',
    11: 'lowPrice',
    12: 'closePrice',
    13: 'exchange',
    14: 'description',
    15: 'openPrice',
    16: 'netChange',
    17: 'percentChange',
    18: 'exchangeName',
    19: 'digits',
    20: 'securityStatus',
    21: 'tick',
    22: 'tickAmount',
    23: 'product',
    24: 'tradingHours',
    25: 'isTradable',
    26: 'marketMaker',
    27: '52WeekHigh',
    28: '52WeekLow',
    29: 'mark',
}

# CHART_EQUITY Field Definitions
CHART_EQUITY_FIELDS = {
    0: 'key',
    1: 'openPrice',
    2: 'highPrice',
    3: 'lowPrice',
    4: 'closePrice',
    5: 'volume',
    6: 'sequence',
    7: 'chartTime',
    8: 'chartDay',
}

# CHART_FUTURES Field Definitions
CHART_FUTURES_FIELDS = {
    0: 'key',
    1: 'chartTime',
    2: 'openPrice',
    3: 'highPrice',
    4: 'lowPrice',
    5: 'closePrice',
    6: 'volume',
}

# SCREENER Field Definitions
SCREENER_FIELDS = {
    0: 'symbol',
    1: 'timestamp',
    2: 'sortField',
    3: 'frequency',
    4: 'items',
}

# SCREENER Items Sub-Fields
SCREENER_ITEM_FIELDS = {
    'description': 'description',
    'lastPrice': 'lastPrice',
    'marketShare': 'marketShare',
    'netChange': 'netChange',
    'netPercentChange': 'netPercentChange',
    'symbol': 'symbol',
    'totalVolume': 'totalVolume',
    'trades': 'trades',
    'volume': 'volume',
}

# ACCT_ACTIVITY Field Definitions
ACCT_ACTIVITY_FIELDS = {
    'seq': 'sequence',
    'key': 'key',
    1: 'account',
    2: 'messageType',
    3: 'messageData',
}

# Book Field Definitions (NYSE_BOOK, NASDAQ_BOOK, OPTIONS_BOOK)
BOOK_FIELDS = {
    0: 'symbol',
    1: 'marketSnapshotTime',
    2: 'bidSideLevels',
    3: 'askSideLevels',
}

# Book Price Level Sub-Fields
BOOK_PRICE_LEVEL_FIELDS = {
    0: 'price',
    1: 'aggregateSize',
    2: 'marketMakerCount',
    3: 'marketMakers',
}

# Book Market Maker Sub-Fields
BOOK_MARKET_MAKER_FIELDS = {
    0: 'marketMakerId',
    1: 'size',
    2: 'quoteTime',
}


def parse_fields(data: dict, field_map: dict) -> dict:
    """
    Parse numeric field IDs to readable field names.
    
    Args:
        data: Raw data dict with numeric keys
        field_map: Field mapping dict
    
    Returns:
        Parsed dict with readable field names
    """
    parsed = {}
    for key, value in data.items():
        if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
            field_id = int(key)
            field_name = field_map.get(field_id, f'field_{field_id}')
            parsed[field_name] = value
        else:
            # Non-numeric keys (like 'key', 'delayed', etc.)
            parsed[key] = value
    return parsed
