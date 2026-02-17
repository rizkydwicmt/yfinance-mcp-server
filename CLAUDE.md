# CLAUDE.md — YFinance MCP Server

> Project context and instructions for AI assistants working on this codebase.

## Project Overview

This is a **Python MCP server** that wraps the [yfinance](https://github.com/ranaroussi/yfinance) library, exposing Yahoo Finance data through the Model Context Protocol. It provides 12 tools for stock prices, financials, options, dividends, market movers, screeners, search, and news.

- **Runtime**: Python ≥ 3.10 (deployed with 3.12 via `uv`)
- **Framework**: FastMCP from `mcp[cli]`
- **Transport**: stdio (standard input/output)
- **Entry point**: `yfin-mcp` (defined in `pyproject.toml` → `yfinance_mcp.server:main`)

## Architecture

```
src/yfinance_mcp/
├── server.py          # FastMCP instance + 12 @mcp.tool() registrations
├── types.py           # Enums: Period, Interval, StatementType, MoverType
├── utils.py           # JSON encoding, DataFrame→dict, safe_ticker_call
└── tools/
    ├── ticker.py      # 7 tools: info, price, history, financials, recommendations, options, dividends
    ├── market.py      # 3 tools: compare, market_movers, screen
    └── search.py      # 2 tools: search, news
```

### Data Flow

1. MCP client sends tool call via stdio → FastMCP routes to `@mcp.tool()` function in `server.py`
2. `server.py` delegates to the implementation in `tools/*.py`
3. Tool functions create `yfinance.Ticker(symbol)` objects and call yfinance APIs
4. Results are formatted via `utils.py` helpers (JSON encoding, DataFrame conversion, field extraction)
5. JSON string returned to the MCP client

### Key Design Patterns

- **Thin wrapper functions in `server.py`**: Each `@mcp.tool()` function is a thin proxy that delegates to `tools/*.py`. This separates MCP registration from business logic.
- **Safe calls via `safe_ticker_call()`**: All yfinance attribute/method access goes through this wrapper, which catches exceptions and returns structured error dicts.
- **`extract_fields()`**: Pulls only relevant fields from yfinance's verbose `info` dict using curated field lists defined in `types.py`.
- **`df_to_records()`**: Converts pandas DataFrames to list-of-dicts, handling DatetimeIndex conversion and NaN cleanup.
- **`FinanceEncoder`**: Custom JSON encoder handling `Timestamp`, `numpy` scalars, `NaN`, `Infinity`, and `datetime` objects.
- **Tool naming**: Functions in `server.py` are prefixed with `tool_` to avoid import collisions with the implementations in `tools/*.py`.

## Dependencies

| Package | Purpose |
|---------|---------|
| `yfinance ≥ 0.2.40` | Yahoo Finance API wrapper |
| `mcp[cli] ≥ 1.0.0` | MCP server framework (FastMCP) |
| `pandas` | Pulled in by yfinance — used for DataFrames |
| `numpy` | Pulled in by yfinance — used for numeric types |

## Development

### Local Setup

```bash
# Using uv (recommended)
uv venv .venv --python 3.12
uv pip install -e . --python .venv/bin/python

# Using pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running Locally

```bash
# Start the server (stdio mode — will listen on stdin)
.venv/bin/yfin-mcp

# Or run directly
.venv/bin/python -m yfinance_mcp.server
```

### Testing with mcporter

```bash
# List tools
mcporter --config /path/to/mcporter.json list yfinance --schema

# Call a tool
mcporter --config /path/to/mcporter.json call yfinance.tool_get_stock_price symbol=AAPL
```

### Quick Smoke Test (no MCP client)

```python
from yfinance_mcp.server import mcp
tools = list(mcp._tool_manager._tools.keys())
print(f"Registered tools ({len(tools)}): {tools}")
# Expected: 12 tools
```

## Server Deployment

### Production Path (on server)

- **Project**: `/root/project/mcp/yfinance-mcp-server/`
- **Venv**: `/root/project/mcp/yfinance-mcp-server/.venv/`
- **Binary**: `/root/project/mcp/yfinance-mcp-server/.venv/bin/yfin-mcp`
- **Python**: 3.12.12 (managed by `uv` at `/root/.local/bin/uv`)
- **Skill file**: `/root/clawd/skills/yfinance/SKILL.md`
- **mcporter config**: `/root/clawd/config/mcporter.json`

### Deploying Changes

```bash
# From local machine — copy updated files
scp -P 22 src/yfinance_mcp/*.py user@your-server:/tmp/
scp -P 22 src/yfinance_mcp/tools/*.py user@your-server:/tmp/

# On server — copy to project dir (editable install picks up changes)
sudo cp /tmp/server.py /root/project/mcp/yfinance-mcp-server/src/yfinance_mcp/
sudo cp /tmp/ticker.py /tmp/market.py /tmp/search.py /root/project/mcp/yfinance-mcp-server/src/yfinance_mcp/tools/

# If new dependencies added
sudo /root/.local/bin/uv pip install -e /root/project/mcp/yfinance-mcp-server/ \
  --python /root/project/mcp/yfinance-mcp-server/.venv/bin/python
```

## Adding a New Tool

1. **Implement** the function in the appropriate `tools/*.py` file:
   ```python
   # tools/ticker.py
   def get_splits(symbol: str) -> str:
       ticker = yf.Ticker(symbol)
       splits = safe_ticker_call("splits", ticker)
       if isinstance(splits, dict) and "error" in splits:
           return to_json(splits)
       records = df_to_records(splits) if hasattr(splits, 'to_dict') else []
       return to_json({"symbol": symbol, "splits": records})
   ```

2. **Import** in `server.py`:
   ```python
   from yfinance_mcp.tools.ticker import get_splits
   ```

3. **Register** as an MCP tool in `server.py`:
   ```python
   @mcp.tool()
   def tool_get_splits(symbol: str) -> str:
       """Get stock split history.

       Args:
           symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
       """
       return get_splits(symbol)
   ```

4. **Update** `SKILL.md` with usage examples.

### Tool Conventions

- Tool functions in `server.py` must be prefixed with `tool_` (e.g., `tool_get_splits`)
- Docstrings are used by FastMCP for the tool description and parameter docs — keep them clear and include `Args:` section
- All tools return `str` (JSON-serialized via `to_json()`)
- Use type hints for all parameters — FastMCP uses them for schema generation
- Default values create optional parameters in the MCP schema
- Use `str | None = None` for truly optional string params

## Error Handling

- **Never raise exceptions** from tool functions — always return structured JSON errors
- Use `safe_ticker_call()` for any yfinance attribute access
- The `to_json()` helper uses `FinanceEncoder` which handles pandas/numpy edge cases
- If a tool fails, the return format is: `{"error": "message", "symbol": "XYZ"}`

## Common Pitfalls

1. **`FastMCP()` constructor**: The installed `mcp` version may not support `version` or `instructions` kwargs — use only `FastMCP("name")`
2. **yfinance rate limits**: Yahoo Finance may throttle requests. The server handles this gracefully with error returns.
3. **`Screener` API**: `yfinance.Screener()` has limited predefined screeners (`day_gainers`, `day_losers`, `most_actives`). Custom screening uses `yfinance.screen()` or per-ticker filtering.
4. **DataFrame index**: yfinance history returns DatetimeIndex. `df_to_records()` converts this to `date` string fields.
5. **NaN values**: Financial data often contains NaN. `FinanceEncoder` converts these to `null` in JSON.
6. **Large numbers**: `extract_fields()` adds `_formatted` suffix fields (e.g., `marketCap_formatted: "3.76T"`) for readability.

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `pyproject.toml` | 22 | Package metadata, deps (`yfinance`, `mcp[cli]`), entry point (`yfin-mcp`) |
| `server.py` | ~200 | FastMCP instance, 12 `@mcp.tool()` registrations, `main()` entry |
| `types.py` | ~90 | Enums + curated field lists for `extract_fields()` |
| `utils.py` | ~100 | `FinanceEncoder`, `to_json()`, `df_to_records()`, `extract_fields()`, `safe_ticker_call()` |
| `tools/ticker.py` | ~170 | `get_stock_info`, `get_stock_price`, `get_history`, `get_financials`, `get_recommendations`, `get_options`, `get_dividends` |
| `tools/market.py` | ~130 | `compare_stocks`, `get_market_movers`, `screen_stocks` |
| `tools/search.py` | ~60 | `search_stocks`, `get_news` |
| `SKILL.md` | ~160 | AI agent skill reference — all tools with examples |
| `README.md` | ~250 | Install/deploy guide for all platforms |
