import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMarketStore = defineStore('market', () => {
  // State
  const watchlist = ref([])
  const marketStatus = ref('OPEN')
  const marketIndices = ref({})
  const selectedSymbol = ref('AAPL')
  const chartData = ref([])
  
  // Mock watchlist
  const mockWatchlist = [
    { symbol: 'AAPL', price: 242.50, change: 2.85, changePct: 1.19, volume: 52000000 },
    { symbol: 'TSLA', price: 875.25, change: -12.50, changePct: -1.41, volume: 38000000 },
    { symbol: 'NVDA', price: 1142.75, change: 18.25, changePct: 1.62, volume: 45000000 },
    { symbol: 'MSFT', price: 428.90, change: 3.40, changePct: 0.80, volume: 28000000 },
    { symbol: 'GOOGL', price: 178.50, change: -1.25, changePct: -0.70, volume: 22000000 }
  ]
  
  const mockIndices = {
    SPY: { price: 518.50, change: 2.15, changePct: 0.42 },
    QQQ: { price: 445.75, change: 3.80, changePct: 0.86 },
    VIX: { price: 14.25, change: -0.50, changePct: -3.39 }
  }
  
  // Mock chart data (OHLC)
  const mockChartData = generateMockChartData()
  
  // Getters
  const selectedSymbolData = computed(() => 
    watchlist.value.find(item => item.symbol === selectedSymbol.value)
  )
  
  const isMarketOpen = computed(() => marketStatus.value === 'OPEN')
  
  // Actions
  function loadWatchlist() {
    watchlist.value = mockWatchlist
    marketIndices.value = mockIndices
    chartData.value = mockChartData
  }
  
  function setSelectedSymbol(symbol) {
    selectedSymbol.value = symbol
    chartData.value = generateMockChartData()
  }
  
  function addToWatchlist(symbol) {
    if (!watchlist.value.find(item => item.symbol === symbol)) {
      watchlist.value.push({
        symbol,
        price: 0,
        change: 0,
        changePct: 0,
        volume: 0
      })
    }
  }
  
  function removeFromWatchlist(symbol) {
    watchlist.value = watchlist.value.filter(item => item.symbol !== symbol)
  }
  
  function updatePrices() {
    // Simulate real-time price updates
    watchlist.value = watchlist.value.map(item => ({
      ...item,
      price: item.price + (Math.random() - 0.5) * 2,
      change: item.change + (Math.random() - 0.5) * 0.5
    }))
  }
  
  // Initialize
  loadWatchlist()
  
  // Simulate real-time updates every 3 seconds
  setInterval(updatePrices, 3000)
  
  return {
    watchlist,
    marketStatus,
    marketIndices,
    selectedSymbol,
    chartData,
    selectedSymbolData,
    isMarketOpen,
    loadWatchlist,
    setSelectedSymbol,
    addToWatchlist,
    removeFromWatchlist,
    updatePrices
  }
})

// Helper function to generate mock OHLC data
function generateMockChartData() {
  const data = []
  const now = Date.now()
  const oneDay = 24 * 60 * 60 * 1000
  let price = 240
  
  for (let i = 90; i >= 0; i--) {
    const time = now - (i * oneDay)
    const open = price
    const change = (Math.random() - 0.5) * 10
    const close = price + change
    const high = Math.max(open, close) + Math.random() * 3
    const low = Math.min(open, close) - Math.random() * 3
    
    data.push({
      time: Math.floor(time / 1000),
      open,
      high,
      low,
      close
    })
    
    price = close
  }
  
  return data
}
