import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

const API_BASE = '/api'

function getAuthHeaders() {
  const token = localStorage.getItem('session_token')
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
}

export const useConfigStore = defineStore('config', () => {
  // API Connections
  const schwabApiConnected = ref(true)
  const schwabApiKey = ref('m3RcdW4LPQgMcpAXIqgHgWCwwFkXjr1k6GYzmxAVYdJg8CB0')
  const schwabApiSecret = ref('••••••••••••••••••••••••••••••••')
  const schwabCallbackUrl = ref('https://volflowagent.com/oauth/callback')
  const apiRateLimit = ref(120) // requests per minute
  const apiRateLimitUsed = ref(47)
  const lastApiCall = ref(new Date())
  const autoReconnect = ref(true)
  
  // Notification Settings
  const emailNotifications = ref(true)
  const emailAddress = ref('demo@volflowagent.com')
  const smsNotifications = ref(false)
  const smsNumber = ref('')
  
  // Alert Thresholds
  const alertOnPositionOpen = ref(true)
  const alertOnPositionClose = ref(true)
  const alertOnProfitTarget = ref(true)
  const alertOnStopLoss = ref(true)
  const alertOnDailyLossLimit = ref(true)
  const alertOnRiskRuleBreach = ref(true)
  const dailyPnLAlertThreshold = ref(1000) // Alert if daily P&L exceeds this
  
  // Display Preferences
  const theme = ref('retro-orange')
  const chartDefaultTimeframe = ref('5min')
  const chartShowVolume = ref(true)
  const chartShowIndicators = ref(true)
  const tableCompactMode = ref(false)
  const showGreeksInPositions = ref(true)
  const dashboardLayout = ref('default')
  
  // Data Management
  const dataRefreshInterval = ref(5) // seconds
  const historicalDataDays = ref(90)
  const cacheEnabled = ref(true)
  const cacheExpiry = ref(300) // seconds
  const autoBackup = ref(true)
  const backupFrequency = ref('daily')
  
  // ── Investment Profile ──────────────────────────────────────────────────────
  const investmentProfile = reactive({
    exists: false,
    rawAnswers: {
      short_term_goals:        { text: '', slider: 5 },
      medium_term_goals:       { text: '', slider: 5 },
      long_term_goals:         { text: '', slider: 5 },
      risk_tolerance:          { text: '', slider: 5 },
      portfolio_concentration: { text: '', slider: 5 },
      intraday_activity:       { text: '', slider: 3 },
      income_vs_growth:        { text: '', slider: 4 },
      options_comfort:         { text: '', slider: 5 },
      active_trading_pct:      { text: '', slider: 4 },
      max_position_drawdown:   { text: '', slider: 4 },
      max_portfolio_drawdown:  { text: '', slider: 3 },
      sectors_themes:          { text: '' },
      special_instructions:    { text: '' },
    },
    aiSummary: '',
    summaryModel: 'claude',
    updatedAt: null,
    isLoading: false,
    isSaving: false,
    error: null,
    successMessage: null,
  })

  async function loadInvestmentProfile() {
    investmentProfile.isLoading = true
    investmentProfile.error = null
    try {
      const res = await fetch(`${API_BASE}/profile`, { headers: getAuthHeaders() })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      investmentProfile.exists = data.exists
      if (data.exists) {
        // Merge raw answers back into reactive state
        if (data.raw_answers) {
          Object.keys(data.raw_answers).forEach(key => {
            if (investmentProfile.rawAnswers[key] !== undefined) {
              Object.assign(investmentProfile.rawAnswers[key], data.raw_answers[key])
            }
          })
        }
        investmentProfile.aiSummary = data.ai_summary || ''
        investmentProfile.summaryModel = data.summary_model || 'claude'
        investmentProfile.updatedAt = data.updated_at
      }
    } catch (e) {
      investmentProfile.error = 'Failed to load investment profile.'
    } finally {
      investmentProfile.isLoading = false
    }
  }

  async function saveInvestmentProfile() {
    investmentProfile.isSaving = true
    investmentProfile.error = null
    investmentProfile.successMessage = null
    try {
      const res = await fetch(`${API_BASE}/profile`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          raw_answers: investmentProfile.rawAnswers,
          model: investmentProfile.summaryModel
        })
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()
      investmentProfile.aiSummary = data.ai_summary
      investmentProfile.exists = true
      investmentProfile.updatedAt = new Date().toISOString()
      investmentProfile.successMessage = 'Investment profile updated successfully.'
    } catch (e) {
      investmentProfile.error = e.message || 'Failed to save investment profile.'
    } finally {
      investmentProfile.isSaving = false
    }
  }

  // Account Settings
  const userName = ref('Demo User')
  const userEmail = ref('demo@volflowagent.com')
  const sessionTimeout = ref(60) // minutes
  const twoFactorEnabled = ref(false)
  const autoLogout = ref(true)
  
  // Actions
  function updateSchwabApi(key, secret, callback) {
    schwabApiKey.value = key
    schwabApiSecret.value = secret
    schwabCallbackUrl.value = callback
  }
  
  function testSchwabConnection() {
    // Mock API test
    return new Promise((resolve) => {
      setTimeout(() => {
        schwabApiConnected.value = true
        resolve({ success: true, message: 'Connection successful' })
      }, 1000)
    })
  }
  
  function disconnectSchwabApi() {
    schwabApiConnected.value = false
  }
  
  function updateNotificationSettings(settings) {
    emailNotifications.value = settings.email
    emailAddress.value = settings.emailAddress
    smsNotifications.value = settings.sms
    smsNumber.value = settings.smsNumber
  }
  
  function updateAlertThresholds(thresholds) {
    Object.assign({
      alertOnPositionOpen,
      alertOnPositionClose,
      alertOnProfitTarget,
      alertOnStopLoss,
      alertOnDailyLossLimit,
      alertOnRiskRuleBreach,
      dailyPnLAlertThreshold
    }, thresholds)
  }
  
  function updateDisplayPreferences(prefs) {
    theme.value = prefs.theme || theme.value
    chartDefaultTimeframe.value = prefs.chartTimeframe || chartDefaultTimeframe.value
    chartShowVolume.value = prefs.showVolume ?? chartShowVolume.value
    chartShowIndicators.value = prefs.showIndicators ?? chartShowIndicators.value
    tableCompactMode.value = prefs.compactMode ?? tableCompactMode.value
    showGreeksInPositions.value = prefs.showGreeks ?? showGreeksInPositions.value
  }
  
  function updateDataSettings(settings) {
    dataRefreshInterval.value = settings.refreshInterval || dataRefreshInterval.value
    historicalDataDays.value = settings.historicalDays || historicalDataDays.value
    cacheEnabled.value = settings.cacheEnabled ?? cacheEnabled.value
    cacheExpiry.value = settings.cacheExpiry || cacheExpiry.value
    autoBackup.value = settings.autoBackup ?? autoBackup.value
    backupFrequency.value = settings.backupFrequency || backupFrequency.value
  }
  
  function updateAccountSettings(settings) {
    userName.value = settings.name || userName.value
    userEmail.value = settings.email || userEmail.value
    sessionTimeout.value = settings.timeout || sessionTimeout.value
    twoFactorEnabled.value = settings.twoFactor ?? twoFactorEnabled.value
    autoLogout.value = settings.autoLogout ?? autoLogout.value
  }
  
  function exportSettings() {
    return {
      api: {
        schwabApiKey: schwabApiKey.value,
        schwabCallbackUrl: schwabCallbackUrl.value,
        apiRateLimit: apiRateLimit.value,
        autoReconnect: autoReconnect.value
      },
      notifications: {
        emailNotifications: emailNotifications.value,
        emailAddress: emailAddress.value,
        smsNotifications: smsNotifications.value,
        smsNumber: smsNumber.value,
        alerts: {
          alertOnPositionOpen: alertOnPositionOpen.value,
          alertOnPositionClose: alertOnPositionClose.value,
          alertOnProfitTarget: alertOnProfitTarget.value,
          alertOnStopLoss: alertOnStopLoss.value,
          alertOnDailyLossLimit: alertOnDailyLossLimit.value,
          alertOnRiskRuleBreach: alertOnRiskRuleBreach.value,
          dailyPnLAlertThreshold: dailyPnLAlertThreshold.value
        }
      },
      display: {
        theme: theme.value,
        chartDefaultTimeframe: chartDefaultTimeframe.value,
        chartShowVolume: chartShowVolume.value,
        chartShowIndicators: chartShowIndicators.value,
        tableCompactMode: tableCompactMode.value,
        showGreeksInPositions: showGreeksInPositions.value,
        dashboardLayout: dashboardLayout.value
      },
      data: {
        dataRefreshInterval: dataRefreshInterval.value,
        historicalDataDays: historicalDataDays.value,
        cacheEnabled: cacheEnabled.value,
        cacheExpiry: cacheExpiry.value,
        autoBackup: autoBackup.value,
        backupFrequency: backupFrequency.value
      },
      account: {
        userName: userName.value,
        userEmail: userEmail.value,
        sessionTimeout: sessionTimeout.value,
        twoFactorEnabled: twoFactorEnabled.value,
        autoLogout: autoLogout.value
      }
    }
  }
  
  function importSettings(settings) {
    if (settings.api) {
      schwabApiKey.value = settings.api.schwabApiKey
      schwabCallbackUrl.value = settings.api.schwabCallbackUrl
      apiRateLimit.value = settings.api.apiRateLimit
      autoReconnect.value = settings.api.autoReconnect
    }
    if (settings.notifications) {
      updateNotificationSettings(settings.notifications)
      if (settings.notifications.alerts) {
        updateAlertThresholds(settings.notifications.alerts)
      }
    }
    if (settings.display) {
      updateDisplayPreferences(settings.display)
    }
    if (settings.data) {
      updateDataSettings(settings.data)
    }
    if (settings.account) {
      updateAccountSettings(settings.account)
    }
  }
  
  return {
    // API
    schwabApiConnected,
    schwabApiKey,
    schwabApiSecret,
    schwabCallbackUrl,
    apiRateLimit,
    apiRateLimitUsed,
    lastApiCall,
    autoReconnect,
    
    // Notifications
    emailNotifications,
    emailAddress,
    smsNotifications,
    smsNumber,
    
    // Alerts
    alertOnPositionOpen,
    alertOnPositionClose,
    alertOnProfitTarget,
    alertOnStopLoss,
    alertOnDailyLossLimit,
    alertOnRiskRuleBreach,
    dailyPnLAlertThreshold,
    
    // Display
    theme,
    chartDefaultTimeframe,
    chartShowVolume,
    chartShowIndicators,
    tableCompactMode,
    showGreeksInPositions,
    dashboardLayout,
    
    // Data
    dataRefreshInterval,
    historicalDataDays,
    cacheEnabled,
    cacheExpiry,
    autoBackup,
    backupFrequency,
    
    // Account
    userName,
    userEmail,
    sessionTimeout,
    twoFactorEnabled,
    autoLogout,
    
    // Investment Profile
    investmentProfile,
    loadInvestmentProfile,
    saveInvestmentProfile,

    // Actions
    updateSchwabApi,
    testSchwabConnection,
    disconnectSchwabApi,
    updateNotificationSettings,
    updateAlertThresholds,
    updateDisplayPreferences,
    updateDataSettings,
    updateAccountSettings,
    exportSettings,
    importSettings
  }
})
