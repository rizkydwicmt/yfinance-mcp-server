"""Search and news tools."""

from __future__ import annotations

import yfinance as yf

from yfinance_mcp.utils import to_json


def search_stocks(query: str, max_results: int = 10) -> str:
    """Search for stocks, ETFs, mutual funds, and other financial instruments.

    Args:
        query: Search query (e.g., 'Apple', 'tech ETF', 'semiconductor').
        max_results: Maximum number of results to return. Default: 10, max: 20.

    Returns:
        JSON string with matching tickers, names, types, and exchanges.
    """
    max_results = min(max_results, 20)

    try:
        search = yf.Search(query)
        results = []

        # Quotes (primary results)
        if hasattr(search, "quotes") and search.quotes:
            for q in search.quotes[:max_results]:
                results.append({
                    "symbol": q.get("symbol"),
                    "name": q.get("shortname") or q.get("longname"),
                    "type": q.get("quoteType"),
                    "exchange": q.get("exchange"),
                    "sector": q.get("sector"),
                    "industry": q.get("industry"),
                })

        return to_json({
            "query": query,
            "count": len(results),
            "results": results,
        })

    except Exception as e:
        return to_json({"query": query, "error": str(e)})


def get_news(symbol: str, max_items: int = 10) -> str:
    """Get latest news articles for a stock ticker.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'BBCA.JK').
        max_items: Maximum number of news items. Default: 10, max: 20.

    Returns:
        JSON string with news articles including title, publisher,
        link, and publish time.
    """
    max_items = min(max_items, 20)

    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news

        if not news:
            return to_json({
                "symbol": symbol,
                "articles": [],
                "message": f"No news available for '{symbol}'.",
            })

        articles = []
        for item in news[:max_items]:
            content = item.get("content", {})
            article = {
                "title": content.get("title"),
                "publisher": content.get("provider", {}).get("displayName"),
                "link": content.get("canonicalUrl", {}).get("url"),
                "summary": content.get("summary"),
                "publishedAt": content.get("pubDate"),
                "thumbnail": content.get("thumbnail", {}).get("originalUrl")
                if content.get("thumbnail")
                else None,
            }
            articles.append(article)

        return to_json({
            "symbol": symbol,
            "count": len(articles),
            "articles": articles,
        })

    except Exception as e:
        return to_json({"symbol": symbol, "error": str(e)})
