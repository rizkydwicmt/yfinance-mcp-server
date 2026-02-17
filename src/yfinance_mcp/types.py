"""Type definitions and enums for YFinance MCP Server."""

from enum import Enum


class Period(str, Enum):
    """Valid periods for historical data."""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"


class Interval(str, Enum):
    """Valid intervals for historical data."""
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


class StatementType(str, Enum):
    """Financial statement types."""
    INCOME = "income"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    ALL = "all"


class MoverType(str, Enum):
    """Market mover categories."""
    GAINERS = "gainers"
    LOSERS = "losers"
    MOST_ACTIVE = "most_active"


# Key fields to extract from ticker.info for a clean summary
STOCK_INFO_FIELDS = [
    "symbol", "shortName", "longName", "sector", "industry",
    "country", "website", "longBusinessSummary",
    "marketCap", "enterpriseValue",
    "currentPrice", "previousClose", "open", "dayLow", "dayHigh",
    "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "fiftyDayAverage", "twoHundredDayAverage",
    "volume", "averageVolume", "averageDailyVolume10Day",
    "trailingPE", "forwardPE", "pegRatio", "priceToBook",
    "trailingEps", "forwardEps",
    "dividendRate", "dividendYield", "exDividendDate",
    "totalRevenue", "revenuePerShare", "revenueGrowth",
    "grossMargins", "ebitdaMargins", "operatingMargins", "profitMargins",
    "totalDebt", "debtToEquity", "totalCash", "freeCashflow",
    "returnOnAssets", "returnOnEquity",
    "beta", "bookValue", "earningsGrowth",
    "recommendationKey", "recommendationMean", "numberOfAnalystOpinions",
    "targetHighPrice", "targetLowPrice", "targetMeanPrice", "targetMedianPrice",
    "currency", "exchange", "quoteType",
]

PRICE_FIELDS = [
    "symbol", "shortName", "currency", "exchange",
    "currentPrice", "previousClose", "open",
    "dayLow", "dayHigh", "volume",
    "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
    "marketCap", "trailingPE", "dividendYield",
]
