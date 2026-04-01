import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usePanelStore } from './panels'

export const useAIStore = defineStore('ai', () => {
  // State
  const messages = ref([])
  const isProcessing = ref(false)
  const selectedModel = ref('claude') // claude, grok, gemini
  const debateMode = ref(false)
  
  // Mock conversation history
  const mockMessages = [
    {
      id: 1,
      role: 'assistant',
      model: 'claude',
      content: 'Welcome to VolFlow Agent! I\'m your Volflow Ecosystem AI trading assistant. I can help you analyze markets, find trade opportunities, and manage your portfolio. Try asking me about a stock or select a pre-screened prompt from the library.',
      timestamp: new Date(Date.now() - 3600000)
    }
  ]
  
  // Getters
  const conversationHistory = computed(() => messages.value)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])
  
  // Actions
  async function sendMessage(content) {
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    isProcessing.value = true
    
    // Simulate AI response
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      model: selectedModel.value,
      content: generateMockResponse(content),
      timestamp: new Date()
    }
    messages.value.push(aiMessage)
    
    isProcessing.value = false
  }
  
  function generateMockResponse(userInput) {
    const input = userInput.toLowerCase()
    
    // Check for panel-triggering keywords
    if (input.includes('dark pool') || input.includes('darkpool')) {
      // Trigger dark pool panel
      const panelStore = usePanelStore()
      const html = `
        <div style="font-family: 'VT323', monospace; color: #e0e0e0;">
          <h3 style="color: #ff9500; text-shadow: 0 0 8px #ff9500; margin-bottom: 1rem;">AAPL DARK POOL ACTIVITY</h3>
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid #333;">
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">TIME</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">SIZE</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">PRICE</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">SIGNAL</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">10:32</td>
                <td style="padding: 0.5rem;">$12.4M</td>
                <td style="padding: 0.5rem;">$189.50</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bullish">BULLISH</span> Above VWAP</td>
              </tr>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">10:18</td>
                <td style="padding: 0.5rem;">$8.7M</td>
                <td style="padding: 0.5rem;">$188.90</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bullish">BULLISH</span> Above VWAP</td>
              </tr>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">09:54</td>
                <td style="padding: 0.5rem;">$15.2M</td>
                <td style="padding: 0.5rem;">$187.20</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bearish">BEARISH</span> Below VWAP</td>
              </tr>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">09:41</td>
                <td style="padding: 0.5rem;">$6.3M</td>
                <td style="padding: 0.5rem;">$188.50</td>
                <td style="padding: 0.5rem;"><span class="badge badge-neutral">NEUTRAL</span> At VWAP</td>
              </tr>
            </tbody>
          </table>
          <div style="margin-top: 1.5rem; padding: 1rem; background: #1a1a1a; border: 1px solid #333; border-radius: 4px;">
            <div style="font-size: 0.9rem; color: #999; margin-bottom: 0.5rem;">NET SENTIMENT</div>
            <div style="font-size: 1.2rem; color: #00ff00;">BULLISH</div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #999;">
              Total Volume: $42.6M | Avg Price: $188.53 | VWAP: $188.20
            </div>
          </div>
        </div>
      `
      panelStore.open('AAPL Dark Pool Activity', html)
      return 'I\'ve opened a dark pool activity panel for AAPL. The data shows strong bullish sentiment with $42.6M in total volume, mostly above VWAP.'
    }
    
    if (input.includes('options flow') || input.includes('unusual activity')) {
      // Trigger options flow panel
      const panelStore = usePanelStore()
      const html = `
        <div style="font-family: 'VT323', monospace; color: #e0e0e0;">
          <h3 style="color: #ff9500; text-shadow: 0 0 8px #ff9500; margin-bottom: 1rem;">UNUSUAL OPTIONS ACTIVITY</h3>
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid #333;">
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">TIME</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">SYMBOL</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">STRIKE</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">TYPE</th>
                <th style="padding: 0.5rem; text-align: left; color: #999; font-size: 0.85rem;">PREMIUM</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">10:32</td>
                <td style="padding: 0.5rem; font-weight: bold;">AAPL</td>
                <td style="padding: 0.5rem;">$190 C Apr 18</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bullish">SWEEP BUY</span></td>
                <td style="padding: 0.5rem; color: #00ff00;">$2.8M</td>
              </tr>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">10:28</td>
                <td style="padding: 0.5rem; font-weight: bold;">TSLA</td>
                <td style="padding: 0.5rem;">$850 P Apr 11</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bearish">BLOCK</span></td>
                <td style="padding: 0.5rem; color: #ff0000;">$1.2M</td>
              </tr>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">10:25</td>
                <td style="padding: 0.5rem; font-weight: bold;">NVDA</td>
                <td style="padding: 0.5rem;">$950 C May 16</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bullish">SWEEP BUY</span></td>
                <td style="padding: 0.5rem; color: #00ff00;">$4.1M</td>
              </tr>
              <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 0.5rem;">10:21</td>
                <td style="padding: 0.5rem; font-weight: bold;">SPY</td>
                <td style="padding: 0.5rem;">$510 P Apr 04</td>
                <td style="padding: 0.5rem;"><span class="badge badge-bearish">BLOCK</span></td>
                <td style="padding: 0.5rem; color: #ff0000;">$3.6M</td>
              </tr>
            </tbody>
          </table>
          <div style="margin-top: 1.5rem; padding: 1rem; background: #1a1a1a; border: 1px solid #333; border-radius: 4px;">
            <div style="font-size: 0.9rem; color: #999; margin-bottom: 0.5rem;">MARKET SENTIMENT</div>
            <div style="display: flex; gap: 1rem;">
              <div>
                <div style="font-size: 0.85rem; color: #999;">Bullish Flow</div>
                <div style="font-size: 1.1rem; color: #00ff00;">$6.9M (60%)</div>
              </div>
              <div>
                <div style="font-size: 0.85rem; color: #999;">Bearish Flow</div>
                <div style="font-size: 1.1rem; color: #ff0000;">$4.8M (40%)</div>
              </div>
            </div>
          </div>
        </div>
      `
      panelStore.open('Unusual Options Activity', html)
      return 'I\'ve opened an unusual options activity panel. Currently seeing strong bullish flow with $6.9M in call sweeps vs $4.8M in put blocks.'
    }
    
    if (input.includes('aapl') || input.includes('apple')) {
      return `**AAPL Analysis**

**Current Price:** $242.50 (+1.2%)

**Technical Setup:**
- Trading above all major moving averages (bullish)
- RSI: 62 (neutral-bullish)
- Volume: Above 20-day average (+15%)

**Sentiment:**
- StockTwits: 68% bullish (strong)
- Recent catalyst: New product launch next week

**Options Flow:**
- Heavy call buying at $245 strike (Apr 18 expiry)
- Implied volatility: 28% (slightly elevated)

**AI Recommendation:**
Consider a **long call spread** targeting the product launch event. Entry at current levels with a stop below $238 support.

Would you like me to execute this trade or analyze further?`
    }
    
    if (input.includes('portfolio') || input.includes('positions')) {
      return `**Portfolio Review**

**Current Positions:** 3 active
**Total P&L:** +$1,425.00 (+1.9%)
**Win Rate:** 66.7%

**Position Breakdown:**
1. **AAPL Call** - Up 26% (take profit zone)
2. **TSLA Put** - Down 19.6% (monitor closely)
3. **NVDA Call** - Up 16.1% (holding well)

**Recommendations:**
- Consider taking profits on AAPL (hit 25% target)
- TSLA position approaching stop loss - review thesis
- NVDA showing strength - let it run with trailing stop

Would you like me to execute any of these recommendations?`
    }
    
    if (input.includes('scan') || input.includes('find') || input.includes('opportunities')) {
      return `**Market Scan Results**

**Top 3 Setups Right Now:**

1. **NVDA - Volatility Skew Anomaly**
   - HV/IV ratio: 1.45 (options underpriced)
   - ATM calls 15% cheaper than historical
   - Catalyst: Earnings in 2 weeks
   - **Edge:** Long volatility play

2. **TSLA - Mean Reversion**
   - RSI: 28 (oversold)
   - 3x volume spike (institutional buying)
   - At 200-day MA support
   - **Edge:** Bounce play with defined risk

3. **SPY - Gamma Squeeze Zone**
   - Heavy call OI at $520 strike
   - Current: $518.50
   - Dealer gamma flip at $520
   - **Edge:** Breakout acceleration

Which setup would you like to explore further?`
    }
    
    return `I understand you're asking about "${userInput}". 

I can help you with:
- **Market analysis** for any stock
- **Trade ideas** based on technical/fundamental data
- **Portfolio management** and position reviews
- **Risk assessment** for potential trades
- **Options strategies** tailored to your goals

Try asking me something specific, or select a pre-screened prompt from the library on the right!`
  }
  
  function clearConversation() {
    messages.value = [...mockMessages]
  }
  
  function setModel(model) {
    selectedModel.value = model
  }
  
  function toggleDebateMode() {
    debateMode.value = !debateMode.value
  }
  
  // Initialize
  messages.value = [...mockMessages]
  
  return {
    messages,
    isProcessing,
    selectedModel,
    debateMode,
    conversationHistory,
    lastMessage,
    sendMessage,
    clearConversation,
    setModel,
    toggleDebateMode
  }
})
