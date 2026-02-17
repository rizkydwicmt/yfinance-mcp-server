"""YFinance MCP Server — Main entry point.

A comprehensive MCP server providing Yahoo Finance data tools
via the Model Context Protocol. Powered by the yfinance library.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from yfinance_mcp.tools.ticker import (
    get_stock_info,
    get_stock_price,
    get_history,
    get_financials,
    get_recommendations,
    get_options,
    get_dividends,
)
from yfinance_mcp.tools.market import (
    compare_stocks,
    get_market_movers,
    screen_stocks,
)
from yfinance_mcp.tools.search import (
    search_stocks,
    get_news,
)

# ── Server Instance ──────────────────────────────────────────────────────────

mcp = FastMCP("YFinance MCP Server")


# ── Ticker Tools ─────────────────────────────────────────────────────────────

@mcp.tool()
def tool_get_stock_info(symbol: str) -> str:
    """Get comprehensive company information for a stock ticker.

    Returns company details including sector, industry, market cap,
    valuation ratios, margins, analyst targets, and business description.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BBCA.JK', 'TSLA').
    """
    return get_stock_info(symbol)


@mcp.tool()
def tool_get_stock_price(symbol: str) -> str:
    """Get current stock price and key trading metrics.

    Returns real-time price, price change, day range, volume,
    52-week range, market cap, P/E ratio, and dividend yield.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BBCA.JK').
    """
    return get_stock_price(symbol)


@mcp.tool()
def tool_get_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
) -> str:
    """Get historical OHLCV (Open, High, Low, Close, Volume) price data.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'BBCA.JK').
        period: Data period. Valid: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
        interval: Data interval. Valid: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.
    """
    return get_history(symbol, period, interval)


@mcp.tool()
def tool_get_financials(
    symbol: str,
    statement_type: str = "all",
    quarterly: bool = False,
) -> str:
    """Get financial statements: income statement, balance sheet, cash flow.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT').
        statement_type: Type of statement. Valid: income, balance_sheet, cash_flow, all.
        quarterly: If true, return quarterly data instead of annual.
    """
    return get_financials(symbol, statement_type, quarterly)


@mcp.tool()
def tool_get_recommendations(symbol: str) -> str:
    """Get analyst recommendations, price targets, and upgrades/downgrades.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
    """
    return get_recommendations(symbol)


@mcp.tool()
def tool_get_options(symbol: str, expiration: str | None = None) -> str:
    """Get options chain data (calls and puts) for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
        expiration: Expiration date (e.g., '2025-03-21'). Uses nearest if omitted.
    """
    return get_options(symbol, expiration)


@mcp.tool()
def tool_get_dividends(symbol: str) -> str:
    """Get dividend payment history and current yield info.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'JNJ', 'BBCA.JK').
    """
    return get_dividends(symbol)


# ── Market Tools ─────────────────────────────────────────────────────────────

@mcp.tool()
def tool_compare_stocks(symbols: str) -> str:
    """Compare multiple stocks side by side with key metrics.

    Returns price, market cap, P/E, dividend yield, margins, growth,
    and analyst recommendations for each stock.

    Args:
        symbols: Comma or space separated symbols (e.g., 'AAPL,MSFT,GOOG'). Max 10.
    """
    return compare_stocks(symbols)


@mcp.tool()
def tool_get_market_movers(mover_type: str = "gainers") -> str:
    """Get top market movers: gainers, losers, or most active stocks.

    Args:
        mover_type: Type of movers. Valid: 'gainers', 'losers', 'most_active'.
    """
    return get_market_movers(mover_type)


@mcp.tool()
def tool_screen_stocks(
    sector: str | None = None,
    min_market_cap: float | None = None,
    max_pe_ratio: float | None = None,
    min_dividend_yield: float | None = None,
    exchange: str | None = None,
) -> str:
    """Screen stocks by fundamental criteria.

    Args:
        sector: Filter by sector (e.g., 'Technology', 'Healthcare').
        min_market_cap: Minimum market cap in USD (e.g., 1000000000 for $1B).
        max_pe_ratio: Maximum trailing P/E ratio (e.g., 25).
        min_dividend_yield: Minimum dividend yield as decimal (e.g., 0.03 for 3%).
        exchange: Filter by exchange (e.g., 'NMS' for NASDAQ).
    """
    return screen_stocks(sector, min_market_cap, max_pe_ratio, min_dividend_yield, exchange)


# ── Search & News Tools ──────────────────────────────────────────────────────

@mcp.tool()
def tool_search_stocks(query: str, max_results: int = 10) -> str:
    """Search for stocks, ETFs, mutual funds, and other instruments.

    Args:
        query: Search query (e.g., 'Apple', 'tech ETF', 'semiconductor').
        max_results: Maximum results (1-20, default 10).
    """
    return search_stocks(query, max_results)


@mcp.tool()
def tool_get_news(symbol: str, max_items: int = 10) -> str:
    """Get latest news articles for a stock ticker.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'BBCA.JK').
        max_items: Maximum news items (1-20, default 10).
    """
    return get_news(symbol, max_items)


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    """Run the YFinance MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
