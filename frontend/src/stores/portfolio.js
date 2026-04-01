import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePortfolioStore = defineStore('portfolio', () => {
  // State
  const positions = ref([])
  const accountBalance = ref(0)
  const buyingPower = ref(0)
  const totalPnL = ref(0)
  const isLoading = ref(false)
  
  // Mock data
  const mockPositions = [
    {
      id: 1,
      symbol: 'AAPL',
      option_symbol: 'AAPL  260418C00230000',
      type: 'CALL',
      strike: 230,
      expiration: '2026-04-18',
      contracts: 5,
      entry_price: 12.50,
      current_price: 15.75,
      underlying_price: 242.50,
      pnl: 1625.00,
      pnl_pct: 26.0,
      strategy: 'AI Board - Momentum Scalp',
      days_held: 3
    },
    {
      id: 2,
      symbol: 'TSLA',
      option_symbol: 'TSLA  260425P00850000',
      type: 'PUT',
      strike: 850,
      expiration: '2026-04-25',
      contracts: 3,
      entry_price: 28.00,
      current_price: 22.50,
      underlying_price: 875.25,
      pnl: -1650.00,
      pnl_pct: -19.6,
      strategy: 'AI Board - Mean Reversion',
      days_held: 5
    },
    {
      id: 3,
      symbol: 'NVDA',
      option_symbol: 'NVDA  260411C01100000',
      type: 'CALL',
      strike: 1100,
      expiration: '2026-04-11',
      contracts: 2,
      entry_price: 45.00,
      current_price: 52.25,
      underlying_price: 1142.75,
      pnl: 1450.00,
      pnl_pct: 16.1,
      strategy: 'AI Board - Volatility Skew',
      days_held: 2
    }
  ]
  
  // Getters
  const totalPositions = computed(() => positions.value.length)
  const profitablePositions = computed(() => 
    positions.value.filter(p => p.pnl > 0).length
  )
  const losingPositions = computed(() => 
    positions.value.filter(p => p.pnl < 0).length
  )
  const winRate = computed(() => {
    if (totalPositions.value === 0) return 0
    return (profitablePositions.value / totalPositions.value) * 100
  })
  
  // Actions
  function loadPositions() {
    isLoading.value = true
    // Simulate API call
    setTimeout(() => {
      positions.value = mockPositions
      accountBalance.value = 125000.00
      buyingPower.value = 87500.00
      totalPnL.value = mockPositions.reduce((sum, p) => sum + p.pnl, 0)
      isLoading.value = false
    }, 500)
  }
  
  function updatePosition(id, updates) {
    const index = positions.value.findIndex(p => p.id === id)
    if (index !== -1) {
      positions.value[index] = { ...positions.value[index], ...updates }
    }
  }
  
  function removePosition(id) {
    positions.value = positions.value.filter(p => p.id !== id)
  }
  
  // Initialize
  loadPositions()
  
  return {
    positions,
    accountBalance,
    buyingPower,
    totalPnL,
    isLoading,
    totalPositions,
    profitablePositions,
    losingPositions,
    winRate,
    loadPositions,
    updatePosition,
    removePosition
  }
})
