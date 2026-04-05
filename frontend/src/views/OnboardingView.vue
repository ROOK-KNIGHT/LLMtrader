<template>
  <div style="width: 100%; min-height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-primary); padding: 2rem 0;">
    <div class="card" style="max-width: 720px; width: 90%;">
      <div class="card-header">
        <h2 class="card-title">
          <span v-if="step === 1">Connect Schwab Account</span>
          <span v-else-if="step === 2">Authorize Access</span>
          <span v-else-if="step === 3">Investment Profile</span>
          <span v-else>Profile Complete</span>
        </h2>
        <!-- Step indicator -->
        <div class="step-indicator">
          <div v-for="s in 4" :key="s" :class="['step-dot', { active: step === s, done: step > s }]"></div>
        </div>
      </div>

      <div class="card-body">
        <!-- Error message -->
        <div v-if="error" class="alert alert-error">
          <p>{{ error }}</p>
        </div>

        <!-- Success message -->
        <div v-if="success && step < 3" class="alert alert-success">
          <p>Credentials saved! Click "Connect Schwab" to authorize.</p>
        </div>

        <!-- ─── STEP 1: Schwab Credentials ─── -->
        <div v-if="step === 1">
          <p class="step-desc">
            To enable live trading, provide your Schwab API credentials from the
            <a href="https://developer.schwab.com" target="_blank" class="link">Schwab Developer Portal</a>.
          </p>
          <form @submit.prevent="saveCredentials">
            <div class="field">
              <label class="field-label">App Key (Client ID)</label>
              <input v-model="appKey" type="text" class="input" placeholder="Your Schwab App Key" required :disabled="isLoading" />
            </div>
            <div class="field">
              <label class="field-label">App Secret (Client Secret)</label>
              <input v-model="appSecret" type="password" class="input" placeholder="Your Schwab App Secret" required :disabled="isLoading" />
            </div>
            <div class="field">
              <label class="field-label">Callback URL</label>
              <input v-model="callbackUrl" type="text" class="input" readonly style="background: var(--bg-secondary);" />
              <p class="field-hint">Add this URL to your Schwab app's redirect URIs</p>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;" :disabled="isLoading">
              {{ isLoading ? 'Saving...' : 'Save Credentials' }}
            </button>
          </form>
        </div>

        <!-- ─── STEP 2: Authorize ─── -->
        <div v-if="step === 2">
          <p class="step-desc">
            Click below to authorize VolFlow to access your Schwab account. You'll be redirected to Schwab's login page.
          </p>
          <button class="btn btn-primary btn-lg" style="width: 100%;" @click="connectSchwab" :disabled="isLoading">
            {{ isLoading ? 'Loading...' : 'Connect Schwab Account' }}
          </button>
          <button class="btn btn-secondary" style="width: 100%; margin-top: 1rem;" @click="step = 1">
            Back to Credentials
          </button>
        </div>

        <!-- ─── STEP 3: Investment Profile Questionnaire ─── -->
        <div v-if="step === 3">
          <p class="step-desc">
            Help your AI advisor understand your goals. These answers will be summarized and used to personalize every recommendation.
            You can update these anytime in Settings.
          </p>

          <div class="questions-container">
            <!-- Q1: Short-Term Goals -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">01</span>
                <div>
                  <div class="question-title">Short-Term Goals <span class="question-horizon">(0–1 Year)</span></div>
                  <div class="question-subtitle">Income targets, specific returns, learning goals, etc.</div>
                </div>
              </div>
              <textarea v-model="answers.short_term_goals.text" class="input textarea" placeholder="e.g. Generate $2k/month through options premiums while building a core equity position..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Low Priority</span>
                <input type="range" min="1" max="10" v-model.number="answers.short_term_goals.slider" class="slider" />
                <span class="slider-label-right">Critical Priority</span>
                <span class="slider-value">{{ answers.short_term_goals.slider }}/10</span>
              </div>
            </div>

            <!-- Q2: Medium-Term Goals -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">02</span>
                <div>
                  <div class="question-title">Medium-Term Goals <span class="question-horizon">(1–5 Years)</span></div>
                  <div class="question-subtitle">Financial milestones, account growth targets, major purchases.</div>
                </div>
              </div>
              <textarea v-model="answers.medium_term_goals.text" class="input textarea" placeholder="e.g. Grow account to $500k, fund a down payment, build a dividend income stream..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Low Priority</span>
                <input type="range" min="1" max="10" v-model.number="answers.medium_term_goals.slider" class="slider" />
                <span class="slider-label-right">Critical Priority</span>
                <span class="slider-value">{{ answers.medium_term_goals.slider }}/10</span>
              </div>
            </div>

            <!-- Q3: Long-Term Goals -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">03</span>
                <div>
                  <div class="question-title">Long-Term Goals <span class="question-horizon">(5+ Years)</span></div>
                  <div class="question-subtitle">Retirement, generational wealth, financial independence.</div>
                </div>
              </div>
              <textarea v-model="answers.long_term_goals.text" class="input textarea" placeholder="e.g. Retire at 55 with $3M portfolio generating $120k/year in passive income..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Low Priority</span>
                <input type="range" min="1" max="10" v-model.number="answers.long_term_goals.slider" class="slider" />
                <span class="slider-label-right">Critical Priority</span>
                <span class="slider-value">{{ answers.long_term_goals.slider }}/10</span>
              </div>
            </div>

            <!-- Q4: Risk Tolerance -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">04</span>
                <div>
                  <div class="question-title">Risk Tolerance</div>
                  <div class="question-subtitle">How do you handle market volatility and drawdowns?</div>
                </div>
              </div>
              <textarea v-model="answers.risk_tolerance.text" class="input textarea" placeholder="e.g. I've been through 2020 and 2022 without panic selling. I can handle 20% drawdowns but get uncomfortable beyond that..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Very Conservative</span>
                <input type="range" min="1" max="10" v-model.number="answers.risk_tolerance.slider" class="slider" />
                <span class="slider-label-right">Very Aggressive</span>
                <span class="slider-value">{{ answers.risk_tolerance.slider }}/10</span>
              </div>
            </div>

            <!-- Q5: Portfolio Concentration -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">05</span>
                <div>
                  <div class="question-title">Portfolio Concentration</div>
                  <div class="question-subtitle">Concentrated high-conviction positions vs. broad diversification?</div>
                </div>
              </div>
              <textarea v-model="answers.portfolio_concentration.text" class="input textarea" placeholder="e.g. I prefer 8-12 high-conviction positions rather than spreading thin across 50+ holdings..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Very Broad (50+ holdings)</span>
                <input type="range" min="1" max="10" v-model.number="answers.portfolio_concentration.slider" class="slider" />
                <span class="slider-label-right">Ultra Concentrated (3-5)</span>
                <span class="slider-value">{{ answers.portfolio_concentration.slider }}/10</span>
              </div>
            </div>

            <!-- Q6: Intra-Day Activity -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">06</span>
                <div>
                  <div class="question-title">Intra-Day Trading Interest</div>
                  <div class="question-subtitle">Day trading for quick cash alongside longer-term holds?</div>
                </div>
              </div>
              <textarea v-model="answers.intraday_activity.text" class="input textarea" placeholder="e.g. Mostly swing trades (2-10 days), but I'll day trade on strong momentum setups a few times a week..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">None (Swing/Position Only)</span>
                <input type="range" min="1" max="10" v-model.number="answers.intraday_activity.slider" class="slider" />
                <span class="slider-label-right">Heavy Intra-Day Focus</span>
                <span class="slider-value">{{ answers.intraday_activity.slider }}/10</span>
              </div>
            </div>

            <!-- Q7: Income vs Growth -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">07</span>
                <div>
                  <div class="question-title">Income vs. Growth Orientation</div>
                  <div class="question-subtitle">Capital appreciation, income generation, or both?</div>
                </div>
              </div>
              <textarea v-model="answers.income_vs_growth.text" class="input textarea" placeholder="e.g. Primarily growth-focused but want to generate 1-2% monthly income through covered calls and cash-secured puts..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Pure Capital Growth</span>
                <input type="range" min="1" max="10" v-model.number="answers.income_vs_growth.slider" class="slider" />
                <span class="slider-label-right">Pure Income Generation</span>
                <span class="slider-value">{{ answers.income_vs_growth.slider }}/10</span>
              </div>
            </div>

            <!-- Q8: Options Comfort -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">08</span>
                <div>
                  <div class="question-title">Options Experience & Comfort</div>
                  <div class="question-subtitle">Your experience level with options strategies.</div>
                </div>
              </div>
              <textarea v-model="answers.options_comfort.text" class="input textarea" placeholder="e.g. Comfortable with buying calls/puts and selling covered calls. Learning spreads and iron condors..." rows="3"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Never Traded Options</span>
                <input type="range" min="1" max="10" v-model.number="answers.options_comfort.slider" class="slider" />
                <span class="slider-label-right">Complex Multi-Leg Strategies</span>
                <span class="slider-value">{{ answers.options_comfort.slider }}/10</span>
              </div>
            </div>

            <!-- Q9: Active Trading % -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">09</span>
                <div>
                  <div class="question-title">Active Trading Allocation</div>
                  <div class="question-subtitle">What % of your portfolio should be actively traded vs. held long-term?</div>
                </div>
              </div>
              <textarea v-model="answers.active_trading_pct.text" class="input textarea" placeholder="e.g. Keep 60% in core long-term positions (ETFs, blue chips), actively trade the remaining 40%..." rows="2"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">0% (Fully Passive)</span>
                <input type="range" min="0" max="10" v-model.number="answers.active_trading_pct.slider" class="slider" />
                <span class="slider-label-right">100% (Fully Active)</span>
                <span class="slider-value">{{ answers.active_trading_pct.slider * 10 }}%</span>
              </div>
            </div>

            <!-- Q10: Max Position Drawdown -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">10</span>
                <div>
                  <div class="question-title">Max Position Drawdown Tolerance</div>
                  <div class="question-subtitle">Maximum loss on a single position before you want out.</div>
                </div>
              </div>
              <textarea v-model="answers.max_position_drawdown.text" class="input textarea" placeholder="e.g. Cut any position that loses more than 20% from entry. No exceptions..." rows="2"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Very Tight (5%)</span>
                <input type="range" min="1" max="10" v-model.number="answers.max_position_drawdown.slider" class="slider" />
                <span class="slider-label-right">Wide Tolerance (50%)</span>
                <span class="slider-value">{{ answers.max_position_drawdown.slider }}/10</span>
              </div>
            </div>

            <!-- Q11: Max Portfolio Drawdown -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">11</span>
                <div>
                  <div class="question-title">Max Portfolio Drawdown Tolerance</div>
                  <div class="question-subtitle">Maximum total portfolio drawdown you can stomach.</div>
                </div>
              </div>
              <textarea v-model="answers.max_portfolio_drawdown.text" class="input textarea" placeholder="e.g. If the overall portfolio drops more than 15%, I want to de-risk and reassess..." rows="2"></textarea>
              <div class="slider-row">
                <span class="slider-label-left">Very Conservative (5%)</span>
                <input type="range" min="1" max="10" v-model.number="answers.max_portfolio_drawdown.slider" class="slider" />
                <span class="slider-label-right">High Tolerance (50%)</span>
                <span class="slider-value">{{ answers.max_portfolio_drawdown.slider }}/10</span>
              </div>
            </div>

            <!-- Q12: Sectors & Themes (text only) -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">12</span>
                <div>
                  <div class="question-title">Sectors & Themes of Interest</div>
                  <div class="question-subtitle">Any sectors you love, want to avoid, or specific themes you follow.</div>
                </div>
              </div>
              <textarea v-model="answers.sectors_themes.text" class="input textarea" placeholder="e.g. Bullish on AI/semiconductors (NVDA, AMD, SMCI). Interested in energy transition. Avoid biotech pre-FDA..." rows="3"></textarea>
            </div>

            <!-- Q13: Special Instructions (text only) -->
            <div class="question-card">
              <div class="question-header">
                <span class="question-number">13</span>
                <div>
                  <div class="question-title">Special Instructions</div>
                  <div class="question-subtitle">Anything else your AI advisor should know about your preferences.</div>
                </div>
              </div>
              <textarea v-model="answers.special_instructions.text" class="input textarea" placeholder="e.g. I trade part-time and can only monitor positions during lunch and after market close. Prefer defined-risk strategies..." rows="3"></textarea>
            </div>
          </div>

          <!-- Model selector for summarization -->
          <div class="field" style="margin-top: 1.5rem;">
            <label class="field-label">AI Model for Profile Summarization</label>
            <select v-model="selectedModel" class="input">
              <option value="claude">Claude (Recommended)</option>
              <option value="grok">Grok</option>
              <option value="gemini">Gemini</option>
            </select>
          </div>

          <button class="btn btn-primary" style="width: 100%; margin-top: 1rem;" @click="saveProfile" :disabled="isSaving">
            <span v-if="isSaving">Generating Your Investment Profile...</span>
            <span v-else>Save & Generate Profile</span>
          </button>
        </div>

        <!-- ─── STEP 4: Profile Complete ─── -->
        <div v-if="step === 4">
          <div class="success-banner">
            <div class="success-icon">✓</div>
            <div class="success-title">Investment Profile Created</div>
            <div class="success-subtitle">Your AI advisor now knows your goals and preferences.</div>
          </div>

          <div class="summary-preview">
            <div class="summary-label">YOUR AI INVESTMENT PROFILE SUMMARY</div>
            <div class="summary-text">{{ generatedSummary }}</div>
          </div>

          <p style="color: var(--text-muted); font-size: 0.85rem; margin: 1rem 0; text-align: center;">
            This summary is injected into every AI conversation. Update it anytime in Settings → Investment Preferences.
          </p>

          <button class="btn btn-primary" style="width: 100%;" @click="$router.push('/dashboard')">
            Go to Dashboard
          </button>
        </div>

        <!-- Skip option (steps 1-3) -->
        <div v-if="step < 4" style="margin-top: 2rem; text-align: center;">
          <button class="btn btn-secondary" @click="skipStep">
            {{ step === 3 ? 'Skip Profile for Now' : 'Skip for Now' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const step = ref(1)
const appKey = ref('')
const appSecret = ref('')
const callbackUrl = ref('https://volflowagent.com')
const isLoading = ref(false)
const isSaving = ref(false)
const error = ref(null)
const success = ref(false)
const selectedModel = ref('claude')
const generatedSummary = ref('')

// Investment profile answers — each has text + slider (where applicable)
const answers = reactive({
  short_term_goals:       { text: '', slider: 5 },
  medium_term_goals:      { text: '', slider: 5 },
  long_term_goals:        { text: '', slider: 5 },
  risk_tolerance:         { text: '', slider: 5 },
  portfolio_concentration:{ text: '', slider: 5 },
  intraday_activity:      { text: '', slider: 3 },
  income_vs_growth:       { text: '', slider: 4 },
  options_comfort:        { text: '', slider: 5 },
  active_trading_pct:     { text: '', slider: 4 },
  max_position_drawdown:  { text: '', slider: 4 },
  max_portfolio_drawdown: { text: '', slider: 3 },
  sectors_themes:         { text: '' },
  special_instructions:   { text: '' },
})

const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('session_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

async function saveCredentials() {
  isLoading.value = true
  error.value = null
  success.value = false
  try {
    await api.post('/api/schwab/credentials', {
      app_key: appKey.value,
      app_secret: appSecret.value,
      callback_url: callbackUrl.value
    })
    success.value = true
    step.value = 2
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save credentials'
  } finally {
    isLoading.value = false
  }
}

async function connectSchwab() {
  isLoading.value = true
  error.value = null
  try {
    const response = await api.get('/api/schwab/auth-url')
    window.location.href = response.data.auth_url
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to get authorization URL'
    isLoading.value = false
  }
}

async function saveProfile() {
  // Check at least a few answers have been filled
  const hasContent = Object.values(answers).some(a => a.text && a.text.trim().length > 10)
  if (!hasContent) {
    error.value = 'Please fill in at least a few answers before saving your profile.'
    return
  }

  isSaving.value = true
  error.value = null

  try {
    const response = await api.post('/api/profile', {
      raw_answers: answers,
      model: selectedModel.value
    })
    generatedSummary.value = response.data.ai_summary
    step.value = 4
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to generate investment profile. Please try again.'
  } finally {
    isSaving.value = false
  }
}

function skipStep() {
  if (step.value === 3) {
    router.push('/dashboard')
  } else {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 0 20px rgba(255, 149, 0, 0.2);
}

.card-header {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.1em;
  text-shadow: 0 0 8px var(--accent-primary);
  margin: 0;
}

.step-indicator {
  display: flex;
  gap: 0.5rem;
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  transition: all 0.3s;
}

.step-dot.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  box-shadow: 0 0 8px var(--accent-primary);
}

.step-dot.done {
  background: rgba(255, 149, 0, 0.4);
  border-color: var(--accent-primary);
}

.card-body {
  padding: 1.5rem;
}

.step-desc {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.link {
  color: var(--accent-primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
}

.alert p { margin: 0; }

.alert-success {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid #10b981;
  color: #10b981;
}

.field {
  margin-bottom: 1rem;
}

.field-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.field-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.input {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 0.5rem 0.75rem;
  color: var(--text-primary);
  font-family: 'VT323', monospace;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 8px rgba(255, 149, 0, 0.3);
}

.textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
  font-size: 0.95rem;
}

/* Questions */
.questions-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.question-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  transition: border-color 0.2s;
}

.question-card:hover {
  border-color: rgba(255, 149, 0, 0.4);
}

.question-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.question-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-primary);
  opacity: 0.6;
  font-family: 'VT323', monospace;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}

.question-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.2rem;
}

.question-horizon {
  color: var(--accent-primary);
  font-size: 0.9rem;
}

.question-subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Slider */
.slider-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.slider-label-left,
.slider-label-right {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

.slider {
  flex: 1;
  min-width: 120px;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  background: var(--border-secondary);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent-primary);
  cursor: pointer;
  box-shadow: 0 0 8px rgba(255, 149, 0, 0.6);
  transition: box-shadow 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  box-shadow: 0 0 14px rgba(255, 149, 0, 0.9);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent-primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 0 8px rgba(255, 149, 0, 0.6);
}

.slider-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent-primary);
  font-family: 'VT323', monospace;
  min-width: 40px;
  text-align: right;
  flex-shrink: 0;
}

/* Success / Step 4 */
.success-banner {
  text-align: center;
  padding: 2rem 1rem;
  margin-bottom: 1.5rem;
}

.success-icon {
  font-size: 3rem;
  color: #10b981;
  text-shadow: 0 0 20px #10b981;
  margin-bottom: 0.5rem;
}

.success-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.1em;
  margin-bottom: 0.25rem;
}

.success-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.summary-preview {
  background: var(--bg-primary);
  border: 1px solid var(--accent-primary);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  box-shadow: 0 0 12px rgba(255, 149, 0, 0.15);
}

.summary-label {
  font-size: 0.75rem;
  color: var(--accent-primary);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.summary-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  white-space: pre-wrap;
}

/* Buttons */
.btn {
  padding: 0.6rem 1.5rem;
  border-radius: var(--radius-md);
  font-family: 'VT323', monospace;
  font-size: 1.1rem;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: var(--accent-primary);
  color: #000;
  border-color: var(--accent-primary);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 0 15px rgba(255, 149, 0, 0.5);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-color: var(--border-secondary);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--text-primary);
}

.btn-lg {
  padding: 0.85rem 2rem;
  font-size: 1.2rem;
}

/* ── Mobile Responsive ────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  /* Card fills screen */
  .card { width: 96% !important; max-width: 100% !important; }

  /* Question cards */
  .question-card { padding: 1rem; }
  .question-header { gap: 0.75rem; }
  .question-number { font-size: 1.5rem; }
  .question-title { font-size: 0.95rem; }

  /* Slider row: stack labels above/below */
  .slider-row {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  .slider-label-left, .slider-label-right { font-size: 0.7rem; }
  .slider { width: 100%; order: 3; }
  .slider-value { order: 4; width: 100%; text-align: center; }

  /* Multi-select options: 2 columns */
  .options-grid { grid-template-columns: 1fr 1fr !important; }

  /* Buttons full width */
  .btn { width: 100%; }
}
</style>
