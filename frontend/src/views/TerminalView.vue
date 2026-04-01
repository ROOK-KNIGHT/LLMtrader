<template>
  <div class="terminal-grid">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="flex items-center gap-md">
        <h1 class="retro-title" style="font-size: 1.5rem; font-weight: 700; color: var(--accent-primary);">
          VOLFLOW AGENT
        </h1>
        <div class="flex items-center gap-sm">
          <span class="badge badge-success">{{ marketStore.marketStatus }}</span>
          <span class="text-secondary" style="font-size: 0.875rem;">
            {{ currentTime }}
          </span>
        </div>
      </div>
      
      <div class="flex items-center gap-md">
        <!-- Market Indices -->
        <div class="flex gap-md mono" style="font-size: 0.875rem;">
          <div v-for="(data, symbol) in marketStore.marketIndices" :key="symbol">
            <span class="text-secondary">{{ symbol }}</span>
            <span :class="data.change >= 0 ? 'text-profit' : 'text-loss'" style="margin-left: 0.5rem;">
              {{ data.price.toFixed(2) }}
            </span>
            <span :class="data.change >= 0 ? 'text-profit' : 'text-loss'" style="margin-left: 0.25rem; font-size: 0.75rem;">
              {{ data.change >= 0 ? '+' : '' }}{{ data.changePct.toFixed(2) }}%
            </span>
          </div>
        </div>
        
        <!-- User Menu -->
        <div class="flex items-center gap-sm">
          <span class="text-secondary" style="font-size: 0.875rem;">{{ authStore.userName }}</span>
          <button class="btn btn-sm btn-secondary" @click="authStore.logout">Logout</button>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <!-- Prompt Library Panel -->
      <div class="panel" style="grid-column: 1 / 2; grid-row: 1 / 2;">
        <div class="panel-header">
          <div class="panel-title">Quick Actions</div>
        </div>
        <div class="panel-body" style="padding: 0;">
          <PromptLibrary @select-prompt="handlePromptSelect" />
        </div>
      </div>
      
      <!-- AI Chat Panel -->
      <div class="panel" style="grid-column: 1 / 2; grid-row: 2 / 3;">
        <div class="panel-header">
          <div class="panel-title">AI Trading Assistant</div>
          <div class="panel-actions">
            <select v-model="aiStore.selectedModel" class="input" style="width: 120px; padding: 0.25rem 0.5rem;">
              <option value="claude">Claude</option>
              <option value="grok">Grok</option>
              <option value="gemini">Gemini</option>
            </select>
            <button 
              class="btn btn-sm" 
              :class="aiStore.debateMode ? 'btn-primary' : 'btn-secondary'"
              @click="aiStore.toggleDebateMode"
            >
              {{ aiStore.debateMode ? 'Debate ON' : 'Single' }}
            </button>
          </div>
        </div>
        <div class="panel-body" style="display: flex; flex-direction: column; padding: 0;">
          <!-- Messages -->
          <div ref="messagesContainer" style="flex: 1; overflow-y: auto; padding: 1rem;">
            <div v-for="message in aiStore.messages" :key="message.id" style="margin-bottom: 1.5rem;">
              <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                <div 
                  style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"
                  :style="{ background: message.role === 'user' ? 'var(--accent-primary)' : 'var(--accent-secondary)' }"
                >
                  {{ message.role === 'user' ? 'U' : 'AI' }}
                </div>
                <div style="flex: 1;">
                  <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; font-size: 0.875rem;">
                      {{ message.role === 'user' ? 'You' : message.model?.toUpperCase() || 'AI' }}
                    </span>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">
                      {{ formatTime(message.timestamp) }}
                    </span>
                  </div>
                  <div style="color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap;">
                    {{ message.content }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Loading indicator -->
            <div v-if="aiStore.isProcessing" style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem;">
              <div class="spinner"></div>
              <span style="color: var(--text-secondary); font-size: 0.875rem;">AI is thinking...</span>
            </div>
          </div>
          
          <!-- Input -->
          <div style="border-top: 1px solid var(--border-primary); padding: 1rem;">
            <form @submit.prevent="handleSendMessage" style="display: flex; gap: 0.5rem;">
              <input 
                v-model="messageInput"
                type="text"
                class="input"
                placeholder="Ask me anything about markets, trades, or your portfolio..."
                :disabled="aiStore.isProcessing"
              />
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="!messageInput.trim() || aiStore.isProcessing"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Portfolio Panel -->
      <div class="panel" style="grid-column: 2 / 3; grid-row: 1 / 2;">
        <div class="panel-header">
          <div class="panel-title">Portfolio</div>
        </div>
        <div class="panel-body" style="padding: 1rem;">
          <!-- Account Summary -->
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
            <div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Account Balance</div>
              <div class="mono" style="font-size: 1.25rem; font-weight: 600;">
                ${{ portfolioStore.accountBalance.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
              </div>
            </div>
            <div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Total P&L</div>
              <div class="mono" style="font-size: 1.25rem; font-weight: 600;" :class="portfolioStore.totalPnL >= 0 ? 'text-profit' : 'text-loss'">
                {{ portfolioStore.totalPnL >= 0 ? '+' : '' }}${{ Math.abs(portfolioStore.totalPnL).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
              </div>
            </div>
          </div>
          
          <!-- Positions Table -->
          <div style="overflow-x: auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Contracts</th>
                  <th>P&L</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="position in portfolioStore.positions" :key="position.id">
                  <td class="font-bold">{{ position.symbol }}</td>
                  <td>
                    <span class="badge" :class="position.type === 'CALL' ? 'badge-success' : 'badge-danger'">
                      {{ position.type }}
                    </span>
                  </td>
                  <td class="mono">{{ position.contracts }}</td>
                  <td class="mono" :class="position.pnl >= 0 ? 'text-profit' : 'text-loss'">
                    {{ position.pnl >= 0 ? '+' : '' }}${{ Math.abs(position.pnl).toFixed(2) }}
                    <span style="font-size: 0.75rem; margin-left: 0.25rem;">
                      ({{ position.pnl_pct >= 0 ? '+' : '' }}{{ position.pnl_pct.toFixed(1) }}%)
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- Chart Panel -->
      <div class="panel" style="grid-column: 2 / 3; grid-row: 2 / 3;">
        <div class="panel-header">
          <div class="panel-title">{{ marketStore.selectedSymbol }} Chart</div>
        </div>
        <div class="panel-body" style="padding: 0;">
          <div ref="chartContainer" style="width: 100%; height: 100%;"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePortfolioStore } from '@/stores/portfolio'
import { useAIStore } from '@/stores/ai'
import { useMarketStore } from '@/stores/market'
import { createChart } from 'lightweight-charts'
import dayjs from 'dayjs'
import PromptLibrary from '@/components/terminal/PromptLibrary.vue'

const authStore = useAuthStore()
const portfolioStore = usePortfolioStore()
const aiStore = useAIStore()
const marketStore = useMarketStore()

const messageInput = ref('')
const messagesContainer = ref(null)
const chartContainer = ref(null)
const currentTime = ref(dayjs().format('MMM DD, YYYY HH:mm:ss'))
let chart = null

// Update time every second
setInterval(() => {
  currentTime.value = dayjs().format('MMM DD, YYYY HH:mm:ss')
}, 1000)

function formatTime(timestamp) {
  return dayjs(timestamp).format('HH:mm')
}

async function handleSendMessage() {
  if (!messageInput.value.trim()) return
  
  await aiStore.sendMessage(messageInput.value)
  messageInput.value = ''
  
  // Scroll to bottom
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function handlePromptSelect(prompt) {
  messageInput.value = prompt.prompt
  handleSendMessage()
}

function initChart() {
  if (!chartContainer.value) return
  
  chart = createChart(chartContainer.value, {
    layout: {
      background: { color: 'transparent' },
      textColor: '#64748b'
    },
    grid: {
      vertLines: { color: '#1e293b' },
      horzLines: { color: '#1e293b' }
    },
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    timeScale: {
      timeVisible: true,
      secondsVisible: false
    }
  })
  
  const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#ef4444',
    borderVisible: false,
    wickUpColor: '#10b981',
    wickDownColor: '#ef4444'
  })
  
  candlestickSeries.setData(marketStore.chartData)
  
  // Handle resize
  const resizeObserver = new ResizeObserver(entries => {
    if (chart && entries.length > 0) {
      const { width, height } = entries[0].contentRect
      chart.applyOptions({ width, height })
    }
  })
  
  resizeObserver.observe(chartContainer.value)
}

onMounted(() => {
  initChart()
})

// Watch for symbol changes
watch(() => marketStore.selectedSymbol, () => {
  if (chart) {
    chart.remove()
    initChart()
  }
})
</script>
