# LLMtrader.com Setup Guide

Complete authentication and Schwab OAuth integration for LLMtrader.com.

## 🎯 What's Been Built

### Backend (Python/FastAPI)
- ✅ **database.py** - PostgreSQL schema with connection pooling
- ✅ **auth/service.py** - JWT tokens + bcrypt password hashing
- ✅ **auth/schwab_oauth.py** - Schwab OAuth 2.0 flow
- ✅ **server.py** - FastAPI with 8 auth/Schwab routes

### Frontend (Vue 3)
- ✅ **LoginView.vue** - Sign up/sign in with email + password
- ✅ **OnboardingView.vue** - 2-step Schwab credentials + OAuth
- ✅ **OAuthCallbackView.vue** - Success/error handling
- ✅ **stores/auth.js** - Real API calls with axios

---

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
# Backend
cd backend
pip3 install -r requirements.txt

# Frontend (if not already done)
cd ../frontend
npm install
```

### 2. Setup PostgreSQL Database

```bash
# Create database
createdb llmtrader

# Or using psql
psql -U postgres
CREATE DATABASE llmtrader;
\q
```

### 3. Generate Encryption Keys

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Fernet encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Create .env File

```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

Example `.env`:
```env
DATABASE_URL=postgresql://localhost:5432/llmtrader
JWT_SECRET=<your-generated-jwt-secret>
ENCRYPTION_KEY=<your-generated-fernet-key>
HOST=127.0.0.1
PORT=8000
```

### 5. Generate Self-Signed SSL Certificates

Schwab requires HTTPS for OAuth callbacks. Generate self-signed certs for local development:

```bash
cd backend
mkdir -p ssl

# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -days 365 \
  -subj "/CN=127.0.0.1"
```

### 6. Initialize Database Tables

```bash
cd backend
python3 database.py
```

You should see: `✅ Database tables created successfully`

### 7. Register Schwab Developer App

1. Go to https://developer.schwab.com
2. Create a new app
3. Set callback URL to: `https://127.0.0.1:8000/api/schwab/callback`
4. Save your **App Key** and **App Secret**

---

## 🚀 Running the Application

### Terminal 1: Backend Server

```bash
cd backend
python3 server.py
```

Server will start at: `https://127.0.0.1:8000`

**Note:** Your browser will warn about the self-signed certificate. Click "Advanced" → "Proceed to 127.0.0.1" to accept it.

### Terminal 2: Frontend Dev Server

```bash
cd frontend
npm run dev
```

Frontend will start at: `http://localhost:5173`

---

## 🔄 Complete User Flow

### 1. Sign Up
- Visit `http://localhost:5173`
- Click "Sign Up" tab
- Enter email, display name, password
- Click "Create Account"
- → Redirected to `/onboarding`

### 2. Connect Schwab (Onboarding)
- **Step 1:** Enter Schwab App Key + App Secret
- Click "Save Credentials"
- **Step 2:** Click "Connect Schwab Account"
- → Redirected to Schwab login page

### 3. Schwab Authorization
- Log into your Schwab account
- Authorize the app
- → Schwab redirects to `https://127.0.0.1:8000/api/schwab/callback?code=XXX&state=USER_ID`

### 4. Backend Token Exchange
- Backend exchanges auth code for tokens
- Tokens saved to PostgreSQL
- → Backend redirects to `http://localhost:5173/oauth/success`

### 5. Success Page
- Shows "Successfully Connected!"
- Auto-redirects to `/terminal` after 2 seconds

---

## 🗄️ Database Schema

### Tables Created:
- **users** - User accounts (email, password_hash, display_name)
- **schwab_credentials** - Schwab app_key + encrypted app_secret
- **schwab_tokens** - Access/refresh tokens with expiry
- **ai_api_keys** - API keys for Claude/Grok/Gemini
- **managed_positions** - LLM-monitored positions
- **conversation_history** - AI chat history

---

## 🔐 Security Features

- ✅ **bcrypt** password hashing (12 rounds)
- ✅ **JWT** tokens (24hr expiry)
- ✅ **Fernet encryption** for Schwab app_secret
- ✅ **HTTPS** for OAuth (self-signed cert for dev)
- ✅ **CORS** protection
- ✅ **State parameter** in OAuth for CSRF protection

---

## 🧪 Testing the API

FastAPI auto-generates interactive docs:

**Visit:** `https://127.0.0.1:8000/docs`

### Available Endpoints:

**Auth:**
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Sign in
- `GET /api/auth/me` - Get current user (requires JWT)

**Schwab:**
- `POST /api/schwab/credentials` - Save app_key/secret
- `GET /api/schwab/auth-url` - Get OAuth URL
- `GET /api/schwab/callback` - OAuth callback (backend handles)
- `GET /api/schwab/status` - Check connection status

**Health:**
- `GET /health` - Health check

---

## 🐛 Troubleshooting

### "Connection refused" on backend
- Make sure PostgreSQL is running: `brew services start postgresql` (macOS)
- Check database exists: `psql -l | grep llmtrader`

### "SSL certificate error" in browser
- This is expected with self-signed certs
- Click "Advanced" → "Proceed to 127.0.0.1"
- Or add cert to system keychain (macOS): `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain backend/ssl/cert.pem`

### "CORS error" in frontend
- Make sure backend is running on `https://127.0.0.1:8000`
- Check CORS origins in `server.py` include `http://localhost:5173`

### OAuth redirect fails
- Verify callback URL in Schwab Developer Portal matches: `https://127.0.0.1:8000/api/schwab/callback`
- Check backend logs for token exchange errors

---

## 📦 Next Steps

Now that auth is complete, you can:

1. **Add AI chat endpoint** - `POST /api/chat` with LLM integration
2. **Add WebSocket streaming** - `/ws/stream` for real-time data
3. **Wire up Schwab API tools** - Connect `backend/schwab/` to AI tools
4. **Add portfolio endpoints** - Fetch positions, orders, account data
5. **Build news/sentiment module** - Port from VolFlow

---

## 🎉 You're Ready!

The complete authentication and Schwab OAuth flow is now functional. Users can:
- ✅ Sign up with email/password
- ✅ Save Schwab credentials (encrypted)
- ✅ Complete OAuth flow
- ✅ Get JWT tokens for API access
- ✅ Access protected routes

**Start the servers and test the full flow!**
