# LLM VolFlow Trader

**AI-Powered Portfolio Management & Swing Trading Platform**

Domain: `llmvolflowtrader.com`

---

## Overview

LLM VolFlow Trader is a next-generation trading platform that combines institutional-grade market analysis with AI-powered decision making. Unlike traditional algorithmic trading systems, this platform uses Large Language Models (Claude, Grok, Gemini) to analyze market conditions, manage positions, and execute trades through the Schwab API.

### Key Features

- **Google SSO Authentication** - Secure sign-in with Google accounts only
- **SMS 2FA via AWS SNS** - Two-factor authentication on every login
- **User-Provided Schwab API Keys** - Full encryption at rest with Fernet
- **LLM-Powered Trading** - AI models analyze markets and execute trades
- **Pre-Screened Prompt Library** - 20+ institutional-grade trading strategies
- **Real-Time Position Monitoring** - WebSocket streaming with trigger-based reviews
- **Bloomberg Terminal UI** - Professional dark-theme interface
- **TradingView Charts** - Lightweight charts for technical analysis
- **TA-Lib Integration** - On-demand technical indicators
- **Multi-Tenant Architecture** - Fully isolated per-user credentials

---

## Architecture

### Tech Stack

**Backend:**
- Python 3.11+
- PostgreSQL (user data, positions, market data)
- FastAPI (HTTP + WebSocket server)
- Schwab API (OAuth2, REST, WebSocket streaming)
- AWS SNS (SMS verification)
- Fernet encryption (credential storage)

**Frontend:**
- Vanilla JavaScript (ES6+)
- TradingView Lightweight Charts
- WebSocket client (real-time data)
- Bloomberg-inspired dark theme

**AI/LLM:**
- Claude Sonnet 4.6 (Anthropic)
- Grok 4.1 Fast Reasoning (xAI)
- Gemini 3 Pro Preview (Google)
- Single model OR debate mode per request

**Infrastructure:**
- AWS EC2 (c5.xlarge or similar)
- NGINX (reverse proxy, SSL termination)
- systemd (service management)
- Route53 (DNS)
- Let's Encrypt (SSL certificates)

---

## Project Structure

```
LLM_VolFlow_Trader/
├── README.md
├── requirements.txt
├── .env.example
├── server.py                    # Main FastAPI server (HTTP + WebSocket)
├── config/
│   └── settings.py              # Environment config, encryption keys
├── auth/                        # Authentication layer
│   ├── google_sso.py            # Google OAuth2 flow
│   ├── sms_verify.py            # AWS SNS SMS verification
│   ├── credential_manager.py    # Fernet encryption for Schwab keys/tokens
│   ├── session_manager.py       # JWT creation, validation, refresh
│   └── middleware.py            # Auth middleware for HTTP + WebSocket
├── core/                        # Core trading infrastructure
│   ├── schwab_client.py         # Per-user Schwab API client (full endpoint coverage)
│   ├── order_handler.py         # Schwab order execution (per-user)
│   ├── streaming_service.py     # Schwab WebSocket streaming (per-user)
│   └── database_manager.py      # PostgreSQL connection pooling
├── llm/                         # LLM orchestration
│   ├── orchestrator.py          # AI Board (single & debate modes)
│   ├── handler.py               # LLM API calls (Claude/Grok/Gemini)
│   ├── prompts.py               # System prompts & prompt library
│   ├── tools_registry.py        # Expanded tools (per-user context)
│   └── position_monitor.py      # LLM position monitor (ported from VolFlow)
├── indicators/
│   └── talib_engine.py          # TA-Lib wrapper (on-demand indicators)
├── data/                        # Data services
│   ├── sentiment.py             # StockTwits sentiment
│   ├── news.py                  # News headlines
│   ├── regime.py                # Regime chain
│   └── tables.py                # DataTables (ported from VolFlow)
├── websocket/                   # WebSocket server
│   ├── server.py                # WebSocket server
│   ├── ai_handler.py            # AI Board WS handler
│   └── data_stream.py           # Real-time data stream
├── frontend/                    # Frontend files
│   ├── index.html               # Login/Signup page
│   ├── terminal.html            # Main Bloomberg terminal UI
│   ├── oauth-callback.html      # Schwab OAuth callback page
│   ├── css/
│   │   ├── auth.css             # Login/signup styles
│   │   ├── terminal.css         # Bloomberg dark theme
│   │   └── components.css       # Panel/widget styles
│   └── js/
│       ├── auth.js              # Login/signup/OAuth logic
│       ├── app.js               # Main app controller
│       ├── terminal.js          # Chat/command terminal
│       ├── portfolio.js         # Portfolio dashboard
│       ├── charts.js            # TradingView Lightweight Charts
│       ├── options.js           # Options chain viewer
│       └── ws-client.js         # WebSocket client (auth'd)
├── deployment/
│   ├── nginx.conf               # NGINX configuration
│   ├── llmvolflowtrader.service # systemd service file
│   └── setup.sh                 # EC2 setup script
└── tests/
    └── ...
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id TEXT UNIQUE NOT NULL,           -- Google sub (unique identifier)
    email TEXT UNIQUE NOT NULL,               -- From Google
    display_name TEXT,                        -- From Google
    avatar_url TEXT,                          -- From Google
    phone_number TEXT,                        -- For SMS verification
    phone_verified BOOLEAN DEFAULT false,
    schwab_app_key_encrypted TEXT,            -- Fernet encrypted (user provides)
    schwab_app_secret_encrypted TEXT,         -- Fernet encrypted (user provides)
    schwab_access_token_encrypted TEXT,       -- Fernet encrypted (from OAuth)
    schwab_refresh_token_encrypted TEXT,      -- Fernet encrypted (from OAuth)
    schwab_token_expires_at TIMESTAMP,
    schwab_account_hash TEXT,
    schwab_connected BOOLEAN DEFAULT false,   -- true after successful OAuth
    onboarding_complete BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE sms_verification_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    phone_number TEXT NOT NULL,
    code TEXT NOT NULL,                       -- 6-digit code (hashed)
    expires_at TIMESTAMP NOT NULL,           -- 5 min expiry
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token TEXT UNIQUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id UUID,
    model TEXT,
    prompt TEXT,
    response TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE llm_managed_positions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol TEXT NOT NULL,
    option_symbol TEXT,
    underlying_symbol TEXT,
    contracts INTEGER DEFAULT 1,
    entry_price FLOAT,
    current_price FLOAT,
    strategy_name TEXT,
    trade_thesis TEXT,
    triggers JSONB DEFAULT '[]',
    review_log JSONB DEFAULT '[]',
    review_cooldown_minutes INTEGER DEFAULT 10,
    last_reviewed_at TIMESTAMP,
    status TEXT DEFAULT 'ACTIVE',
    closed_at TIMESTAMP,
    close_price FLOAT,
    close_reason TEXT,
    pnl FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Authentication Flow

1. **User visits llmvolflowtrader.com** → "Sign in with Google" button (ONLY option)
2. **Google SSO (OAuth2):**
   - Redirect to Google → User signs in with Google account
   - Google redirects back with auth code → We get their email, name, avatar
   - User record created/found in our DB
3. **SMS Verification (EVERY sign-in):**
   - After Google SSO completes, prompt for phone number (first time) or use stored number
   - Send 6-digit code via AWS SNS
   - User enters code → Verified → JWT session issued
4. **Schwab API Key Setup (first time only, or if not yet configured):**
   - After verified sign-in, check if user has Schwab keys stored
   - If NO keys → Show onboarding wizard with step-by-step guide
   - User provides App Key + Secret → Encrypted with Fernet → Stored in DB
   - Trigger Schwab OAuth flow → Get access/refresh tokens → Encrypted + stored
5. **User is now fully authenticated:**
   - ✅ Google identity verified
   - ✅ Phone number verified via SMS
   - ✅ Schwab API keys encrypted in DB
   - ✅ Schwab OAuth tokens encrypted in DB
   - → Redirect to Bloomberg terminal dashboard

---

## Pre-Screened Prompt Library

Users can select from 20+ institutional-grade prompts that auto-execute trades:

### Categories

1. **🔥 Quick Plays** - Fast-action trade ideas for today
2. **🔬 Volatility & Options** - Options mispricing and volatility edge
3. **📊 Swing Trade Setups** - Multi-day technical setups with defined risk
4. **🌍 Macro & Thematic** - Sector rotation and macro-driven trades
5. **🛡️ Portfolio Management** - Hedge, rebalance, and manage risk

Each prompt:
- Has `auto_execute: true/false` flag
- Includes risk level (limited/moderate)
- Specifies timeframe (15min-4hrs, 1-3 weeks, etc.)
- Provides clear description for users

---

## Deployment

### EC2 Instance Requirements

- **Instance Type:** c5.xlarge or c6i.xlarge
- **OS:** Amazon Linux 2 or Ubuntu 22.04
- **Storage:** 50GB+ SSD
- **Security Group:** Ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL - internal only)

### Setup Steps

1. **Provision EC2 instance**
2. **Install dependencies:**
   ```bash
   sudo yum update -y
   sudo yum install python3.11 postgresql15 nginx git -y
   ```
3. **Clone repository:**
   ```bash
   git clone https://github.com/YOUR_ORG/LLM_VolFlow_Trader.git
   cd LLM_VolFlow_Trader
   ```
4. **Install Python dependencies:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```
6. **Setup PostgreSQL database**
7. **Configure NGINX** (see `deployment/nginx.conf`)
8. **Setup systemd service** (see `deployment/llmvolflowtrader.service`)
9. **Obtain SSL certificate** (Let's Encrypt)
10. **Start services:**
    ```bash
    sudo systemctl start llmvolflowtrader
    sudo systemctl enable llmvolflowtrader
    sudo systemctl restart nginx
    ```

---

## Development Roadmap

### Phase 1: Project Scaffolding + Auth System ✅
- [x] Project structure
- [ ] Google SSO integration
- [ ] AWS SNS SMS verification
- [ ] JWT session management
- [ ] Fernet credential encryption
- [ ] Schwab onboarding wizard

### Phase 2: Per-User Schwab API Client
- [ ] Full Schwab REST API client (all endpoints)
- [ ] Schwab OAuth2 flow
- [ ] Token auto-refresh service
- [ ] Per-user client isolation

### Phase 3: LLM Orchestrator + Tools Registry
- [ ] Port LLM handler from VolFlow
- [ ] Expand tools registry (all Schwab endpoints)
- [ ] TA-Lib indicator engine
- [ ] Pre-screened prompt library
- [ ] Single & debate modes

### Phase 4: Bloomberg Terminal UI
- [ ] Dark theme CSS
- [ ] TradingView Lightweight Charts integration
- [ ] Portfolio dashboard
- [ ] Options chain viewer
- [ ] Chat/command terminal
- [ ] Prompt card selector

### Phase 5: Background Services
- [ ] LLM position monitor (per-user)
- [ ] Schwab streaming (per-user)
- [ ] Sentiment & news daemons
- [ ] PostgreSQL LISTEN/NOTIFY pipeline

### Phase 6: EC2 Deployment
- [ ] EC2 instance provisioning
- [ ] Domain + SSL + NGINX
- [ ] systemd services
- [ ] Monitoring & logging

---

## License

Proprietary - All Rights Reserved

---

## Contact

For questions or support, contact: [Your Email]
