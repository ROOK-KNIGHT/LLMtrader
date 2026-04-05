<template>
  <div class="landing">

    <!-- ── NAV ─────────────────────────────────────────────────────────────── -->
    <nav class="nav">
      <div class="nav-inner">
        <div class="nav-logo">
          <img src="/logo.svg" alt="VolFlow Agent" class="nav-logo-img" />
        </div>
        <div class="nav-links">
          <a href="#features" class="nav-link">Features</a>
          <a href="#how" class="nav-link">How It Works</a>
          <a href="#edge" class="nav-link">The Edge</a>
          <router-link to="/login" class="nav-cta">Launch Platform</router-link>
        </div>
        <!-- Hamburger (mobile only) -->
        <button class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen" :class="{ open: mobileMenuOpen }" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </div>
      <!-- Mobile dropdown menu -->
      <div class="mobile-menu" :class="{ open: mobileMenuOpen }">
        <a href="#features" class="mobile-link" @click="mobileMenuOpen = false">Features</a>
        <a href="#how" class="mobile-link" @click="mobileMenuOpen = false">How It Works</a>
        <a href="#edge" class="mobile-link" @click="mobileMenuOpen = false">The Edge</a>
        <router-link to="/login" class="mobile-cta" @click="mobileMenuOpen = false">Launch Platform</router-link>
      </div>
    </nav>

    <!-- ── HERO ────────────────────────────────────────────────────────────── -->
    <section class="hero">
      <div class="hero-grid-bg"></div>
      <div class="hero-scan-line"></div>

      <div class="hero-inner">
        <div class="hero-badge">INSTITUTIONAL-GRADE AI TRADING</div>

        <h1 class="hero-title">
          Your Portfolio.<br />
          <span class="hero-title-accent">Managed by AI.</span><br />
          Executed with Precision.
        </h1>

        <p class="hero-sub">
          VolFlow Agent connects directly to your Schwab account and deploys an AI portfolio manager
          that knows your goals, risk tolerance, and trading style — then acts on them in real time.
        </p>

        <div class="hero-actions">
          <router-link to="/login" class="btn-hero-primary">Get Started Free</router-link>
          <a href="#how" class="btn-hero-secondary">See How It Works</a>
        </div>

        <!-- Live ticker strip -->
        <div class="ticker-strip">
          <div class="ticker-inner">
            <span class="ticker-item"><span class="ticker-sym">SPY</span> <span class="ticker-up">+1.24%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">QQQ</span> <span class="ticker-up">+1.87%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">NVDA</span> <span class="ticker-up">+3.41%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">AAPL</span> <span class="ticker-down">-0.32%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">TSLA</span> <span class="ticker-up">+2.15%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">VIX</span> <span class="ticker-down">-4.20%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">GLD</span> <span class="ticker-up">+0.88%</span></span>
            <span class="ticker-sep">|</span>
            <span class="ticker-item"><span class="ticker-sym">BTC</span> <span class="ticker-up">+5.62%</span></span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── STATS BAR ───────────────────────────────────────────────────────── -->
    <section class="stats-bar">
      <div class="stats-inner">
        <div class="stat">
          <div class="stat-num">40+</div>
          <div class="stat-label">Live Trading Tools</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <div class="stat-num">3</div>
          <div class="stat-label">AI Models (Claude · Grok · Gemini)</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <div class="stat-num">Real-Time</div>
          <div class="stat-label">Schwab Market Data</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <div class="stat-num">24/7</div>
          <div class="stat-label">Position Monitoring</div>
        </div>
      </div>
    </section>

    <!-- ── FEATURES ────────────────────────────────────────────────────────── -->
    <section class="section" id="features">
      <div class="section-inner">
        <div class="section-label">CAPABILITIES</div>
        <h2 class="section-title">Everything a Desk Trader Has.<br />Now in Your Hands.</h2>

        <div class="features-grid">

          <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">AI Portfolio Manager</div>
            <div class="feature-desc">
              Describe your goals once. The AI learns your risk tolerance, time horizons, and trading style — then tailors every recommendation to your personal Investment Policy Statement.
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Live Order Execution</div>
            <div class="feature-desc">
              Preview, place, and cancel orders directly through Schwab. Every order is validated for buying power, commissions, and risk before execution. No surprises.
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Options Intelligence</div>
            <div class="feature-desc">
              Full options chain analysis with Greeks, IV rank, and expiration chains. The AI selects strikes, structures spreads, and monitors theta decay in real time.
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Technical Analysis Engine</div>
            <div class="feature-desc">
              RSI, MACD, Bollinger Bands, ATR, VWAP, and 30+ more indicators computed on live price history. The AI reads the tape so you don't have to.
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Position Monitoring</div>
            <div class="feature-desc">
              Register positions with profit targets and stop triggers. The AI reviews them continuously and alerts you when action is required — with a clear recommendation.
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">◈</div>
            <div class="feature-title">Macro & Fundamentals</div>
            <div class="feature-desc">
              GDP, CPI, Fed Funds Rate, earnings, income statements, and balance sheets — all accessible in a single conversation. Context that moves markets, at your fingertips.
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── HOW IT WORKS ────────────────────────────────────────────────────── -->
    <section class="section section-dark" id="how">
      <div class="section-inner">
        <div class="section-label">PROCESS</div>
        <h2 class="section-title">From Setup to Live Trading<br />in Under 10 Minutes.</h2>

        <div class="steps">
          <div class="step">
            <div class="step-num">01</div>
            <div class="step-content">
              <div class="step-title">Connect Your Schwab Account</div>
              <div class="step-desc">Securely link your Schwab brokerage via OAuth. Your credentials are encrypted and never stored in plain text. Full institutional-grade security.</div>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step">
            <div class="step-num">02</div>
            <div class="step-content">
              <div class="step-title">Build Your Investment Profile</div>
              <div class="step-desc">Answer 13 questions about your goals, risk tolerance, and trading style. The AI summarizes your answers into a personalized Investment Policy Statement injected into every session.</div>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step">
            <div class="step-num">03</div>
            <div class="step-content">
              <div class="step-title">Trade with Your AI Advisor</div>
              <div class="step-desc">Open the terminal and start a conversation. Ask for trade ideas, analyze positions, execute orders, or monitor your portfolio — all in natural language.</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── THE EDGE ────────────────────────────────────────────────────────── -->
    <section class="section" id="edge">
      <div class="section-inner">
        <div class="section-label">THE EDGE</div>
        <h2 class="section-title">Not a Chatbot.<br />A Trading Desk.</h2>

        <div class="edge-grid">
          <div class="edge-col">
            <div class="edge-item">
              <div class="edge-check">✓</div>
              <div>Personalized to your exact goals and risk profile</div>
            </div>
            <div class="edge-item">
              <div class="edge-check">✓</div>
              <div>Pulls live market data before every recommendation</div>
            </div>
            <div class="edge-item">
              <div class="edge-check">✓</div>
              <div>Previews every order before execution — no blind trades</div>
            </div>
            <div class="edge-item">
              <div class="edge-check">✓</div>
              <div>Monitors positions 24/7 with trigger-based alerts</div>
            </div>
            <div class="edge-item">
              <div class="edge-check">✓</div>
              <div>Renders charts, tables, and payoff diagrams inline</div>
            </div>
            <div class="edge-item">
              <div class="edge-check">✓</div>
              <div>Supports Claude, Grok, and Gemini — you choose the model</div>
            </div>
          </div>

          <div class="terminal-preview">
            <div class="tp-header">
              <span class="tp-dot tp-red"></span>
              <span class="tp-dot tp-yellow"></span>
              <span class="tp-dot tp-green"></span>
              <span class="tp-title">VOLFLOW AGENT — TERMINAL</span>
            </div>
            <div class="tp-body">
              <div class="tp-line tp-user">&gt; Analyze NVDA and give me a swing trade setup</div>
              <div class="tp-line tp-ai">Pulling NVDA price history and options chain...</div>
              <div class="tp-line tp-ai">NVDA is trading at $875.40, up 3.4% today on above-average volume.</div>
              <div class="tp-line tp-ai">RSI(14) = 62 — momentum building, not yet overbought.</div>
              <div class="tp-line tp-ai">Key resistance at $890. A close above opens $920 target.</div>
              <div class="tp-line tp-ai">Setup: Buy the $880/$900 call spread expiring in 14 days.</div>
              <div class="tp-line tp-ai">Max risk: $340 | Max reward: $1,660 | Risk/Reward: 4.9:1</div>
              <div class="tp-line tp-ai">Shall I preview the order?</div>
              <div class="tp-line tp-user tp-blink">&gt; <span class="cursor">|</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ─────────────────────────────────────────────────────────────── -->
    <section class="cta-section">
      <div class="cta-inner">
        <div class="cta-label">GET STARTED TODAY</div>
        <h2 class="cta-title">Your AI Trading Desk<br />Is Ready.</h2>
        <p class="cta-sub">Connect your Schwab account, build your investment profile, and start trading with institutional-grade AI in minutes.</p>
        <router-link to="/login" class="btn-hero-primary btn-cta">Launch VolFlow Agent</router-link>
      </div>
    </section>

    <!-- ── FOOTER ──────────────────────────────────────────────────────────── -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-logo">VOLFLOW<span class="nav-logo-accent">AGENT</span></div>
        <div class="footer-note">AI-Powered Portfolio Management · Powered by Schwab API</div>
        <div class="footer-disclaimer">
          VolFlow Agent is a trading tool, not a registered investment advisor. All trading involves risk.
          Past performance does not guarantee future results. Use at your own discretion.
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref } from 'vue'
const mobileMenuOpen = ref(false)
</script>

<style scoped>
/* ── Base ─────────────────────────────────────────────────────────────────── */
.landing {
  background: #080808;
  color: #e8e8e8;
  font-family: 'DaggerSquare', 'Inter', 'Helvetica Neue', Arial, sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── Nav ──────────────────────────────────────────────────────────────────── */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(8, 8, 8, 0.92);
  border-bottom: 1px solid rgba(255, 149, 0, 0.15);
  backdrop-filter: blur(12px);
}
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.nav-logo {
  display: flex;
  align-items: center;
}
.nav-logo-img {
  height: 36px;
  width: auto;
  filter: drop-shadow(0 0 8px rgba(255, 149, 0, 0.4));
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}
.nav-link {
  color: #999;
  text-decoration: none;
  font-size: 0.875rem;
  letter-spacing: 0.05em;
  transition: color 0.2s;
}
.nav-link:hover { color: #fff; }
.nav-cta {
  background: #ff9500;
  color: #000;
  padding: 0.5rem 1.25rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  transition: box-shadow 0.2s;
}
.nav-cta:hover { box-shadow: 0 0 20px rgba(255, 149, 0, 0.5); }

/* ── Hero ─────────────────────────────────────────────────────────────────── */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
  padding-top: 80px;
}
.hero-grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 149, 0, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 149, 0, 0.04) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
}
.hero-scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 149, 0, 0.6), transparent);
  animation: scan 6s linear infinite;
  pointer-events: none;
}
@keyframes scan {
  0%   { top: 0; opacity: 1; }
  90%  { opacity: 0.3; }
  100% { top: 100%; opacity: 0; }
}
.hero-inner {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
  text-align: center;
}
.hero-badge {
  display: inline-block;
  border: 1px solid rgba(255, 149, 0, 0.5);
  color: #ff9500;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  padding: 0.4rem 1rem;
  border-radius: 2px;
  margin-bottom: 2rem;
  background: rgba(255, 149, 0, 0.05);
}
.hero-title {
  font-size: clamp(2.5rem, 6vw, 5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: #fff;
  margin-bottom: 1.5rem;
}
.hero-title-accent {
  color: #ff9500;
  text-shadow: 0 0 40px rgba(255, 149, 0, 0.4);
}
.hero-sub {
  font-size: clamp(1rem, 2vw, 1.2rem);
  color: #888;
  max-width: 680px;
  margin: 0 auto 2.5rem;
  line-height: 1.7;
}
.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}
.btn-hero-primary {
  background: #ff9500;
  color: #000;
  padding: 0.85rem 2.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 800;
  font-size: 1rem;
  letter-spacing: 0.08em;
  transition: all 0.2s;
  display: inline-block;
}
.btn-hero-primary:hover {
  box-shadow: 0 0 30px rgba(255, 149, 0, 0.6);
  transform: translateY(-1px);
}
.btn-hero-secondary {
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ccc;
  padding: 0.85rem 2.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  letter-spacing: 0.05em;
  transition: all 0.2s;
  display: inline-block;
}
.btn-hero-secondary:hover {
  border-color: rgba(255, 149, 0, 0.5);
  color: #fff;
}

/* Ticker */
.ticker-strip {
  border-top: 1px solid rgba(255, 149, 0, 0.15);
  border-bottom: 1px solid rgba(255, 149, 0, 0.15);
  padding: 0.75rem 0;
  overflow: hidden;
  background: rgba(255, 149, 0, 0.03);
}
.ticker-inner {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}
.ticker-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-family: 'Courier New', monospace;
}
.ticker-sym { color: #ccc; font-weight: 600; }
.ticker-up  { color: #22c55e; }
.ticker-down{ color: #ef4444; }
.ticker-sep { color: rgba(255, 149, 0, 0.3); }

/* ── Stats Bar ────────────────────────────────────────────────────────────── */
.stats-bar {
  background: rgba(255, 149, 0, 0.04);
  border-top: 1px solid rgba(255, 149, 0, 0.12);
  border-bottom: 1px solid rgba(255, 149, 0, 0.12);
  padding: 2.5rem 2rem;
}
.stats-inner {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  justify-content: space-around;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
}
.stat { text-align: center; }
.stat-num {
  font-size: 2.5rem;
  font-weight: 800;
  color: #ff9500;
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 0.4rem;
}
.stat-label {
  font-size: 0.8rem;
  color: #666;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.stat-divider {
  width: 1px;
  height: 50px;
  background: rgba(255, 149, 0, 0.2);
}

/* ── Sections ─────────────────────────────────────────────────────────────── */
.section {
  padding: 6rem 2rem;
}
.section-dark {
  background: #0d0d0d;
}
.section-inner {
  max-width: 1200px;
  margin: 0 auto;
}
.section-label {
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  color: #ff9500;
  text-transform: uppercase;
  margin-bottom: 1rem;
}
.section-title {
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 800;
  color: #fff;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 3.5rem;
}

/* ── Features Grid ────────────────────────────────────────────────────────── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}
.feature-card {
  background: #111;
  border: 1px solid rgba(255, 149, 0, 0.12);
  border-radius: 8px;
  padding: 2rem;
  transition: all 0.3s;
}
.feature-card:hover {
  border-color: rgba(255, 149, 0, 0.4);
  background: #141414;
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(255, 149, 0, 0.08);
}
.feature-icon {
  font-size: 1.5rem;
  color: #ff9500;
  margin-bottom: 1rem;
  opacity: 0.8;
}
.feature-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.75rem;
  letter-spacing: 0.02em;
}
.feature-desc {
  font-size: 0.9rem;
  color: #777;
  line-height: 1.7;
}

/* ── Steps ────────────────────────────────────────────────────────────────── */
.steps {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.step {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}
.step-num {
  font-size: 3rem;
  font-weight: 800;
  color: #ff9500;
  opacity: 0.3;
  line-height: 1;
  flex-shrink: 0;
  width: 80px;
  text-align: right;
  font-family: 'Courier New', monospace;
}
.step-content {
  padding: 0.5rem 0 2rem;
  border-left: 1px solid rgba(255, 149, 0, 0.2);
  padding-left: 2rem;
  flex: 1;
}
.step-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.5rem;
}
.step-desc {
  font-size: 0.95rem;
  color: #777;
  line-height: 1.7;
  max-width: 600px;
}
.step-connector {
  display: none;
}

/* ── Edge Section ─────────────────────────────────────────────────────────── */
.edge-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}
@media (max-width: 900px) {
  .edge-grid { grid-template-columns: 1fr; }
}
.edge-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.edge-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  font-size: 0.95rem;
  color: #aaa;
  line-height: 1.5;
}
.edge-check {
  color: #ff9500;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Terminal Preview */
.terminal-preview {
  background: #0a0a0a;
  border: 1px solid rgba(255, 149, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 40px rgba(255, 149, 0, 0.1);
}
.tp-header {
  background: #111;
  border-bottom: 1px solid rgba(255, 149, 0, 0.2);
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.tp-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.tp-red    { background: #ef4444; }
.tp-yellow { background: #f59e0b; }
.tp-green  { background: #22c55e; }
.tp-title {
  font-size: 0.75rem;
  color: #555;
  letter-spacing: 0.1em;
  margin-left: 0.5rem;
}
.tp-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.tp-line {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
}
.tp-user { color: #ff9500; }
.tp-ai   { color: #aaa; padding-left: 1rem; }
.cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}

/* ── CTA ──────────────────────────────────────────────────────────────────── */
.cta-section {
  background: linear-gradient(135deg, #0d0d0d 0%, #111008 50%, #0d0d0d 100%);
  border-top: 1px solid rgba(255, 149, 0, 0.15);
  border-bottom: 1px solid rgba(255, 149, 0, 0.15);
  padding: 7rem 2rem;
  text-align: center;
}
.cta-inner { max-width: 700px; margin: 0 auto; }
.cta-label {
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  color: #ff9500;
  text-transform: uppercase;
  margin-bottom: 1rem;
}
.cta-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  color: #fff;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 1.25rem;
}
.cta-sub {
  font-size: 1rem;
  color: #777;
  line-height: 1.7;
  margin-bottom: 2.5rem;
}
.btn-cta {
  font-size: 1.1rem;
  padding: 1rem 3rem;
}

/* ── Footer ───────────────────────────────────────────────────────────────── */
.footer {
  background: #050505;
  padding: 3rem 2rem;
  text-align: center;
}
.footer-inner { max-width: 800px; margin: 0 auto; }
.footer-logo {
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  color: #fff;
  margin-bottom: 0.5rem;
}
.footer-note {
  font-size: 0.8rem;
  color: #555;
  letter-spacing: 0.05em;
  margin-bottom: 1.5rem;
}
.footer-disclaimer {
  font-size: 0.75rem;
  color: #333;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

/* ── Hamburger ────────────────────────────────────────────────────────────── */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 26px;
  height: 18px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 200;
}
.hamburger span {
  display: block;
  width: 100%;
  height: 2px;
  background: #ff9500;
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}
.hamburger.open span:nth-child(1) { transform: translateY(8px) rotate(45deg); }
.hamburger.open span:nth-child(2) { opacity: 0; }
.hamburger.open span:nth-child(3) { transform: translateY(-8px) rotate(-45deg); }

/* ── Mobile Menu ──────────────────────────────────────────────────────────── */
.mobile-menu {
  display: none;
  flex-direction: column;
  background: rgba(8, 8, 8, 0.98);
  border-top: 1px solid rgba(255, 149, 0, 0.15);
  padding: 0;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s ease, padding 0.35s ease;
}
.mobile-menu.open {
  max-height: 400px;
  padding: 1rem 0;
}
.mobile-link {
  display: block;
  padding: 0.85rem 2rem;
  color: #ccc;
  text-decoration: none;
  font-size: 1rem;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255, 149, 0, 0.07);
  transition: color 0.2s, background 0.2s;
}
.mobile-link:hover { color: #fff; background: rgba(255, 149, 0, 0.05); }
.mobile-cta {
  display: block;
  margin: 1rem 2rem 0;
  padding: 0.75rem 1.5rem;
  background: #ff9500;
  color: #000;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  border-radius: 4px;
  text-align: center;
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  /* Nav */
  .nav-links { display: none; }
  .hamburger { display: flex; }
  .mobile-menu { display: flex; }

  /* Hero */
  .hero { min-height: auto; padding-top: 70px; }
  .hero-inner { padding: 3rem 1.25rem 2rem; }
  .hero-badge { font-size: 0.65rem; letter-spacing: 0.12em; }
  .hero-actions { flex-direction: column; align-items: center; }
  .btn-hero-primary, .btn-hero-secondary { width: 100%; max-width: 320px; text-align: center; }
  .ticker-inner { gap: 1rem; }
  .ticker-sep { display: none; }

  /* Stats */
  .stats-bar { padding: 2rem 1.25rem; }
  .stat-divider { display: none; }
  .stats-inner { gap: 1.5rem; }

  /* Sections */
  .section { padding: 4rem 1.25rem; }
  .section-title { margin-bottom: 2rem; }
  .features-grid { grid-template-columns: 1fr; }

  /* Steps */
  .step { flex-direction: column; gap: 0.5rem; }
  .step-num { width: auto; text-align: left; font-size: 2rem; }
  .step-content { border-left: none; padding-left: 0; }

  /* Edge */
  .edge-grid { grid-template-columns: 1fr; gap: 2rem; }
  .tp-body { padding: 1rem; }
  .tp-line { font-size: 0.75rem; }

  /* CTA */
  .cta-section { padding: 4rem 1.25rem; }

  /* Footer */
  .footer { padding: 2rem 1.25rem; }
}
</style>
