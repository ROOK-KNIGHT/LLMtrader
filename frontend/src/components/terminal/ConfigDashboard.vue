<template>
  <div class="config-dashboard">
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
import { ref } from 'vue'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
const testing = ref(false)
const fileInput = ref(null)

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
</style>
