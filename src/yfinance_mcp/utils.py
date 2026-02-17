"""Utility functions for YFinance MCP Server."""

from __future__ import annotations

import json
from datetime import datetime, date
from typing import Any

import pandas as pd


class FinanceEncoder(json.JSONEncoder):
    """Custom JSON encoder for financial data types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Timedelta):
            return str(obj)
        if hasattr(obj, "item"):  # numpy scalar
            return obj.item()
        if pd.isna(obj):
            return None
        return super().default(obj)


def _clean_nan(obj: Any) -> Any:
    """Recursively replace NaN/Inf float values with None."""
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(v) for v in obj]
    if isinstance(obj, float):
        import math
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj


def to_json(data: Any, indent: int = 2) -> str:
    """Serialize data to JSON string with financial type handling."""
    data = _clean_nan(data)
    return json.dumps(data, cls=FinanceEncoder, indent=indent, ensure_ascii=False)


def df_to_records(df: pd.DataFrame, max_rows: int = 100) -> list[dict]:
    """Convert DataFrame to list of dicts with clean index handling.

    Args:
        df: Input DataFrame.
        max_rows: Maximum rows to return (prevents huge responses).

    Returns:
        List of row dictionaries with index as a field.
    """
    if df is None or df.empty:
        return []

    df = df.head(max_rows).copy()

    # Convert index to column if it's a DatetimeIndex
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime("%Y-%m-%d")
        df = df.reset_index()
        df.rename(columns={df.columns[0]: "date"}, inplace=True)
    elif df.index.name:
        df = df.reset_index()

    # Clean NaN values
    df = df.where(pd.notna(df), None)

    # Convert any Timestamp column names to strings (e.g., financial statements)
    df.columns = [
        col.isoformat() if isinstance(col, (pd.Timestamp, datetime)) else col
        for col in df.columns
    ]

    records = df.to_dict(orient="records")

    # Round float values for readability
    for record in records:
        for key, value in record.items():
            if isinstance(value, float):
                record[key] = round(value, 4)

    return records


def extract_fields(info: dict, fields: list[str]) -> dict:
    """Extract specific fields from a dict, skipping missing keys.

    Args:
        info: Source dictionary (e.g., ticker.info).
        fields: List of field names to extract.

    Returns:
        Dict with only the requested fields that exist.
    """
    result = {}
    for field in fields:
        if field in info and info[field] is not None:
            value = info[field]
            # Format large numbers for readability
            if isinstance(value, (int, float)) and abs(value) >= 1e9:
                result[field] = value
                result[f"{field}_formatted"] = _format_large_number(value)
            else:
                result[field] = value
    return result


def _format_large_number(value: float) -> str:
    """Format large numbers with suffix (B, M, K)."""
    abs_val = abs(value)
    if abs_val >= 1e12:
        return f"{'−' if value < 0 else ''}{abs_val / 1e12:.2f}T"
    if abs_val >= 1e9:
        return f"{'−' if value < 0 else ''}{abs_val / 1e9:.2f}B"
    if abs_val >= 1e6:
        return f"{'−' if value < 0 else ''}{abs_val / 1e6:.2f}M"
    if abs_val >= 1e3:
        return f"{'−' if value < 0 else ''}{abs_val / 1e3:.2f}K"
    return str(value)


def safe_ticker_call(func_name: str, ticker, *args, **kwargs) -> Any:
    """Safely call a yfinance ticker method with error handling.

    Args:
        func_name: Name of the method/property to access.
        ticker: yfinance Ticker object.

    Returns:
        Result of the call, or error dict on failure.
    """
    try:
        attr = getattr(ticker, func_name)
        if callable(attr):
            return attr(*args, **kwargs)
        return attr
    except Exception as e:
        return {"error": f"Failed to get {func_name}: {str(e)}"}
