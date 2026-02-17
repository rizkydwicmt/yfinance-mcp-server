"""Ticker-related tools: stock info, price, history, financials, etc."""

from __future__ import annotations

import yfinance as yf

from yfinance_mcp.types import (
    STOCK_INFO_FIELDS,
    PRICE_FIELDS,
    Period,
    Interval,
    StatementType,
)
from yfinance_mcp.utils import to_json, df_to_records, extract_fields, safe_ticker_call


def get_stock_info(symbol: str) -> str:
    """Get comprehensive company information for a stock ticker.

    Returns company details including sector, industry, market cap,
    valuation ratios, margins, analyst targets, and more.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BBCA.JK', 'TSLA').

    Returns:
        JSON string with company information.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info

    if not info or "symbol" not in info:
        return to_json({"error": f"No data found for symbol '{symbol}'."})

    data = extract_fields(info, STOCK_INFO_FIELDS)
    return to_json(data)


def get_stock_price(symbol: str) -> str:
    """Get current stock price and key trading metrics.

    Returns real-time price, day range, volume, 52-week range,
    market cap, P/E ratio, and dividend yield.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BBCA.JK').

    Returns:
        JSON string with current price data.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info

    if not info or "symbol" not in info:
        return to_json({"error": f"No data found for symbol '{symbol}'."})

    data = extract_fields(info, PRICE_FIELDS)

    # Calculate change from previous close
    current = info.get("currentPrice") or info.get("regularMarketPrice")
    prev_close = info.get("previousClose")
    if current and prev_close:
        change = current - prev_close
        change_pct = (change / prev_close) * 100
        data["change"] = round(change, 4)
        data["changePercent"] = round(change_pct, 2)
        data["direction"] = "▲" if change > 0 else "▼" if change < 0 else "—"

    return to_json(data)


def get_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
) -> str:
    """Get historical OHLCV (Open, High, Low, Close, Volume) data.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BBCA.JK').
        period: Data period. Valid values: 1d, 5d, 1mo, 3mo, 6mo,
                1y, 2y, 5y, 10y, ytd, max. Default: '1mo'.
        interval: Data interval. Valid values: 1m, 2m, 5m, 15m, 30m,
                  60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Default: '1d'.

    Returns:
        JSON string with historical price data as array of records.
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)

    if df is None or df.empty:
        return to_json({
            "error": f"No history data for '{symbol}' with period={period}, interval={interval}.",
        })

    records = df_to_records(df)
    return to_json({
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "count": len(records),
        "data": records,
    })


def get_financials(
    symbol: str,
    statement_type: str = "all",
    quarterly: bool = False,
) -> str:
    """Get financial statements: income statement, balance sheet, cash flow.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT').
        statement_type: Type of statement. Valid values: income, balance_sheet,
                        cash_flow, all. Default: 'all'.
        quarterly: If true, return quarterly data instead of annual. Default: false.

    Returns:
        JSON string with financial statement data.
    """
    ticker = yf.Ticker(symbol)
    result: dict = {"symbol": symbol, "quarterly": quarterly}

    statements = {
        "income": ("income_stmt", "quarterly_income_stmt"),
        "balance_sheet": ("balance_sheet", "quarterly_balance_sheet"),
        "cash_flow": ("cashflow", "quarterly_cashflow"),
    }

    targets = (
        statements.items()
        if statement_type == "all"
        else [(statement_type, statements.get(statement_type, (None, None)))]
    )

    for name, (annual_attr, quarterly_attr) in targets:
        if annual_attr is None:
            result[name] = {"error": f"Invalid statement type: {name}"}
            continue

        attr_name = quarterly_attr if quarterly else annual_attr
        df = safe_ticker_call(attr_name, ticker)

        if isinstance(df, dict) and "error" in df:
            result[name] = df
        else:
            result[name] = df_to_records(df) if hasattr(df, "empty") else df

    return to_json(result)


def get_recommendations(symbol: str) -> str:
    """Get analyst recommendations and price targets for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').

    Returns:
        JSON string with analyst recommendations, upgrades/downgrades,
        and price targets.
    """
    ticker = yf.Ticker(symbol)
    result: dict = {"symbol": symbol}

    # Analyst price targets
    targets = safe_ticker_call("analyst_price_targets", ticker)
    if isinstance(targets, dict) and "error" not in targets:
        result["price_targets"] = targets
    elif hasattr(targets, "to_dict"):
        result["price_targets"] = targets.to_dict()

    # Recommendations summary
    recs = safe_ticker_call("recommendations", ticker)
    if hasattr(recs, "empty") and not recs.empty:
        result["recommendations"] = df_to_records(recs, max_rows=20)

    # Upgrades/downgrades
    upgrades = safe_ticker_call("upgrades_downgrades", ticker)
    if hasattr(upgrades, "empty") and not upgrades.empty:
        result["upgrades_downgrades"] = df_to_records(upgrades, max_rows=20)

    return to_json(result)


def get_options(symbol: str, expiration: str | None = None) -> str:
    """Get options chain data (calls and puts) for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
        expiration: Expiration date string (e.g., '2025-03-21').
                    If not provided, uses the nearest expiration.

    Returns:
        JSON string with calls and puts data plus available expirations.
    """
    ticker = yf.Ticker(symbol)
    result: dict = {"symbol": symbol}

    try:
        expirations = ticker.options
        result["available_expirations"] = list(expirations)

        if not expirations:
            return to_json({"error": f"No options data available for '{symbol}'."})

        exp_date = expiration if expiration and expiration in expirations else expirations[0]
        result["selected_expiration"] = exp_date

        chain = ticker.option_chain(exp_date)
        result["calls"] = df_to_records(chain.calls, max_rows=50)
        result["puts"] = df_to_records(chain.puts, max_rows=50)

    except Exception as e:
        result["error"] = str(e)

    return to_json(result)


def get_dividends(symbol: str) -> str:
    """Get dividend payment history for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'JNJ').

    Returns:
        JSON string with dividend history and current yield info.
    """
    ticker = yf.Ticker(symbol)
    result: dict = {"symbol": symbol}

    # Dividend history
    dividends = ticker.dividends
    if dividends is not None and not dividends.empty:
        div_df = dividends.reset_index()
        div_df.columns = ["date", "dividend"]
        div_df["date"] = div_df["date"].dt.strftime("%Y-%m-%d")
        result["history"] = div_df.tail(20).to_dict(orient="records")
        result["total_dividends_paid"] = round(float(dividends.sum()), 4)
        result["count"] = len(dividends)
    else:
        result["history"] = []
        result["message"] = "No dividend history available."

    # Current dividend info from ticker info
    info = ticker.info
    for field in ["dividendRate", "dividendYield", "exDividendDate", "payoutRatio"]:
        if field in info and info[field] is not None:
            result[field] = info[field]

    return to_json(result)
