<template>
  <div class="trading-dashboard">
    <!-- Top Navigation Bar -->
    <div class="top-nav">
      <div class="nav-left">
        <div class="logo">
          <span class="status-indicator"></span>
          <span class="retro-title">VOLFLOW</span>
        </div>
        <div class="search-box">
          <input 
            type="text" 
            placeholder="⌘K Search anything..." 
            class="search-input"
          />
        </div>
      </div>
      <div class="nav-right">
        <span class="status-badge live">Live</span>
        <span class="status-badge privacy">Privacy</span>
        <button class="nav-btn" @click="$router.push('/onboarding')" title="Schwab Settings">
          ⚙ Settings
        </button>
        <button class="nav-btn nav-btn-logout" @click="handleLogout" title="Logout">
          ⏻ Logout
        </button>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-nav">
      <div class="tab-nav-left">
        <button 
          :class="['tab-btn', 'ai-tab', { active: activeTab === 'ai' }]"
          @click="activeTab = 'ai'"
        >
          AI
        </button>
      </div>
      <div class="tab-nav-right">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="dashboard-content" v-if="activeTab === 'trade'">
      <!-- Account Banner -->
      <div class="account-banner">
        <div class="banner-stat">
          <div class="stat-value mono">${{ accountBalance.toLocaleString() }}</div>
        </div>
        <div class="banner-stat">
          <div class="stat-label">Day:</div>
          <div class="stat-value mono" :class="dayPnL >= 0 ? 'text-profit' : 'text-loss'">
            {{ dayPnL >= 0 ? '+' : '' }}${{ Math.abs(dayPnL).toLocaleString() }} 
            ({{ dayPnL >= 0 ? '+' : '' }}{{ dayPnLPct.toFixed(2) }}%)
          </div>
        </div>
        <div class="banner-stat">
          <div class="stat-label">Open P/L:</div>
          <div class="stat-value mono" :class="openPnL >= 0 ? 'text-profit' : 'text-loss'">
            {{ openPnL >= 0 ? '+' : '' }}${{ Math.abs(openPnL).toLocaleString() }}
          </div>
        </div>
        <div class="banner-stat">
          <div class="stat-value mono">{{ positionCount }} Pos</div>
        </div>
        <div class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: dailyTargetProgress + '%' }"></div>
          </div>
          <div class="progress-label">{{ dailyTargetProgress }}% of daily target achieved</div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <!-- Equity Curve -->
        <div class="chart-panel">
          <div class="panel-header">
            <div class="panel-title">EQUITY CURVE</div>
          </div>
          <div class="chart-body">
            <div ref="equityChartContainer" class="chart-container"></div>
            <div class="chart-controls">
              <button 
                v-for="period in ['1W', '1M', '3M', '6M', 'YTD', 'ALL']" 
                :key="period"
                class="chart-control-btn"
              >
                {{ period }}
              </button>
            </div>
          </div>
        </div>

        <!-- Intraday P&L -->
        <div class="chart-panel">
          <div class="panel-header">
            <div class="panel-title">INTRADAY P&L CHART</div>
          </div>
          <div class="chart-body">
            <div ref="intradayChartContainer" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- Positions Table -->
      <div class="positions-panel">
        <div class="panel-header">
          <div class="panel-title">POSITIONS</div>
        </div>
        <div class="positions-table-wrapper">
          <table class="positions-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Side</th>
                <th>Qty</th>
                <th>Entry</th>
                <th>Current</th>
                <th>P/L</th>
                <th>Stop</th>
                <th>TP</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="position in positions" :key="position.id">
                <td class="mono font-bold">{{ position.symbol }}</td>
                <td>
                  <span :class="['side-badge', position.side.toLowerCase()]">
                    {{ position.side }}
                  </span>
                </td>
                <td class="mono">{{ position.qty >= 0 ? '+' : '' }}{{ position.qty }}</td>
                <td class="mono">${{ position.entry.toFixed(2) }}</td>
                <td class="mono">${{ position.current.toFixed(2) }}</td>
                <td class="mono" :class="position.pnl >= 0 ? 'text-profit' : 'text-loss'">
                  {{ position.pnl >= 0 ? '+' : '' }}${{ Math.abs(position.pnl).toFixed(2) }}
                </td>
                <td class="mono">${{ position.stop.toFixed(2) }}</td>
                <td class="mono">${{ position.tp.toFixed(2) }}</td>
              </tr>
              <tr v-for="position in positions" :key="'viz-' + position.id" class="position-viz-row">
                <td colspan="8">
                  <div class="position-visualizer">
                    <div class="viz-track">
                      <div class="viz-range" :style="getVizRangeStyle(position)"></div>
                      <div class="viz-marker stop" :style="{ left: getStopPosition(position) + '%' }">
                        <span class="marker-label">stop</span>
                      </div>
                      <div class="viz-marker current" :style="{ left: getCurrentPosition(position) + '%' }">●</div>
                      <div class="viz-marker target" :style="{ left: getTargetPosition(position) + '%' }">
                        <span class="marker-label">target</span>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- AI Content Area -->
    <div class="ai-content" v-else-if="activeTab === 'ai'">
      <div class="ai-grid">
        <!-- Prompt Library -->
        <div class="panel ai-prompts-panel">
          <div class="panel-header">
            <div class="panel-title">Quick Actions</div>
          </div>
          <div class="panel-body" style="padding: 0;">
            <PromptLibrary @select-prompt="handlePromptSelect" />
          </div>
        </div>
        
        <!-- AI Chat -->
        <div class="panel ai-chat-panel" :class="{ 'with-side-panel': panelStore.isOpen }">
          <div class="panel-header">
            <div class="panel-title">AI Trading Assistant</div>
            <div class="panel-actions">
              <select v-model="aiStore.selectedModel" class="input" style="width: 120px; padding: 0.25rem 0.5rem;">
                <option value="claude">Claude</option>
                <option value="grok">Grok</option>
                <option value="gemini">Gemini</option>
              </select>
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
                    <div 
                      class="chat-message-content"
                      style="color: var(--text-secondary); line-height: 1.6;"
                      v-html="renderMessage(message.content)"
                    ></div>
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
        
        <!-- Dynamic Side Panel -->
        <SidePanel />
      </div>
    </div>

    <!-- Risk Content -->
    <div class="risk-content" v-else-if="activeTab === 'risk'">
      <RiskDashboard />
    </div>

    <!-- Config Content -->
    <div class="config-content" v-else-if="activeTab === 'conf'">
      <ConfigDashboard />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { createChart } from 'lightweight-charts'
import { useAIStore } from '@/stores/ai'
import { useAuthStore } from '@/stores/auth'
import PromptLibrary from '@/components/terminal/PromptLibrary.vue'
import RiskDashboard from '@/components/terminal/RiskDashboard.vue'
import ConfigDashboard from '@/components/terminal/ConfigDashboard.vue'
import SidePanel from '@/components/terminal/SidePanel.vue'
import { usePanelStore } from '@/stores/panels'
import dayjs from 'dayjs'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const router = useRouter()
const aiStore = useAIStore()
const authStore = useAuthStore()
const panelStore = usePanelStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
const messageInput = ref('')
const messagesContainer = ref(null)

const activeTab = ref('trade')

const tabs = [
  { id: 'trade', label: 'TRADE' },
  { id: 'risk', label: 'RISK' },
  { id: 'conf', label: 'CONF' }
]

// Account data
const accountBalance = ref(142847)
const dayPnL = ref(1247)
const dayPnLPct = ref(0.88)
const openPnL = ref(1175)
const positionCount = ref(4)
const dailyTargetProgress = ref(74)

// Positions data
const positions = ref([
  {
    id: 1,
    symbol: 'AAPL 250321C185',
    side: 'Long',
    qty: 5,
    entry: 3.20,
    current: 3.89,
    pnl: 347.20,
    stop: 2.10,
    tp: 4.80
  },
  {
    id: 2,
    symbol: 'NVDA 250328P880',
    side: 'Long',
    qty: 3,
    entry: 12.40,
    current: 11.97,
    pnl: -128.50,
    stop: 8.40,
    tp: 18.0
  },
  {
    id: 3,
    symbol: 'TSLA 250404C875',
    side: 'Long',
    qty: 2,
    entry: 15.60,
    current: 17.25,
    pnl: 330.00,
    stop: 11.20,
    tp: 22.40
  },
  {
    id: 4,
    symbol: 'SPY 250411C520',
    side: 'Long',
    qty: 10,
    entry: 2.85,
    current: 3.47,
    pnl: 620.00,
    stop: 1.90,
    tp: 4.50
  }
])

const equityChartContainer = ref(null)
const intradayChartContainer = ref(null)

// Position visualization helpers
function getStopPosition(position) {
  const range = position.tp - position.stop
  const stopOffset = 0
  return (stopOffset / range) * 100
}

function getCurrentPosition(position) {
  const range = position.tp - position.stop
  const currentOffset = position.current - position.stop
  return Math.max(0, Math.min(100, (currentOffset / range) * 100))
}

function getTargetPosition(position) {
  return 100
}

function getVizRangeStyle(position) {
  const stopPos = getStopPosition(position)
  const targetPos = getTargetPosition(position)
  return {
    left: stopPos + '%',
    width: (targetPos - stopPos) + '%'
  }
}

// Initialize charts
function initEquityChart() {
  if (!equityChartContainer.value) return
  
  const chart = createChart(equityChartContainer.value, {
    layout: {
      background: { color: 'transparent' },
      textColor: '#996600'
    },
    grid: {
      vertLines: { color: '#1a1a1a' },
      horzLines: { color: '#1a1a1a' }
    },
    width: equityChartContainer.value.clientWidth,
    height: 200,
    timeScale: {
      timeVisible: true,
      secondsVisible: false
    }
  })
  
  const lineSeries = chart.addLineSeries({
    color: '#ff9500',
    lineWidth: 2
  })
  
  // Mock equity curve data
  const data = []
  const now = Date.now() / 1000
  const oneDay = 24 * 60 * 60
  let value = 135000
  
  for (let i = 120; i >= 0; i--) {
    value += (Math.random() - 0.4) * 2000
    data.push({
      time: now - (i * oneDay),
      value: Math.max(130000, Math.min(145000, value))
    })
  }
  
  lineSeries.setData(data)
}

function initIntradayChart() {
  if (!intradayChartContainer.value) return
  
  const chart = createChart(intradayChartContainer.value, {
    layout: {
      background: { color: 'transparent' },
      textColor: '#996600'
    },
    grid: {
      vertLines: { color: '#1a1a1a' },
      horzLines: { color: '#1a1a1a' }
    },
    width: intradayChartContainer.value.clientWidth,
    height: 200,
    timeScale: {
      timeVisible: true,
      secondsVisible: false
    }
  })
  
  const lineSeries = chart.addLineSeries({
    color: '#00ff00',
    lineWidth: 2
  })
  
  // Mock intraday P&L data
  const data = []
  const now = Date.now() / 1000
  const marketOpen = now - (4 * 60 * 60) // 4 hours ago
  let pnl = 0
  
  for (let i = 0; i < 240; i++) {
    pnl += (Math.random() - 0.45) * 50
    data.push({
      time: marketOpen + (i * 60),
      value: pnl
    })
  }
  
  lineSeries.setData(data)
}

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

// ─── renderMessage: parse <sidepanel> tags + render markdown ───────────────
// Track which panel IDs have already been opened this session.
// This prevents re-renders from re-opening panels the user has dismissed.
const _openedPanelIds = new Set()

function _hashStr(str) {
  let hash = 0
  for (let i = 0; i < Math.min(str.length, 200); i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i)
    hash |= 0
  }
  return 'panel_' + Math.abs(hash).toString(36)
}

function renderMessage(content) {
  if (!content) return ''

  // Extract all <sidepanel title="...">...</sidepanel> blocks
  const sidepanelRegex = /<sidepanel\s+title="([^"]*)">([\s\S]*?)<\/sidepanel>/gi
  let match
  let lastPanelTitle = null
  let lastPanelHtml = null
  let lastPanelId = null

  // Collect all panels (open the last one found)
  while ((match = sidepanelRegex.exec(content)) !== null) {
    lastPanelTitle = match[1]
    lastPanelHtml = match[2].trim()
    lastPanelId = _hashStr(lastPanelTitle + lastPanelHtml)
  }

  // Only open the panel if:
  //   1. We found one in this message
  //   2. It hasn't been opened before (prevents re-render re-open)
  //   3. It hasn't been dismissed by the user
  if (lastPanelTitle && lastPanelHtml && lastPanelId) {
    if (!_openedPanelIds.has(lastPanelId) && !panelStore.isDismissed(lastPanelId)) {
      _openedPanelIds.add(lastPanelId)
      setTimeout(() => {
        panelStore.open(lastPanelTitle, lastPanelHtml, lastPanelId)
      }, 0)
    }
  }

  // Strip all sidepanel blocks from the chat text
  const cleanText = content.replace(/<sidepanel[\s\S]*?<\/sidepanel>/gi, '').trim()

  // Render remaining text as markdown, sanitize with DOMPurify
  // Allow SVG tags for inline charts
  const rawHtml = marked.parse(cleanText || '')
  return DOMPurify.sanitize(rawHtml, {
    ADD_TAGS: ['svg', 'path', 'rect', 'circle', 'line', 'polyline', 'polygon', 'text', 'g', 'defs', 'use'],
    ADD_ATTR: ['viewBox', 'xmlns', 'fill', 'stroke', 'stroke-width', 'd', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'x1', 'y1', 'x2', 'y2', 'points', 'transform', 'opacity', 'font-size', 'text-anchor', 'font-family']
  })
}

function handlePromptSelect(prompt) {
  messageInput.value = prompt.prompt
  handleSendMessage()
}

onMounted(() => {
  if (activeTab.value === 'trade') {
    initEquityChart()
    initIntradayChart()
  }
})
</script>

<style scoped>
.trading-dashboard {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  font-family: 'VT323', 'Share Tech Mono', monospace;
}

/* Top Navigation */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: var(--bg-secondary);
  border-bottom: 2px solid var(--border-accent);
  box-shadow: 0 0 10px rgba(255, 149, 0, 0.3);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent-primary);
  box-shadow: 0 0 10px var(--accent-primary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.search-box {
  width: 400px;
}

.search-input {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 0.5rem 1rem;
  color: var(--text-primary);
  font-family: 'VT323', monospace;
  font-size: 1.1rem;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.nav-right {
  display: flex;
  gap: 1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  letter-spacing: 0.1em;
}

.status-badge.live {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
  border: 1px solid #00ff00;
}

.status-badge.privacy {
  background: rgba(255, 149, 0, 0.2);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

/* Nav Buttons */
.nav-btn {
  padding: 0.25rem 0.75rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: 'VT323', monospace;
  font-size: 0.95rem;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.nav-btn-logout:hover {
  border-color: #ef4444;
  color: #ef4444;
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
}

.tab-nav-left {
  flex: 1;
  display: flex;
}

.ai-tab {
  margin-right: auto;
}

.tab-nav-right {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-family: 'VT323', monospace;
  font-size: 1.1rem;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all var(--transition-base);
}

.tab-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-accent);
}

.tab-btn.active {
  background: var(--accent-primary);
  color: #000;
  border-color: var(--accent-primary);
  box-shadow: 0 0 15px rgba(255, 149, 0, 0.5);
}

/* Dashboard Content */
.dashboard-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Account Banner */
.account-banner {
  background: var(--bg-secondary);
  border: 2px solid var(--border-accent);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 0 20px rgba(255, 149, 0, 0.3);
}

.banner-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 1rem;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-section {
  flex: 1;
  margin-left: auto;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  box-shadow: 0 0 10px var(--accent-primary);
  transition: width 0.3s ease;
}

.progress-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-align: right;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.chart-panel {
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
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.15em;
  text-shadow: 0 0 8px var(--accent-primary);
}

.chart-body {
  padding: 1rem;
}

.chart-container {
  width: 100%;
  height: 200px;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  justify-content: center;
}

.chart-control-btn {
  padding: 0.25rem 0.75rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: 'VT323', monospace;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-base);
}

.chart-control-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* Positions Panel */
.positions-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 0 10px rgba(255, 149, 0, 0.2);
}

.positions-table-wrapper {
  overflow-x: auto;
  padding: 1rem;
}

.positions-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'VT323', monospace;
}

.positions-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  color: var(--text-secondary);
  font-size: 1rem;
  letter-spacing: 0.1em;
  border-bottom: 1px solid var(--border-primary);
}

.positions-table td {
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.positions-table tbody tr:not(.position-viz-row) {
  border-bottom: 1px solid var(--border-primary);
}

.side-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  letter-spacing: 0.1em;
}

.side-badge.long {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
  border: 1px solid #00ff00;
}

.side-badge.short {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
  border: 1px solid #ff0000;
}

/* Position Visualizer */
.position-viz-row td {
  padding: 0.5rem 1rem 1rem 1rem;
}

.position-visualizer {
  width: 100%;
}

.viz-track {
  position: relative;
  height: 30px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: visible;
}

.viz-range {
  position: absolute;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, 
    rgba(255, 0, 0, 0.3) 0%, 
    rgba(255, 149, 0, 0.3) 50%, 
    rgba(0, 255, 0, 0.3) 100%
  );
  border-radius: var(--radius-sm);
}

.viz-marker {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2rem;
  color: var(--text-primary);
}

.viz-marker.stop {
  color: #ff0000;
  left: 0;
}

.viz-marker.current {
  color: var(--accent-primary);
  font-size: 1.5rem;
  text-shadow: 0 0 10px var(--accent-primary);
}

.viz-marker.target {
  color: #00ff00;
  left: 100%;
}

.marker-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.8rem;
  white-space: nowrap;
  color: var(--text-muted);
}

/* AI Content */
.ai-content {
  flex: 1;
  overflow: hidden;
  padding: 1.5rem;
}

.ai-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
  height: 100%;
  position: relative;
}

.ai-prompts-panel {
  height: 100%;
}

.ai-chat-panel {
  height: 100%;
  transition: margin-right 0.3s ease;
}

.ai-chat-panel.with-side-panel {
  margin-right: 500px;
}

.panel-actions {
  display: flex;
  gap: 0.5rem;
}

/* Risk Content */
.risk-content {
  flex: 1;
  overflow: hidden;
}

/* Config Content */
.config-content {
  flex: 1;
  overflow: hidden;
}

.placeholder-message {
  text-align: center;
  color: var(--text-secondary);
}

.placeholder-message h2 {
  font-size: 2rem;
  color: var(--accent-primary);
  margin-bottom: 1rem;
  text-shadow: 0 0 10px var(--accent-primary);
}

/* Chat message markdown rendering */
.chat-message-content :deep(p) {
  margin: 0.4rem 0;
}
.chat-message-content :deep(ul),
.chat-message-content :deep(ol) {
  margin: 0.4rem 0 0.4rem 1.2rem;
  padding: 0;
}
.chat-message-content :deep(li) {
  margin: 0.2rem 0;
}
.chat-message-content :deep(strong) {
  color: var(--accent-primary);
  font-weight: 700;
}
.chat-message-content :deep(em) {
  color: var(--text-primary);
  font-style: italic;
}
.chat-message-content :deep(h1),
.chat-message-content :deep(h2),
.chat-message-content :deep(h3) {
  color: var(--accent-primary);
  text-shadow: 0 0 8px var(--accent-primary);
  margin: 0.75rem 0 0.4rem 0;
  letter-spacing: 0.1em;
}
.chat-message-content :deep(code) {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: 3px;
  padding: 0.1rem 0.4rem;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.9em;
  color: var(--accent-primary);
}
.chat-message-content :deep(pre) {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}
.chat-message-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-primary);
}
.chat-message-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
  font-size: 0.95rem;
}
.chat-message-content :deep(th) {
  padding: 0.4rem 0.75rem;
  text-align: left;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-primary);
  letter-spacing: 0.08em;
}
.chat-message-content :deep(td) {
  padding: 0.4rem 0.75rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-primary);
}
.chat-message-content :deep(tr:hover) {
  background: var(--bg-hover);
}
.chat-message-content :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  margin: 0.5rem 0;
  padding: 0.25rem 0.75rem;
  color: var(--text-secondary);
  font-style: italic;
}
.chat-message-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-primary);
  margin: 0.75rem 0;
}
.chat-message-content :deep(svg) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0.5rem 0;
}
</style>
