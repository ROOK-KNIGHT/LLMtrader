import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useRiskStore = defineStore('risk', () => {
  // Portfolio-level risk metrics
  const nav = ref(142847)
  const var95 = ref(-2841)
  const cvar99 = ref(-4126)
  const sharpeRatio = ref(1.82)
  const sortinoRatio = ref(2.15)
  const netDelta = ref(42.3)
  const portfolioBeta = ref(1.12)
  const maxDrawdown = ref(-3.2)
  const marginUsed = ref(34)
  const riskScore = ref(6.2)
  
  // Aggregate Greeks
  const aggregateGreeks = ref({
    delta: 42.3,
    gamma: 8.4,
    theta: -87,
    vega: 215,
    rho: -12,
    charm: -0.03
  })
  
  // Options positions with Greeks
  const optionsPositions = ref([
    {
      id: 1,
      symbol: 'AAPL 250321C185',
      type: 'Call',
      dte: 14,
      delta: 0.62,
      gamma: 0.08,
      theta: -12.4,
      vega: 0.15,
      iv: 32,
      ivRank: 68,
      maxLoss: 1600,
      probITM: 58
    },
    {
      id: 2,
      symbol: 'NVDA 250328P880',
      type: 'Put',
      dte: 21,
      delta: -0.45,
      gamma: 0.06,
      theta: -18.2,
      vega: 0.42,
      iv: 45,
      ivRank: 82,
      maxLoss: 3720,
      probITM: 42
    },
    {
      id: 3,
      symbol: 'TSLA 250404C875',
      type: 'Call',
      dte: 28,
      delta: 0.55,
      gamma: 0.05,
      theta: -22.1,
      vega: 0.38,
      iv: 52,
      ivRank: 71,
      maxLoss: 3120,
      probITM: 51
    },
    {
      id: 4,
      symbol: 'SPY 250411C520',
      type: 'Call',
      dte: 35,
      delta: 0.48,
      gamma: 0.03,
      theta: -8.5,
      vega: 0.12,
      iv: 18,
      ivRank: 45,
      maxLoss: 2850,
      probITM: 46
    }
  ])
  
  // Equity positions
  const equityPositions = ref([
    {
      id: 1,
      symbol: 'AAPL',
      beta: 1.18,
      sector: 'Technology',
      weight: 22,
      atr: 4.50,
      distTo200MA: 8.2,
      rsi: 62,
      maxDD30d: -4.1,
      sharpe: 1.45
    },
    {
      id: 2,
      symbol: 'SPY',
      beta: 1.00,
      sector: 'Index',
      weight: 35,
      atr: 3.20,
      distTo200MA: 5.1,
      rsi: 58,
      maxDD30d: -2.8,
      sharpe: 1.82
    },
    {
      id: 3,
      symbol: 'NVDA',
      beta: 1.45,
      sector: 'Technology',
      weight: 18,
      atr: 12.80,
      distTo200MA: 12.5,
      rsi: 68,
      maxDD30d: -6.2,
      sharpe: 1.28
    },
    {
      id: 4,
      symbol: 'TSLA',
      beta: 1.92,
      sector: 'Consumer Cyclical',
      weight: 15,
      atr: 18.40,
      distTo200MA: -2.3,
      rsi: 45,
      maxDD30d: -8.5,
      sharpe: 0.95
    }
  ])
  
  // Sector exposure
  const sectorExposure = ref([
    { sector: 'Technology', weight: 40, color: '#ff9500' },
    { sector: 'Index', weight: 35, color: '#00ff00' },
    { sector: 'Consumer Cyclical', weight: 15, color: '#00ffff' },
    { sector: 'Cash', weight: 10, color: '#996600' }
  ])
  
  // Asset class exposure
  const assetClassExposure = ref([
    { class: 'Options', weight: 30, color: '#ff9500' },
    { class: 'Equities', weight: 55, color: '#00ff00' },
    { class: 'ETFs', weight: 5, color: '#00ffff' },
    { class: 'Cash', weight: 10, color: '#996600' }
  ])
  
  // Correlation matrix
  const correlationMatrix = ref([
    { symbol1: 'AAPL', symbol2: 'NVDA', correlation: 0.82 },
    { symbol1: 'AAPL', symbol2: 'TSLA', correlation: 0.45 },
    { symbol1: 'AAPL', symbol2: 'SPY', correlation: 0.68 },
    { symbol1: 'NVDA', symbol2: 'TSLA', correlation: 0.52 },
    { symbol1: 'NVDA', symbol2: 'SPY', correlation: 0.71 },
    { symbol1: 'TSLA', symbol2: 'SPY', correlation: 0.38 }
  ])
  
  // Stress test scenarios
  const stressScenarios = ref([
    {
      id: 1,
      name: 'SPX -5% Flash Crash',
      impact: -7142,
      impactPct: -5.0,
      worstPosition: 'AAPL C185',
      worstLoss: -2800
    },
    {
      id: 2,
      name: 'Rate Hike +50bps',
      impact: -3200,
      impactPct: -2.2,
      worstPosition: 'NVDA P880',
      worstLoss: -1450
    },
    {
      id: 3,
      name: 'VIX Spike to 35',
      impact: 1800,
      impactPct: 1.3,
      worstPosition: 'SPY C520',
      worstLoss: 2100
    },
    {
      id: 4,
      name: 'Tech Sector -10%',
      impact: -9500,
      impactPct: -6.7,
      worstPosition: 'TSLA C875',
      worstLoss: -3120
    },
    {
      id: 5,
      name: '2020 COVID-style Crash',
      impact: -18400,
      impactPct: -12.9,
      worstPosition: 'Portfolio-wide',
      worstLoss: -18400
    }
  ])
  
  // Risk rules
  const riskRules = ref([
    {
      id: 1,
      name: 'Daily Loss Limit',
      scope: 'Account',
      status: 'OK',
      limit: -2000,
      current: -128,
      action: 'HALT ALL',
      enabled: true
    },
    {
      id: 2,
      name: 'Weekly Loss Limit',
      scope: 'Account',
      status: 'OK',
      limit: -5000,
      current: 1247,
      action: 'HALT ALL',
      enabled: true
    },
    {
      id: 3,
      name: 'Max Position Size',
      scope: 'Per-Trade',
      status: 'OK',
      limit: 5,
      current: 3.2,
      action: 'BLOCK',
      enabled: true,
      unit: '%'
    },
    {
      id: 4,
      name: 'Net Delta Limit',
      scope: 'Options',
      status: 'WARN',
      limit: 50,
      current: 42.3,
      action: 'ALERT',
      enabled: true
    },
    {
      id: 5,
      name: 'Daily Theta Burn',
      scope: 'Options',
      status: 'OK',
      limit: -150,
      current: -87,
      action: 'ALERT',
      enabled: true,
      unit: '$/day'
    },
    {
      id: 6,
      name: 'Vega Exposure',
      scope: 'Options',
      status: 'OK',
      limit: 500,
      current: 215,
      action: 'ALERT',
      enabled: true,
      unit: '$'
    },
    {
      id: 7,
      name: 'Sector Concentration',
      scope: 'Equity',
      status: 'OK',
      limit: 30,
      current: 22,
      action: 'ALERT',
      enabled: true,
      unit: '%'
    },
    {
      id: 8,
      name: 'Portfolio Beta',
      scope: 'Equity',
      status: 'OK',
      limit: 1.5,
      current: 1.12,
      action: 'REDUCE',
      enabled: true
    },
    {
      id: 9,
      name: 'Correlation Cluster',
      scope: 'All',
      status: 'WARN',
      limit: 3,
      current: 2,
      action: 'ALERT',
      enabled: true,
      note: '2 positions @ 0.82 correlation'
    },
    {
      id: 10,
      name: 'Margin Utilization',
      scope: 'Account',
      status: 'OK',
      limit: 70,
      current: 34,
      action: 'BLOCK',
      enabled: true,
      unit: '%'
    },
    {
      id: 11,
      name: 'DTE Minimum',
      scope: 'Options',
      status: 'OK',
      limit: 7,
      current: 14,
      action: 'BLOCK',
      enabled: true,
      unit: 'days'
    },
    {
      id: 12,
      name: 'Max Drawdown Circuit Breaker',
      scope: 'Account',
      status: 'OK',
      limit: -10,
      current: -3.2,
      action: 'LIQUIDATE',
      enabled: true,
      unit: '%'
    },
    {
      id: 13,
      name: 'Overnight Exposure Limit',
      scope: 'All',
      status: 'OK',
      limit: 80,
      current: 65,
      action: 'REDUCE',
      enabled: true,
      unit: '%'
    },
    {
      id: 14,
      name: 'Concentration (Herfindahl)',
      scope: 'All',
      status: 'OK',
      limit: 0.25,
      current: 0.18,
      action: 'ALERT',
      enabled: true
    }
  ])
  
  // Computed
  const totalOptionsExposure = computed(() => {
    return optionsPositions.value.reduce((sum, pos) => sum + pos.maxLoss, 0)
  })
  
  const totalEquityExposure = computed(() => {
    return equityPositions.value.reduce((sum, pos) => sum + (nav.value * pos.weight / 100), 0)
  })
  
  const activeRules = computed(() => {
    return riskRules.value.filter(rule => rule.enabled)
  })
  
  const breachedRules = computed(() => {
    return riskRules.value.filter(rule => rule.status === 'BREACH')
  })
  
  const warningRules = computed(() => {
    return riskRules.value.filter(rule => rule.status === 'WARN')
  })
  
  // Actions
  function toggleRule(ruleId) {
    const rule = riskRules.value.find(r => r.id === ruleId)
    if (rule) {
      rule.enabled = !rule.enabled
    }
  }
  
  function updateRuleLimit(ruleId, newLimit) {
    const rule = riskRules.value.find(r => r.id === ruleId)
    if (rule) {
      rule.limit = newLimit
    }
  }
  
  return {
    // Portfolio metrics
    nav,
    var95,
    cvar99,
    sharpeRatio,
    sortinoRatio,
    netDelta,
    portfolioBeta,
    maxDrawdown,
    marginUsed,
    riskScore,
    
    // Greeks
    aggregateGreeks,
    optionsPositions,
    
    // Equities
    equityPositions,
    
    // Exposure
    sectorExposure,
    assetClassExposure,
    correlationMatrix,
    
    // Stress tests
    stressScenarios,
    
    // Rules
    riskRules,
    activeRules,
    breachedRules,
    warningRules,
    
    // Computed
    totalOptionsExposure,
    totalEquityExposure,
    
    // Actions
    toggleRule,
    updateRuleLimit
  }
})
