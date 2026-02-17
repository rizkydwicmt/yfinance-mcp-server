"""Market-wide tools: compare stocks, market movers, stock screener."""

from __future__ import annotations

import yfinance as yf

from yfinance_mcp.utils import to_json, extract_fields
from yfinance_mcp.types import PRICE_FIELDS


def compare_stocks(symbols: str) -> str:
    """Compare multiple stocks side by side with key metrics.

    Args:
        symbols: Comma-separated ticker symbols (e.g., 'AAPL,MSFT,GOOG')
                 or space-separated (e.g., 'AAPL MSFT GOOG'). Max 10 symbols.

    Returns:
        JSON string with comparison table of key metrics for all tickers.
    """
    # Parse symbols (support comma or space separated)
    symbol_list = [
        s.strip().upper()
        for s in symbols.replace(",", " ").split()
        if s.strip()
    ][:10]  # Limit to 10

    if not symbol_list:
        return to_json({"error": "No valid symbols provided."})

    comparison_fields = [
        "symbol", "shortName", "currency",
        "currentPrice", "previousClose",
        "marketCap", "trailingPE", "forwardPE",
        "dividendYield", "beta",
        "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
        "revenueGrowth", "profitMargins",
        "returnOnEquity", "debtToEquity",
        "recommendationKey",
    ]

    results = []
    for sym in symbol_list:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            if info and "symbol" in info:
                data = extract_fields(info, comparison_fields)

                # Add price change
                current = info.get("currentPrice") or info.get("regularMarketPrice")
                prev = info.get("previousClose")
                if current and prev:
                    data["changePercent"] = round(((current - prev) / prev) * 100, 2)

                results.append(data)
            else:
                results.append({"symbol": sym, "error": "No data found"})
        except Exception as e:
            results.append({"symbol": sym, "error": str(e)})

    return to_json({
        "count": len(results),
        "stocks": results,
    })


def get_market_movers(mover_type: str = "gainers") -> str:
    """Get top market movers: gainers, losers, or most active stocks.

    Uses yfinance's screen() to fetch current market movers.

    Args:
        mover_type: Type of movers. Valid values: 'gainers', 'losers',
                    'most_active'. Default: 'gainers'.

    Returns:
        JSON string with top movers data.
    """
    screener_map = {
        "gainers": "day_gainers",
        "losers": "day_losers",
        "most_active": "most_actives",
    }

    screener_key = screener_map.get(mover_type, "day_gainers")

    try:
        result = yf.screen(screener_key, count=20)

        if result and "quotes" in result:
            quotes = result["quotes"]
            movers = []
            for q in quotes[:20]:
                mover = {
                    "symbol": q.get("symbol"),
                    "name": q.get("shortName") or q.get("longName"),
                    "price": q.get("regularMarketPrice"),
                    "change": q.get("regularMarketChange"),
                    "changePercent": q.get("regularMarketChangePercent"),
                    "volume": q.get("regularMarketVolume"),
                    "marketCap": q.get("marketCap"),
                }
                movers.append(mover)

            return to_json({
                "type": mover_type,
                "count": len(movers),
                "movers": movers,
            })

        return to_json({"type": mover_type, "movers": [], "message": "No data available."})

    except Exception as e:
        return to_json({
            "type": mover_type,
            "error": str(e),
            "hint": "Market movers may not be available in all regions.",
        })


def screen_stocks(
    sector: str | None = None,
    min_market_cap: float | None = None,
    max_pe_ratio: float | None = None,
    min_dividend_yield: float | None = None,
    exchange: str | None = None,
) -> str:
    """Screen stocks by fundamental criteria.

    Note: This uses yfinance's screen() with predefined screens.
    For complex custom queries, results may be limited.

    Args:
        sector: Filter by sector (e.g., 'Technology', 'Healthcare', 'Financial Services').
        min_market_cap: Minimum market cap in USD (e.g., 1000000000 for $1B).
        max_pe_ratio: Maximum trailing P/E ratio (e.g., 25).
        min_dividend_yield: Minimum dividend yield as decimal (e.g., 0.03 for 3%).
        exchange: Filter by exchange (e.g., 'NMS' for NASDAQ, 'NYQ' for NYSE).

    Returns:
        JSON string with screened stocks matching criteria.
    """
    try:
        result = yf.screen("most_actives", count=100)

        if not result or "quotes" not in result:
            return to_json({"stocks": [], "message": "Screener returned no data."})

        quotes = result["quotes"]
        filtered = []

        for q in quotes:
            # Apply filters
            if sector and q.get("sector", "").lower() != sector.lower():
                continue
            if min_market_cap and (q.get("marketCap") or 0) < min_market_cap:
                continue
            if max_pe_ratio and (q.get("trailingPE") or float("inf")) > max_pe_ratio:
                continue
            if min_dividend_yield and (q.get("dividendYield") or 0) < min_dividend_yield:
                continue
            if exchange and q.get("exchange", "").upper() != exchange.upper():
                continue

            filtered.append({
                "symbol": q.get("symbol"),
                "name": q.get("shortName") or q.get("longName"),
                "sector": q.get("sector"),
                "price": q.get("regularMarketPrice"),
                "marketCap": q.get("marketCap"),
                "pe": q.get("trailingPE"),
                "dividendYield": q.get("dividendYield"),
                "volume": q.get("regularMarketVolume"),
            })

        return to_json({
            "filters_applied": {
                "sector": sector,
                "min_market_cap": min_market_cap,
                "max_pe_ratio": max_pe_ratio,
                "min_dividend_yield": min_dividend_yield,
                "exchange": exchange,
            },
            "count": len(filtered),
            "stocks": filtered[:30],
        })

    except Exception as e:
        return to_json({"error": str(e)})

