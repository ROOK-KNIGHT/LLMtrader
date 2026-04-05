<template>
  <div class="config-dashboard">
    <!-- Investment Preferences Section -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">INVESTMENT PREFERENCES</div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span v-if="configStore.investmentProfile.exists" style="font-size: 0.8rem; color: var(--text-muted);">
            Last updated: {{ formatDate(configStore.investmentProfile.updatedAt) }}
          </span>
          <span v-if="!configStore.investmentProfile.exists" style="font-size: 0.8rem; color: #f59e0b; border: 1px solid #f59e0b; padding: 0.15rem 0.5rem; border-radius: 4px;">
            NOT SET
          </span>
        </div>
      </div>
      <div class="panel-body">

        <!-- Loading state -->
        <div v-if="configStore.investmentProfile.isLoading" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          Loading investment profile...
        </div>

        <template v-else>
          <!-- Error / Success banners -->
          <div v-if="configStore.investmentProfile.error" class="ip-alert ip-alert-error">
            {{ configStore.investmentProfile.error }}
          </div>
          <div v-if="configStore.investmentProfile.successMessage" class="ip-alert ip-alert-success">
            {{ configStore.investmentProfile.successMessage }}
          </div>

          <!-- Current AI Summary preview -->
          <div v-if="configStore.investmentProfile.aiSummary" class="ip-summary-box">
            <div class="ip-summary-label">CURRENT AI PROFILE SUMMARY</div>
            <div class="ip-summary-text">{{ configStore.investmentProfile.aiSummary }}</div>
            <div class="ip-summary-note">This summary is injected into every AI conversation as context.</div>
          </div>
          <div v-else class="ip-summary-box ip-summary-empty">
            <div class="ip-summary-label">NO PROFILE SUMMARY YET</div>
            <div class="ip-summary-note">Fill in your preferences below and click "Update & Summarize" to generate your personalized AI profile.</div>
          </div>

          <!-- Questions -->
          <div class="ip-questions">

            <!-- Short-Term Goals -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">01</span>
                <div>
                  <div class="ip-q-title">Short-Term Goals <span class="ip-q-horizon">(0–1 Year)</span></div>
                  <div class="ip-q-sub">Income targets, specific returns, learning goals.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.short_term_goals.text" class="input ip-textarea" rows="2" placeholder="e.g. Generate $2k/month through options premiums..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Low Priority</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.short_term_goals.slider" class="ip-slider" />
                <span class="ip-sl-right">Critical Priority</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.short_term_goals.slider }}/10</span>
              </div>
            </div>

            <!-- Medium-Term Goals -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">02</span>
                <div>
                  <div class="ip-q-title">Medium-Term Goals <span class="ip-q-horizon">(1–5 Years)</span></div>
                  <div class="ip-q-sub">Financial milestones, account growth targets.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.medium_term_goals.text" class="input ip-textarea" rows="2" placeholder="e.g. Grow account to $500k, fund a down payment..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Low Priority</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.medium_term_goals.slider" class="ip-slider" />
                <span class="ip-sl-right">Critical Priority</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.medium_term_goals.slider }}/10</span>
              </div>
            </div>

            <!-- Long-Term Goals -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">03</span>
                <div>
                  <div class="ip-q-title">Long-Term Goals <span class="ip-q-horizon">(5+ Years)</span></div>
                  <div class="ip-q-sub">Retirement, generational wealth, financial independence.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.long_term_goals.text" class="input ip-textarea" rows="2" placeholder="e.g. Retire at 55 with $3M portfolio..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Low Priority</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.long_term_goals.slider" class="ip-slider" />
                <span class="ip-sl-right">Critical Priority</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.long_term_goals.slider }}/10</span>
              </div>
            </div>

            <!-- Risk Tolerance -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">04</span>
                <div>
                  <div class="ip-q-title">Risk Tolerance</div>
                  <div class="ip-q-sub">How do you handle market volatility and drawdowns?</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.risk_tolerance.text" class="input ip-textarea" rows="2" placeholder="e.g. I've been through 2020 and 2022 without panic selling..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Very Conservative</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.risk_tolerance.slider" class="ip-slider" />
                <span class="ip-sl-right">Very Aggressive</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.risk_tolerance.slider }}/10</span>
              </div>
            </div>

            <!-- Portfolio Concentration -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">05</span>
                <div>
                  <div class="ip-q-title">Portfolio Concentration</div>
                  <div class="ip-q-sub">Concentrated high-conviction vs. broad diversification?</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.portfolio_concentration.text" class="input ip-textarea" rows="2" placeholder="e.g. I prefer 8-12 high-conviction positions..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Very Broad (50+)</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.portfolio_concentration.slider" class="ip-slider" />
                <span class="ip-sl-right">Ultra Concentrated (3-5)</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.portfolio_concentration.slider }}/10</span>
              </div>
            </div>

            <!-- Intra-Day Activity -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">06</span>
                <div>
                  <div class="ip-q-title">Intra-Day Trading Interest</div>
                  <div class="ip-q-sub">Day trading for quick cash alongside longer-term holds?</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.intraday_activity.text" class="input ip-textarea" rows="2" placeholder="e.g. Mostly swing trades, but I'll day trade on strong momentum setups..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">None (Swing Only)</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.intraday_activity.slider" class="ip-slider" />
                <span class="ip-sl-right">Heavy Intra-Day</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.intraday_activity.slider }}/10</span>
              </div>
            </div>

            <!-- Income vs Growth -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">07</span>
                <div>
                  <div class="ip-q-title">Income vs. Growth Orientation</div>
                  <div class="ip-q-sub">Capital appreciation, income generation, or both?</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.income_vs_growth.text" class="input ip-textarea" rows="2" placeholder="e.g. Primarily growth-focused but want 1-2% monthly income through covered calls..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Pure Growth</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.income_vs_growth.slider" class="ip-slider" />
                <span class="ip-sl-right">Pure Income</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.income_vs_growth.slider }}/10</span>
              </div>
            </div>

            <!-- Options Comfort -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">08</span>
                <div>
                  <div class="ip-q-title">Options Experience & Comfort</div>
                  <div class="ip-q-sub">Your experience level with options strategies.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.options_comfort.text" class="input ip-textarea" rows="2" placeholder="e.g. Comfortable with buying calls/puts and selling covered calls..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Never Traded Options</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.options_comfort.slider" class="ip-slider" />
                <span class="ip-sl-right">Complex Multi-Leg</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.options_comfort.slider }}/10</span>
              </div>
            </div>

            <!-- Active Trading % -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">09</span>
                <div>
                  <div class="ip-q-title">Active Trading Allocation</div>
                  <div class="ip-q-sub">What % of your portfolio should be actively traded?</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.active_trading_pct.text" class="input ip-textarea" rows="2" placeholder="e.g. Keep 60% in core long-term positions, actively trade the remaining 40%..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">0% (Fully Passive)</span>
                <input type="range" min="0" max="10" v-model.number="configStore.investmentProfile.rawAnswers.active_trading_pct.slider" class="ip-slider" />
                <span class="ip-sl-right">100% (Fully Active)</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.active_trading_pct.slider * 10 }}%</span>
              </div>
            </div>

            <!-- Max Position Drawdown -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">10</span>
                <div>
                  <div class="ip-q-title">Max Position Drawdown Tolerance</div>
                  <div class="ip-q-sub">Maximum loss on a single position before you want out.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.max_position_drawdown.text" class="input ip-textarea" rows="2" placeholder="e.g. Cut any position that loses more than 20% from entry..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Very Tight (5%)</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.max_position_drawdown.slider" class="ip-slider" />
                <span class="ip-sl-right">Wide Tolerance (50%)</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.max_position_drawdown.slider }}/10</span>
              </div>
            </div>

            <!-- Max Portfolio Drawdown -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">11</span>
                <div>
                  <div class="ip-q-title">Max Portfolio Drawdown Tolerance</div>
                  <div class="ip-q-sub">Maximum total portfolio drawdown you can stomach.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.max_portfolio_drawdown.text" class="input ip-textarea" rows="2" placeholder="e.g. If the overall portfolio drops more than 15%, I want to de-risk..."></textarea>
              <div class="ip-slider-row">
                <span class="ip-sl-left">Very Conservative (5%)</span>
                <input type="range" min="1" max="10" v-model.number="configStore.investmentProfile.rawAnswers.max_portfolio_drawdown.slider" class="ip-slider" />
                <span class="ip-sl-right">High Tolerance (50%)</span>
                <span class="ip-sl-val">{{ configStore.investmentProfile.rawAnswers.max_portfolio_drawdown.slider }}/10</span>
              </div>
            </div>

            <!-- Sectors & Themes -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">12</span>
                <div>
                  <div class="ip-q-title">Sectors & Themes of Interest</div>
                  <div class="ip-q-sub">Sectors you love, want to avoid, or specific themes you follow.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.sectors_themes.text" class="input ip-textarea" rows="2" placeholder="e.g. Bullish on AI/semiconductors. Interested in energy transition. Avoid biotech pre-FDA..."></textarea>
            </div>

            <!-- Special Instructions -->
            <div class="ip-question">
              <div class="ip-q-header">
                <span class="ip-q-num">13</span>
                <div>
                  <div class="ip-q-title">Special Instructions</div>
                  <div class="ip-q-sub">Anything else your AI advisor should know.</div>
                </div>
              </div>
              <textarea v-model="configStore.investmentProfile.rawAnswers.special_instructions.text" class="input ip-textarea" rows="2" placeholder="e.g. I trade part-time and can only monitor positions during lunch and after market close..."></textarea>
            </div>

          </div>

          <!-- Model selector + Save button -->
          <div class="ip-footer">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
              <div>
                <label class="config-label">Summarization Model</label>
                <select v-model="configStore.investmentProfile.summaryModel" class="input" style="width: 160px;">
                  <option value="claude">Claude</option>
                  <option value="grok">Grok</option>
                  <option value="gemini">Gemini</option>
                </select>
              </div>
              <button
                class="btn btn-primary"
                style="margin-top: 1.25rem;"
                @click="configStore.saveInvestmentProfile()"
                :disabled="configStore.investmentProfile.isSaving"
              >
                {{ configStore.investmentProfile.isSaving ? 'Generating Summary...' : 'Update & Summarize' }}
              </button>
            </div>
            <p class="ip-footer-note">
              The AI will summarize your answers into a concise Investment Policy Statement and inject it into every chat session automatically.
            </p>
          </div>
        </template>
      </div>
    </div>

    <!-- API Connections Section -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">API CONNECTIONS</div>
        <div class="connection-status">
          <span :class="['status-indicator', configStore.schwabApiConnected ? 'connected' : 'disconnected']"></span>
          <span>{{ configStore.schwabApiConnected ? 'Connected' : 'Disconnected' }}</span>
        </div>
      </div>
      <div class="panel-body">
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">Schwab API Key</label>
            <input 
              type="text" 
              class="input mono" 
              v-model="configStore.schwabApiKey"
              placeholder="Enter API Key"
            />
          </div>
          <div class="config-item">
            <label class="config-label">API Secret</label>
            <input 
              type="password" 
              class="input mono" 
              v-model="configStore.schwabApiSecret"
              placeholder="Enter API Secret"
            />
          </div>
          <div class="config-item">
            <label class="config-label">Callback URL</label>
            <input 
              type="text" 
              class="input mono" 
              v-model="configStore.schwabCallbackUrl"
              placeholder="https://..."
            />
          </div>
          <div class="config-item">
            <label class="config-label">Rate Limit (req/min)</label>
            <input 
              type="number" 
              class="input mono" 
              v-model.number="configStore.apiRateLimit"
            />
          </div>
        </div>
        
        <div class="api-stats">
          <div class="stat-item">
            <span class="stat-label">Rate Limit Used:</span>
            <span class="stat-value mono">{{ configStore.apiRateLimitUsed }} / {{ configStore.apiRateLimit }}</span>
            <div class="stat-bar">
              <div class="stat-fill" :style="{ width: (configStore.apiRateLimitUsed / configStore.apiRateLimit * 100) + '%' }"></div>
            </div>
          </div>
        </div>
        
        <div class="config-actions">
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.autoReconnect" />
            <span>Auto-reconnect on disconnect</span>
          </label>
          <button class="btn btn-primary" @click="testConnection" :disabled="testing">
            {{ testing ? 'Testing...' : 'Test Connection' }}
          </button>
          <button class="btn btn-secondary" @click="configStore.disconnectSchwabApi">
            Disconnect
          </button>
        </div>
      </div>
    </div>

    <!-- Notification Settings Section -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">NOTIFICATION SETTINGS</div>
      </div>
      <div class="panel-body">
        <div class="config-section">
          <h3 class="section-title">Email Notifications</h3>
          <div class="config-grid">
            <div class="config-item">
              <label class="checkbox-label">
                <input type="checkbox" v-model="configStore.emailNotifications" />
                <span>Enable Email Notifications</span>
              </label>
            </div>
            <div class="config-item">
              <label class="config-label">Email Address</label>
              <input 
                type="email" 
                class="input" 
                v-model="configStore.emailAddress"
                :disabled="!configStore.emailNotifications"
                placeholder="your@email.com"
              />
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3 class="section-title">SMS Notifications</h3>
          <div class="config-grid">
            <div class="config-item">
              <label class="checkbox-label">
                <input type="checkbox" v-model="configStore.smsNotifications" />
                <span>Enable SMS Notifications</span>
              </label>
            </div>
            <div class="config-item">
              <label class="config-label">Phone Number</label>
              <input 
                type="tel" 
                class="input" 
                v-model="configStore.smsNumber"
                :disabled="!configStore.smsNotifications"
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3 class="section-title">Alert Triggers</h3>
          <div class="alert-triggers">
            <label class="checkbox-label">
              <input type="checkbox" v-model="configStore.alertOnPositionOpen" />
              <span>Position Opened</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="configStore.alertOnPositionClose" />
              <span>Position Closed</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="configStore.alertOnProfitTarget" />
              <span>Profit Target Hit</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="configStore.alertOnStopLoss" />
              <span>Stop Loss Hit</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="configStore.alertOnDailyLossLimit" />
              <span>Daily Loss Limit</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="configStore.alertOnRiskRuleBreach" />
              <span>Risk Rule Breach</span>
            </label>
          </div>
          <div class="config-item" style="margin-top: 1rem;">
            <label class="config-label">Daily P&L Alert Threshold ($)</label>
            <input 
              type="number" 
              class="input mono" 
              v-model.number="configStore.dailyPnLAlertThreshold"
              placeholder="1000"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Display Preferences Section -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">DISPLAY PREFERENCES</div>
      </div>
      <div class="panel-body">
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">Theme</label>
            <select class="input" v-model="configStore.theme">
              <option value="retro-orange">Retro Orange (Current)</option>
              <option value="retro-green">Retro Green</option>
              <option value="retro-blue">Retro Blue</option>
              <option value="dark">Dark Modern</option>
            </select>
          </div>
          <div class="config-item">
            <label class="config-label">Default Chart Timeframe</label>
            <select class="input" v-model="configStore.chartDefaultTimeframe">
              <option value="1min">1 Minute</option>
              <option value="5min">5 Minutes</option>
              <option value="15min">15 Minutes</option>
              <option value="30min">30 Minutes</option>
              <option value="1hour">1 Hour</option>
              <option value="daily">Daily</option>
            </select>
          </div>
          <div class="config-item">
            <label class="config-label">Dashboard Layout</label>
            <select class="input" v-model="configStore.dashboardLayout">
              <option value="default">Default</option>
              <option value="compact">Compact</option>
              <option value="expanded">Expanded</option>
            </select>
          </div>
        </div>
        
        <div class="display-toggles">
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.chartShowVolume" />
            <span>Show Volume on Charts</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.chartShowIndicators" />
            <span>Show Technical Indicators</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.tableCompactMode" />
            <span>Compact Table Mode</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.showGreeksInPositions" />
            <span>Show Greeks in Positions Table</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Data Management Section -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">DATA MANAGEMENT</div>
      </div>
      <div class="panel-body">
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">Data Refresh Interval (seconds)</label>
            <input 
              type="number" 
              class="input mono" 
              v-model.number="configStore.dataRefreshInterval"
              min="1"
              max="60"
            />
          </div>
          <div class="config-item">
            <label class="config-label">Historical Data Days</label>
            <input 
              type="number" 
              class="input mono" 
              v-model.number="configStore.historicalDataDays"
              min="30"
              max="365"
            />
          </div>
          <div class="config-item">
            <label class="config-label">Cache Expiry (seconds)</label>
            <input 
              type="number" 
              class="input mono" 
              v-model.number="configStore.cacheExpiry"
              :disabled="!configStore.cacheEnabled"
            />
          </div>
          <div class="config-item">
            <label class="config-label">Backup Frequency</label>
            <select class="input" v-model="configStore.backupFrequency" :disabled="!configStore.autoBackup">
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        </div>
        
        <div class="data-toggles">
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.cacheEnabled" />
            <span>Enable Data Caching</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.autoBackup" />
            <span>Automatic Backups</span>
          </label>
        </div>

        <div class="config-actions">
          <button class="btn btn-secondary" @click="exportConfig">
            Export Settings
          </button>
          <button class="btn btn-secondary" @click="triggerImport">
            Import Settings
          </button>
          <input 
            ref="fileInput" 
            type="file" 
            accept=".json" 
            style="display: none;" 
            @change="importConfig"
          />
        </div>
      </div>
    </div>

    <!-- Account Settings Section -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">ACCOUNT SETTINGS</div>
      </div>
      <div class="panel-body">
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">Display Name</label>
            <input 
              type="text" 
              class="input" 
              v-model="configStore.userName"
              placeholder="Your Name"
            />
          </div>
          <div class="config-item">
            <label class="config-label">Email</label>
            <input 
              type="email" 
              class="input" 
              v-model="configStore.userEmail"
              placeholder="your@email.com"
            />
          </div>
          <div class="config-item">
            <label class="config-label">Session Timeout (minutes)</label>
            <input 
              type="number" 
              class="input mono" 
              v-model.number="configStore.sessionTimeout"
              min="5"
              max="480"
            />
          </div>
        </div>
        
        <div class="security-toggles">
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.twoFactorEnabled" />
            <span>Enable Two-Factor Authentication</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="configStore.autoLogout" />
            <span>Auto-logout on Inactivity</span>
          </label>
        </div>

        <div class="config-actions">
          <button class="btn btn-primary" @click="saveSettings">
            Save All Settings
          </button>
          <button class="btn btn-secondary" @click="resetToDefaults">
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
const testing = ref(false)
const fileInput = ref(null)

onMounted(() => {
  configStore.loadInvestmentProfile()
})

function formatDate(isoString) {
  if (!isoString) return 'Never'
  try {
    return new Date(isoString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return isoString }
}

async function testConnection() {
  testing.value = true
  const result = await configStore.testSchwabConnection()
  testing.value = false
  alert(result.message)
}

function exportConfig() {
  const settings = configStore.exportSettings()
  const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'volflow-config.json'
  a.click()
  URL.revokeObjectURL(url)
}

function triggerImport() {
  fileInput.value.click()
}

function importConfig(event) {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const settings = JSON.parse(e.target.result)
      configStore.importSettings(settings)
      alert('Settings imported successfully!')
    } catch (error) {
      alert('Error importing settings: ' + error.message)
    }
  }
  reader.readAsText(file)
}

function saveSettings() {
  // In real app, would save to backend
  alert('Settings saved successfully!')
}

function resetToDefaults() {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    // Reset logic here
    alert('Settings reset to defaults')
  }
}
</script>

<style scoped>
.config-dashboard {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
}

.panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 0 10px rgba(255, 149, 0, 0.2);
}

.panel-header {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.15em;
  text-shadow: 0 0 8px var(--accent-primary);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.connected {
  background: #00ff00;
  box-shadow: 0 0 10px #00ff00;
  animation: pulse 2s infinite;
}

.status-indicator.disconnected {
  background: #ff0000;
  box-shadow: 0 0 10px #ff0000;
}

.panel-body {
  padding: 1.5rem;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 0.5rem 0.75rem;
  color: var(--text-primary);
  font-family: 'VT323', monospace;
  font-size: 1rem;
  transition: all var(--transition-base);
}

.input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 10px rgba(255, 149, 0, 0.3);
}

.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.api-stats {
  margin-bottom: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1rem;
  color: var(--text-primary);
}

.stat-bar {
  width: 100%;
  height: 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  box-shadow: 0 0 10px var(--accent-primary);
  transition: width 0.3s ease;
}

.config-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.config-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 0.95rem;
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
  text-shadow: 0 0 8px var(--accent-primary);
}

.alert-triggers {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.display-toggles,
.data-toggles,
.security-toggles {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1.5rem;
  border-radius: var(--radius-md);
  font-family: 'VT323', monospace;
  font-size: 1rem;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all var(--transition-base);
  border: 1px solid;
}

.btn-primary {
  background: var(--accent-primary);
  color: #000;
  border-color: var(--accent-primary);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 0 15px rgba(255, 149, 0, 0.5);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Investment Profile styles ─────────────────────────────────────────────── */
.ip-alert {
  padding: 0.65rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}
.ip-alert-error  { background: rgba(239,68,68,0.1); border: 1px solid #ef4444; color: #ef4444; }
.ip-alert-success{ background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #10b981; }

.ip-summary-box {
  background: var(--bg-primary);
  border: 1px solid var(--accent-primary);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 0 10px rgba(255,149,0,0.12);
}
.ip-summary-empty {
  border-color: var(--border-secondary);
  box-shadow: none;
}
.ip-summary-label {
  font-size: 0.75rem;
  color: var(--accent-primary);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.ip-summary-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  white-space: pre-wrap;
  margin-bottom: 0.5rem;
}
.ip-summary-note {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-style: italic;
}

.ip-questions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.ip-question {
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 1rem;
  transition: border-color 0.2s;
}
.ip-question:hover { border-color: rgba(255,149,0,0.35); }

.ip-q-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}
.ip-q-num {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--accent-primary);
  opacity: 0.55;
  font-family: 'VT323', monospace;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}
.ip-q-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.15rem;
}
.ip-q-horizon { color: var(--accent-primary); font-size: 0.85rem; }
.ip-q-sub { font-size: 0.78rem; color: var(--text-muted); }

.ip-textarea {
  width: 100%;
  resize: vertical;
  min-height: 60px;
  line-height: 1.5;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.ip-slider-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.6rem;
  flex-wrap: wrap;
}
.ip-sl-left, .ip-sl-right {
  font-size: 0.72rem;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}
.ip-slider {
  flex: 1;
  min-width: 100px;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  background: var(--border-secondary);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}
.ip-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent-primary);
  cursor: pointer;
  box-shadow: 0 0 6px rgba(255,149,0,0.6);
}
.ip-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent-primary);
  cursor: pointer;
  border: none;
}
.ip-sl-val {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent-primary);
  font-family: 'VT323', monospace;
  min-width: 38px;
  text-align: right;
  flex-shrink: 0;
}

.ip-footer {
  border-top: 1px solid var(--border-secondary);
  padding-top: 1.25rem;
  margin-top: 0.5rem;
}
.ip-footer-note {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.75rem;
  line-height: 1.5;
}

/* ── Mobile Responsive ────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .config-dashboard { padding: 0.5rem; }
  .panel { margin-bottom: 0.75rem; }
  .panel-header { flex-wrap: wrap; gap: 0.5rem; }

  /* Question cards */
  .ip-question { padding: 0.75rem; }
  .ip-q-header { gap: 0.5rem; }
  .ip-q-num { font-size: 1.4rem; }
  .ip-q-title { font-size: 0.9rem; }

  /* Slider row: stack */
  .ip-slider-row { flex-wrap: wrap; gap: 0.25rem; }
  .ip-sl-left, .ip-sl-right { font-size: 0.65rem; }
  .ip-slider { width: 100%; order: 3; }
  .ip-sl-val { order: 4; width: 100%; text-align: center; }

  /* Summary box */
  .ip-summary-box { padding: 0.75rem; }

  /* Footer button full width */
  .ip-footer .btn { width: 100%; }
}
</style>
