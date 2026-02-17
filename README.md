# YFinance MCP Server

A comprehensive MCP (Model Context Protocol) server for Yahoo Finance data, powered by the [yfinance](https://github.com/ranaroussi/yfinance) Python library. Provides 12 tools covering stock prices, company fundamentals, financial statements, analyst recommendations, options, dividends, market movers, screeners, search, and news.

## Features

| Tool | Description |
|------|-------------|
| `tool_get_stock_info` | Company info — sector, market cap, P/E, margins, description |
| `tool_get_stock_price` | Current price, change %, day range, volume, 52-week range |
| `tool_get_history` | Historical OHLCV data (customizable period & interval) |
| `tool_get_financials` | Income statement, balance sheet, cash flow (annual/quarterly) |
| `tool_get_recommendations` | Analyst ratings, price targets, upgrades/downgrades |
| `tool_get_options` | Options chain — calls & puts with greeks |
| `tool_get_dividends` | Dividend history + current yield |
| `tool_compare_stocks` | Compare up to 10 stocks side by side |
| `tool_get_market_movers` | Top gainers, losers, most active stocks |
| `tool_screen_stocks` | Screen by sector, market cap, P/E, dividend yield |
| `tool_search_stocks` | Find tickers by name, sector, or keyword |
| `tool_get_news` | Latest news articles for any ticker |

## Supported Markets

Works with **any ticker supported by Yahoo Finance**:

| Market | Examples |
|--------|----------|
| 🇺🇸 US | AAPL, MSFT, GOOG, TSLA, AMZN |
| 🇮🇩 Indonesia | BBCA.JK, BBRI.JK, TLKM.JK |
| 🇯🇵 Japan | 7203.T (Toyota), 6758.T (Sony) |
| 🇬🇧 UK | SHEL.L, AZN.L, HSBA.L |
| 🇭🇰 Hong Kong | 0700.HK (Tencent) |
| 📊 ETFs | SPY, QQQ, VTI, VOO |
| ₿ Crypto | BTC-USD, ETH-USD, SOL-USD |
| 📈 Indices | ^GSPC (S&P 500), ^JKSE (IDX) |
| 💱 Forex | USDIDR=X, EURUSD=X |

---

## Installation

### Prerequisites

- **Python** ≥ 3.10
- **uv** (recommended) or **pip**

### Option A: Install with uv (recommended)

[uv](https://docs.astral.sh/uv/) manages Python versions and virtual environments automatically.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the project from GitHub
git clone https://github.com/rizkydwicmt/yfinance-mcp-server.git yfinance-mcp-server
cd yfinance-mcp-server

# Create venv with Python 3.12 and install
uv venv .venv --python 3.12
uv pip install -e . --python .venv/bin/python

# Verify
.venv/bin/yfin-mcp --help
```

### Option B: Install with pip

```bash
# Ensure Python ≥ 3.10
python3 --version

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install in editable mode
pip install -e .

# Verify
yfin-mcp --help
```

### Option C: Install from source (no venv)

```bash
pip install -e /path/to/yfinance-mcp-server
```

---

## Running the Server

### Standalone (stdio transport)

The server communicates over stdin/stdout using the MCP stdio transport:

```bash
# If installed in a venv
.venv/bin/yfin-mcp

# If installed globally
yfin-mcp

# Or run directly with Python
python -m yfinance_mcp.server
```

> **Note:** The server is designed to be launched by an MCP client (like Claude, Cursor, or mcporter). Running it standalone will start the stdio listener — you won't see interactive output.

### With mcporter CLI

[mcporter](https://github.com/nicepkg/mcporter) is a CLI tool for managing and calling MCP servers.

#### 1. Configure mcporter

Add the yfinance server to your `mcporter.json`:

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "/absolute/path/to/yfinance-mcp-server/.venv/bin/yfin-mcp"
    }
  }
}
```

#### 2. Verify registration

```bash
# List all tools
mcporter --config /path/to/mcporter.json list yfinance

# With full schema
mcporter --config /path/to/mcporter.json list yfinance --schema
```

#### 3. Call tools

```bash
# Get current stock price
mcporter call yfinance.tool_get_stock_price symbol=AAPL

# Get historical data
mcporter call yfinance.tool_get_history symbol=BBCA.JK period=1y interval=1wk

# Compare stocks
mcporter call yfinance.tool_compare_stocks symbols="AAPL,MSFT,GOOG"

# Search for stocks
mcporter call yfinance.tool_search_stocks query="semiconductor ETF"

# Get market movers
mcporter call yfinance.tool_get_market_movers mover_type=gainers

# Get financial statements
mcporter call yfinance.tool_get_financials symbol=MSFT statement_type=income quarterly=true

# Screen stocks
mcporter call yfinance.tool_screen_stocks sector=Technology min_market_cap=1000000000

# Get news
mcporter call yfinance.tool_get_news symbol=TSLA max_items=5
```

---

## Deploy with OpenClaw

[OpenClaw](https://github.com/nicepkg/openclaw) is a self-hosted AI gateway that manages MCP servers for AI agents.

### Step 1: Copy project to the server

```bash
scp -r -P <port> ./yfinance-mcp-server user@your-server:/root/project/mcp/yfinance-mcp-server
```

### Step 2: Install on the server

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv + install
/root/.local/bin/uv venv /root/project/mcp/yfinance-mcp-server/.venv --python 3.12
/root/.local/bin/uv pip install -e /root/project/mcp/yfinance-mcp-server/ \
  --python /root/project/mcp/yfinance-mcp-server/.venv/bin/python
```

### Step 3: Add to OpenClaw / mcporter config

Edit the mcporter config file (typically at `/root/clawd/config/mcporter.json`):

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "/root/project/mcp/yfinance-mcp-server/.venv/bin/yfin-mcp"
    }
  }
}
```

### Step 4: Verify

```bash
mcporter --config /root/clawd/config/mcporter.json list yfinance --schema
mcporter --config /root/clawd/config/mcporter.json call yfinance.tool_get_stock_price symbol=AAPL
```

Expected output:
```json
{
  "symbol": "AAPL",
  "shortName": "Apple Inc.",
  "currentPrice": 255.78,
  "change": -5.95,
  "changePercent": -2.27,
  "marketCap_formatted": "3.76T",
  "direction": "▼"
}
```

---

## Install as OpenClaw Skill

OpenClaw agents can discover and use the yfinance tools through its **skills** system. Skills are folders containing a `SKILL.md` file that provides tool documentation and usage examples for AI agents.

### Quick Install (one command)

```bash
# On your OpenClaw server — copy SKILL.md into the skills directory
sudo mkdir -p /root/clawd/skills/yfinance && \
sudo cp /root/project/mcp/yfinance-mcp-server/SKILL.md /root/clawd/skills/yfinance/SKILL.md
```

### Manual Install (step by step)

#### Step 1: Create the skill directory

```bash
sudo mkdir -p /root/clawd/skills/yfinance
```

#### Step 2: Copy the SKILL.md

```bash
# From the project directory
sudo cp /root/project/mcp/yfinance-mcp-server/SKILL.md /root/clawd/skills/yfinance/SKILL.md

# Or from source (if installing on a new server)
scp -P <port> ./SKILL.md user@your-server:/tmp/SKILL.md
sudo mkdir -p /root/clawd/skills/yfinance
sudo cp /tmp/SKILL.md /root/clawd/skills/yfinance/SKILL.md
```

#### Step 3: (Optional) Add a skill README

```bash
sudo cp /root/project/mcp/yfinance-mcp-server/README.md /root/clawd/skills/yfinance/README.md
```

#### Step 4: Verify the skill is installed

```bash
# Check skill files exist
ls -la /root/clawd/skills/yfinance/
# Expected:
#   SKILL.md    — tool reference for AI agents
#   README.md   — optional human-readable overview

# Check SKILL.md has correct frontmatter
head -3 /root/clawd/skills/yfinance/SKILL.md
# Expected:
#   ---
#   name: yfinance
#   description: Access Yahoo Finance data — stock prices, history, financials, ...
```

### What the Skill Provides

Once installed, AI agents on your OpenClaw server will see the yfinance skill and can:

- Query real-time stock prices for any market (US, Indonesia, Japan, etc.)
- Analyze financial statements and fundamentals
- Compare multiple stocks side by side
- Screen stocks by sector, market cap, P/E ratio
- Get analyst recommendations and options chains
- Search for tickers and read the latest news

### Requirements

The skill documentation (`SKILL.md`) tells agents *what tools are available*, but the actual MCP server must also be installed and registered in `mcporter.json`. See the [Deploy with OpenClaw](#deploy-with-openclaw) section above.

### Skill Directory Structure

```
/root/clawd/
├── config/
│   └── mcporter.json        ← MCP server registration
└── skills/
    └── yfinance/
        ├── SKILL.md          ← Tool reference (required)
        └── README.md         ← Overview (optional)
```

---

## Integration with AI Clients

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "/absolute/path/to/yfinance-mcp-server/.venv/bin/yfin-mcp"
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "/absolute/path/to/yfinance-mcp-server/.venv/bin/yfin-mcp"
    }
  }
}
```

### VS Code (Copilot)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "yfinance": {
      "type": "stdio",
      "command": "/absolute/path/to/yfinance-mcp-server/.venv/bin/yfin-mcp"
    }
  }
}
```

### Windsurf / Cline / Any MCP Client

The server uses standard **stdio transport**, so it works with any MCP-compatible client. Point the client to the `yfin-mcp` binary as the command.

---

## Project Structure

```
yfinance-mcp-server/
├── pyproject.toml                  # Package config, deps, entry point
├── README.md                       # This file
├── SKILL.md                        # Tool reference for AI agents
├── src/
│   └── yfinance_mcp/
│       ├── __init__.py             # Package version
│       ├── server.py               # FastMCP server + all 12 tool registrations
│       ├── types.py                # Enums (Period, Interval, StatementType, etc.)
│       ├── utils.py                # JSON encoding, DataFrame helpers, error handling
│       └── tools/
│           ├── __init__.py
│           ├── ticker.py           # 7 ticker tools (info, price, history, etc.)
│           ├── market.py           # 3 market tools (compare, movers, screener)
│           └── search.py           # 2 search/news tools
└── tests/
    └── (test files)
```

## Example Queries

Once connected to an AI assistant:

- *"What's the current price of AAPL?"*
- *"Show me BBCA.JK historical data for the past year"*
- *"Compare TSLA, RIVN, and NIO on key metrics"*
- *"Get the income statement for Microsoft"*
- *"Search for semiconductor stocks"*
- *"Show me today's top market gainers"*
- *"What are analysts recommending for Tesla?"*
- *"Get options chain for AAPL expiring March 2025"*
- *"Screen for tech stocks with P/E under 25 and market cap above $10B"*
- *"Latest news about Apple"*

## Troubleshooting

### `FastMCP.__init__() got an unexpected keyword argument 'version'`
The installed `mcp[cli]` version may not support the `version` kwarg. The server is already patched to use `FastMCP("YFinance MCP Server")` without extra kwargs.

### `mcporter: Unknown MCP server 'yfinance'`
mcporter reads config from `./config/mcporter.json` relative to the working directory. Run from the config's parent dir, or use `--config`:
```bash
mcporter --config /path/to/mcporter.json list yfinance
```

### `pip: command not found` / Python too old
Use `uv` — it downloads and manages Python versions automatically:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.12
uv pip install -e . --python .venv/bin/python
```

### Rate limiting / API errors
Yahoo Finance may throttle heavy usage. The server includes built-in error handling — errors are returned as structured JSON rather than crashing.

## License

MIT
