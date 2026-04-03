# LLM VolFlow Trader

**AI-Powered Portfolio Management & Swing Trading Platform**

- **Live URL:** https://volflowagent.com
- **GitHub:** https://github.com/ROOK-KNIGHT/LLMtrader
- **EC2 IP:** 3.238.51.196

---

## Overview

LLM VolFlow Trader is a next-generation trading platform that combines institutional-grade market analysis with AI-powered decision making. Users authenticate, connect their Schwab brokerage account, and interact with an LLM (Claude, Grok, or Gemini) that can analyze markets, pull real-time data, and execute trades — all through a Bloomberg-style terminal UI.

### Key Features

- **Email/Password Authentication** — JWT-based auth with bcrypt hashing
- **Schwab API Integration** — Full OAuth2 flow, token auto-refresh, all REST endpoints
- **LLM-Powered Trading** — Claude Sonnet / Grok / Gemini with 40+ tool calls
- **Pre-Screened Prompt Library** — 20+ institutional-grade trading strategies
- **Real-Time Streaming** — WebSocket streaming for quotes, charts, account activity
- **Technical Indicators** — TA-Lib: RSI, MACD, Bollinger Bands, ATR, VWAP, etc.
- **Macroeconomic Data** — Alpha Vantage: GDP, CPI, Fed Funds Rate, Treasury Yields, NFP
- **Company Fundamentals** — Alpha Vantage: Income Statement, Balance Sheet, Earnings, IPO Calendar
- **Bloomberg Terminal UI** — Vue 3 SPA with dark theme, TradingView Lightweight Charts
- **Multi-Tenant** — Per-user Schwab credentials encrypted with Fernet

---

## Tech Stack

**Backend:**
- Python 3.11 / FastAPI / Uvicorn (4 workers)
- PostgreSQL 16 (user data, positions, conversation history)
- Schwab API (OAuth2, REST, WebSocket streaming)
- Alpha Vantage API (macroeconomic + fundamental data)
- Fernet encryption (Schwab credential storage)
- TA-Lib (technical indicators)

**Frontend:**
- Vue 3 + Vite (SPA, built to `/app/frontend/dist`)
- Pinia (state management)
- TradingView Lightweight Charts
- Bloomberg-inspired dark theme

**AI/LLM:**
- Claude Sonnet (Anthropic)
- Grok Fast (xAI)
- Gemini Pro (Google)
- Single model OR debate mode per request

**Infrastructure:**
- AWS EC2 (c5.xlarge, Ubuntu 22.04)
- Docker + docker-compose (single container: nginx + uvicorn + token-refresher)
- Supervisor (process manager inside container)
- NGINX (reverse proxy, SSL termination)
- Let's Encrypt (SSL certificates, mounted from host)
- Route53 (DNS)

---

## Project Structure

```
LLM_VolFlow_Trader/
├── README.md
├── Dockerfile                        # Multi-stage: builds Vue frontend + installs Python deps
├── docker-compose.yml                # Two services: postgres + app
├── nginx.conf                        # NGINX config (SSL, proxy to uvicorn on :8000)
├── supervisord.conf                  # Manages nginx + uvicorn + token-refresher inside container
├── .env                              # Environment variables (NOT committed)
├── backend/
│   ├── server.py                     # FastAPI app — all HTTP + WebSocket routes
│   ├── database.py                   # PostgreSQL schema + connection pool
│   ├── token_refresher.py            # Background process: refreshes Schwab tokens every 25min
│   ├── requirements.txt              # Python dependencies
│   ├── ai/
│   │   ├── llm_handler.py            # LLM API calls (Claude/Grok/Gemini)
│   │   ├── conversation.py           # Conversation history + tool execution loop
│   │   ├── prompts.py                # System prompt (describes all 40+ capabilities)
│   │   ├── tools_registry.py         # Registers all tool schemas for LLM function calling
│   │   └── tools/
│   │       ├── account_tools.py      # Account balances, positions, transactions
│   │       ├── quote_tools.py        # Real-time quotes, option chains
│   │       ├── history_tools.py      # Price history (OHLCV)
│   │       ├── options_tools.py      # Options chain analysis
│   │       ├── order_tools.py        # Place, preview, cancel, replace orders
│   │       ├── technical_tools.py    # TA-Lib indicators (RSI, MACD, BB, ATR, etc.)
│   │       ├── streaming_tools.py    # Start/stop WebSocket streaming
│   │       ├── position_tools.py     # LLM-managed position monitoring
│   │       ├── economic_tools.py     # Alpha Vantage macro data (GDP, CPI, rates, etc.)
│   │       └── fundamental_tools.py  # Alpha Vantage fundamentals (financials, earnings, IPO)
│   ├── alphavantage/
│   │   └── client.py                 # Alpha Vantage API client
│   ├── auth/
│   │   ├── service.py                # JWT creation/validation, bcrypt hashing
│   │   └── schwab_oauth.py           # Schwab OAuth2 flow + token exchange
│   └── schwab/
│       ├── client.py                 # Base Schwab HTTP client (auth headers, retries)
│       ├── accounts.py               # Account balances, positions
│       ├── quotes.py                 # Real-time quotes
│       ├── price_history.py          # OHLCV history
│       ├── options_chain.py          # Options chain
│       ├── orders.py                 # Order management
│       ├── transactions.py           # Transaction history
│       ├── instruments.py            # Symbol search
│       ├── market_hours.py           # Market hours
│       ├── movers.py                 # Market movers
│       ├── user_preferences.py       # User preferences
│       └── streaming/
│           ├── client.py             # WebSocket streaming client
│           ├── level_one.py          # Level 1 quotes stream
│           ├── chart.py              # Chart data stream
│           ├── book.py               # Order book stream
│           ├── screener.py           # Screener stream
│           ├── account_activity.py   # Account activity stream
│           └── fields.py             # Field definitions
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/index.js           # Vue Router (Login, Onboarding, OAuth, Terminal, Dashboard)
        ├── stores/
        │   ├── auth.js               # Auth state (login, signup, JWT)
        │   ├── ai.js                 # AI chat state + WebSocket
        │   ├── market.js             # Market data state
        │   ├── portfolio.js          # Portfolio state
        │   ├── panels.js             # Terminal panel layout
        │   ├── config.js             # User config
        │   └── risk.js               # Risk dashboard state
        ├── views/
        │   ├── LoginView.vue         # Sign up / sign in
        │   ├── OnboardingView.vue    # Schwab credentials + OAuth wizard
        │   ├── OAuthCallbackView.vue # Schwab OAuth success/error
        │   ├── TradingDashboard.vue  # Main Bloomberg terminal
        │   └── TerminalView.vue      # Terminal view
        └── components/
            └── terminal/
                ├── SidePanel.vue     # Side panel (portfolio, options, etc.)
                ├── PromptLibrary.vue # Pre-screened prompt cards
                ├── ConfigDashboard.vue
                └── RiskDashboard.vue
```

---

## Environment Variables

The app reads from environment variables (set in `.env` on the host, passed via `docker-compose.yml`):

```env
# Database (auto-set by docker-compose)
DATABASE_URL=postgresql://llmtrader:<DB_PASSWORD>@postgres:5432/llmtrader
DB_PASSWORD=your_secure_db_password

# Auth
JWT_SECRET=your_jwt_secret_min_32_chars

# Schwab credential encryption (Fernet key)
ENCRYPTION_KEY=your_fernet_key_base64

# Domain
DOMAIN=volflowagent.com

# Alpha Vantage (macroeconomic + fundamental data)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# LLM API Keys (stored per-user in DB, but can be set globally)
ANTHROPIC_API_KEY=your_anthropic_key
XAI_API_KEY=your_xai_key
GOOGLE_API_KEY=your_google_key
```

Generate keys:
```bash
# Fernet encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Docker Architecture

The app runs as **two Docker containers** managed by `docker-compose`:

### Container 1: `llmtrader-db` (postgres:16-alpine)
- PostgreSQL database
- Data persisted in named volume `postgres_data`
- Healthcheck: `pg_isready -U llmtrader`

### Container 2: `llmtrader-app` (custom image)
Built from `Dockerfile` in two stages:
1. **Stage 1 (node:18):** Builds Vue 3 frontend → `/app/frontend/dist`
2. **Stage 2 (python:3.11-slim):** Installs Python deps, copies built frontend + backend

Inside the container, **Supervisor** manages 3 processes:
| Process | Command | Port |
|---------|---------|------|
| `nginx` | `/usr/sbin/nginx -g 'daemon off;'` | 80, 443 |
| `uvicorn` | `uvicorn backend.server:app --host 127.0.0.1 --port 8000 --workers 4` | 8000 (internal) |
| `token-refresher` | `python3 /app/backend/token_refresher.py` | — |

**Volume mounts:**
- `/etc/letsencrypt` → `/etc/letsencrypt:ro` (SSL certs from host)

---

## Production Deployment Workflow

### EC2 Instance Details
```
IP:           3.238.51.196
User:         ubuntu
Key file:     llmtrader-key-new.pem  (in project root, NOT committed)
Project dir:  /home/ubuntu/llmtrader
SSH command:  ssh -i llmtrader-key-new.pem ubuntu@3.238.51.196
```

### Standard Deploy (code changes only)

```bash
# 1. On local machine — commit and push
git add -A
git commit -m "your message"
git push origin master

# 2. SSH to EC2
ssh -i llmtrader-key-new.pem ubuntu@3.238.51.196

# 3. Pull latest code
cd /home/ubuntu/llmtrader
git pull origin master

# 4. Rebuild Docker image
docker-compose build

# 5. Remove old app container (required — docker-compose v1.29 bug with ContainerConfig)
docker rm llmtrader-app

# 6. Start new container
docker-compose up -d

# 7. Wait for startup (~15s), then verify
sleep 15 && curl -sk https://volflowagent.com/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### First-Time / Fresh EC2 Setup

```bash
# Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose

# Clone repo
cd /home/ubuntu
git clone https://github.com/ROOK-KNIGHT/LLMtrader.git llmtrader
cd llmtrader

# Create .env file with all required variables
nano .env

# Get SSL certificate (port 80 must be free — stop any running containers first)
sudo certbot certonly --standalone -d volflowagent.com -d www.volflowagent.com \
  --non-interactive --agree-tos -m imart913@gmail.com

# Fix letsencrypt directory permissions so Docker can read certs
sudo chmod 755 /etc/letsencrypt/live /etc/letsencrypt/archive
sudo chmod 644 /etc/letsencrypt/live/volflowagent.com/*.pem
sudo chmod 644 /etc/letsencrypt/archive/volflowagent.com/*.pem

# Build and start
docker-compose build
docker-compose up -d
```

### Useful EC2 Commands

```bash
# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}"

# View live logs
docker logs llmtrader-app -f

# View last 50 lines of logs
docker logs llmtrader-app --tail 50

# Restart just the app container
docker restart llmtrader-app

# Get a shell inside the container
docker exec -it llmtrader-app bash

# Check nginx config inside container
docker exec llmtrader-app nginx -t

# Reload nginx inside container (after config change)
docker exec llmtrader-app nginx -s reload

# Connect to PostgreSQL
docker exec -it llmtrader-db psql -U llmtrader -d llmtrader

# Check health endpoint
curl -sk https://volflowagent.com/health
```

---

## Known Issues & Gotchas

### 1. `docker-compose` vs `docker compose`
The EC2 has **docker-compose v1.29** (Python-based, installed via apt). Use `docker-compose` (hyphenated), NOT `docker compose` (plugin syntax).

### 2. `ContainerConfig` KeyError on `docker-compose up`
When rebuilding the image and running `docker-compose up -d`, you may get:
```
KeyError: 'ContainerConfig'
```
This is a known bug in docker-compose v1.29 with newer Docker Engine. **Fix:** manually remove the old container first:
```bash
docker rm llmtrader-app
docker-compose up -d
```

### 3. SSL Certificates — Permissions
Let's Encrypt certs are owned by root with restricted permissions. The Docker container runs as root but the mounted `/etc/letsencrypt` directory may not be readable. Fix:
```bash
sudo chmod 755 /etc/letsencrypt/live /etc/letsencrypt/archive
sudo chmod 644 /etc/letsencrypt/archive/volflowagent.com/*.pem
```

### 4. nginx SSL Cert Paths
The `nginx.conf` uses absolute paths:
```
ssl_certificate /etc/letsencrypt/live/volflowagent.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/volflowagent.com/privkey.pem;
```
These paths are correct and match the volume mount. Do NOT change them to relative paths.

### 5. Alpha Vantage Rate Limits
The free Alpha Vantage tier allows 25 requests/day and 5 requests/minute. The `ALPHA_VANTAGE_API_KEY` env var must be set in `.env` on the EC2 host. If missing, economic/fundamental tools will return errors but the rest of the app works fine.

---

## API Endpoints

All routes are prefixed with `/api/`:

**Auth:**
- `POST /api/auth/signup` — Create account (email, password, display_name)
- `POST /api/auth/login` — Sign in → returns JWT
- `GET /api/auth/me` — Get current user (requires `Authorization: Bearer <token>`)

**Schwab:**
- `POST /api/schwab/credentials` — Save Schwab app_key + app_secret (encrypted)
- `GET /api/schwab/auth-url` — Get Schwab OAuth URL
- `GET /api/schwab/callback` — OAuth callback (Schwab redirects here)
- `GET /api/schwab/status` — Check if Schwab is connected

**AI:**
- `POST /api/ai/chat` — Send message to LLM (triggers tool calls)
- `GET /api/ai/models` — List available LLM models
- `WebSocket /ws/ai` — Real-time AI streaming

**Health:**
- `GET /health` — Health check (used by Docker healthcheck + monitoring)

---

## AI Tools Registry

The LLM has access to **40+ tools** across 10 categories. All tools are defined in `backend/ai/tools_registry.py` and implemented in `backend/ai/tools/`:

| Category | Tools |
|----------|-------|
| **Account** | get_account_summary, get_positions, get_transactions, get_account_numbers |
| **Quotes** | get_quote, get_quotes_batch, search_instruments |
| **Price History** | get_price_history, get_intraday_history |
| **Options** | get_options_chain, analyze_options_chain |
| **Orders** | preview_order, place_order, cancel_order, replace_order, get_orders |
| **Technical** | calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_vwap, get_technical_summary |
| **Streaming** | start_quote_stream, start_chart_stream, stop_stream, get_stream_status |
| **Positions** | add_managed_position, update_position_triggers, get_managed_positions, close_managed_position |
| **Economic** | get_real_gdp, get_cpi, get_fed_funds_rate, get_treasury_yield, get_unemployment, get_nonfarm_payroll, get_retail_sales, get_durable_goods |
| **Fundamental** | get_company_overview, get_income_statement, get_balance_sheet, get_cash_flow, get_earnings, get_ipo_calendar, get_earnings_calendar |

---

## Database Schema

Key tables in PostgreSQL (`llmtrader` database):

```sql
-- Users
users (id, email, password_hash, display_name, created_at, last_login)

-- Schwab credentials (per user, encrypted)
schwab_credentials (id, user_id, app_key, app_secret_encrypted)

-- Schwab OAuth tokens (per user, encrypted)
schwab_tokens (id, user_id, access_token_encrypted, refresh_token_encrypted, expires_at)

-- AI API keys (per user)
ai_api_keys (id, user_id, provider, api_key_encrypted)

-- LLM-managed positions
managed_positions (id, user_id, symbol, strategy, thesis, triggers, status, pnl, ...)

-- Conversation history
conversation_history (id, user_id, role, content, model, created_at)
```

---

## Local Development

```bash
# Backend
cd backend
pip3 install -r requirements.txt
# Set env vars in .env
python3 server.py
# → https://127.0.0.1:8000

# Frontend
cd frontend
npm install
npm run dev
# → http://localhost:5173

# API docs (FastAPI auto-generated)
# → https://127.0.0.1:8000/docs
```

---

## License

Proprietary — All Rights Reserved

---

## Contact

Isaac Martinez — imart913@gmail.com
