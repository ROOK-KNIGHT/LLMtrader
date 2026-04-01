import { defineStore } from 'pinia'
import { ref } from 'vue'

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
