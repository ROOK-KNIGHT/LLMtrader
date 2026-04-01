<template>
  <div class="risk-dashboard">
    <!-- Risk Summary Banner -->
    <div class="risk-banner">
      <div class="banner-section">
        <div class="metric-label">NAV</div>
        <div class="metric-value mono">${{ riskStore.nav.toLocaleString() }}</div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">VaR(95%)</div>
        <div class="metric-value mono text-loss">${{ Math.abs(riskStore.var95).toLocaleString() }}</div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">CVaR(99%)</div>
        <div class="metric-value mono text-loss">${{ Math.abs(riskStore.cvar99).toLocaleString() }}</div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">Sharpe</div>
        <div class="metric-value mono">{{ riskStore.sharpeRatio.toFixed(2) }}</div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">Net Delta</div>
        <div class="metric-value mono" :class="riskStore.netDelta >= 0 ? 'text-profit' : 'text-loss'">
          {{ riskStore.netDelta >= 0 ? '+' : '' }}{{ riskStore.netDelta.toFixed(1) }}
        </div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">Beta</div>
        <div class="metric-value mono">{{ riskStore.portfolioBeta.toFixed(2) }}</div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">Max DD</div>
        <div class="metric-value mono text-loss">{{ riskStore.maxDrawdown.toFixed(1) }}%</div>
      </div>
      <div class="banner-divider"></div>
      <div class="banner-section">
        <div class="metric-label">Margin Used</div>
        <div class="metric-value mono">{{ riskStore.marginUsed }}%</div>
      </div>
      <div class="banner-section risk-score-section">
        <div class="risk-score-container">
          <div class="risk-score-bar">
            <div class="risk-score-fill" :style="{ width: (riskStore.riskScore * 10) + '%' }"></div>
          </div>
          <div class="risk-score-label">Risk Score: {{ riskStore.riskScore.toFixed(1) }}/10 MODERATE</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="risk-content">
      <!-- Options Risk Panel -->
      <div class="panel options-panel">
        <div class="panel-header">
          <div class="panel-title">OPTIONS RISK ENGINE</div>
        </div>
        <div class="panel-body">
          <!-- Aggregate Greeks -->
          <div class="greeks-summary">
            <div class="greek-item">
              <div class="greek-label">Delta</div>
              <div class="greek-value mono">{{ riskStore.aggregateGreeks.delta >= 0 ? '+' : '' }}{{ riskStore.aggregateGreeks.delta.toFixed(1) }}</div>
            </div>
            <div class="greek-item">
              <div class="greek-label">Gamma</div>
              <div class="greek-value mono">{{ riskStore.aggregateGreeks.gamma.toFixed(1) }}</div>
            </div>
            <div class="greek-item">
              <div class="greek-label">Theta</div>
              <div class="greek-value mono text-loss">${{ riskStore.aggregateGreeks.theta }}/day</div>
            </div>
            <div class="greek-item">
              <div class="greek-label">Vega</div>
              <div class="greek-value mono text-profit">${{ riskStore.aggregateGreeks.vega }}</div>
            </div>
            <div class="greek-item">
              <div class="greek-label">Rho</div>
              <div class="greek-value mono">${{ riskStore.aggregateGreeks.rho }}</div>
            </div>
          </div>

          <!-- Options Positions Table -->
          <div class="options-table-wrapper">
            <table class="risk-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>DTE</th>
                  <th>Delta</th>
                  <th>Gamma</th>
                  <th>Theta</th>
                  <th>Vega</th>
                  <th>IV</th>
                  <th>IV Rank</th>
                  <th>Max Loss</th>
                  <th>Prob ITM</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pos in riskStore.optionsPositions" :key="pos.id">
                  <td class="mono font-bold">{{ pos.symbol }}</td>
                  <td>
                    <span :class="['type-badge', pos.type.toLowerCase()]">{{ pos.type }}</span>
                  </td>
                  <td class="mono">{{ pos.dte }}</td>
                  <td class="mono" :class="pos.delta >= 0 ? 'text-profit' : 'text-loss'">
                    {{ pos.delta >= 0 ? '+' : '' }}{{ pos.delta.toFixed(2) }}
                  </td>
                  <td class="mono">{{ pos.gamma.toFixed(2) }}</td>
                  <td class="mono text-loss">${{ pos.theta.toFixed(1) }}</td>
                  <td class="mono">${{ pos.vega.toFixed(2) }}</td>
                  <td class="mono">{{ pos.iv }}%</td>
                  <td class="mono">{{ pos.ivRank }}th</td>
                  <td class="mono text-loss">${{ pos.maxLoss.toLocaleString() }}</td>
                  <td class="mono">{{ pos.probITM }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Equity Risk Panel -->
      <div class="panel equity-panel">
        <div class="panel-header">
          <div class="panel-title">EQUITIES/ETF RISK ENGINE</div>
        </div>
        <div class="panel-body">
          <table class="risk-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Beta</th>
                <th>Sector</th>
                <th>Weight</th>
                <th>ATR(14)</th>
                <th>Dist to 200MA</th>
                <th>RSI</th>
                <th>Max DD(30d)</th>
                <th>Sharpe</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pos in riskStore.equityPositions" :key="pos.id">
                <td class="mono font-bold">{{ pos.symbol }}</td>
                <td class="mono">{{ pos.beta.toFixed(2) }}</td>
                <td>{{ pos.sector }}</td>
                <td class="mono">{{ pos.weight }}%</td>
                <td class="mono">${{ pos.atr.toFixed(2) }}</td>
                <td class="mono" :class="pos.distTo200MA >= 0 ? 'text-profit' : 'text-loss'">
                  {{ pos.distTo200MA >= 0 ? '+' : '' }}{{ pos.distTo200MA.toFixed(1) }}%
                </td>
                <td class="mono">{{ pos.rsi }}</td>
                <td class="mono text-loss">{{ pos.maxDD30d.toFixed(1) }}%</td>
                <td class="mono">{{ pos.sharpe.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Exposure & Stress Tests Row -->
      <div class="analysis-row">
        <!-- Sector Exposure -->
        <div class="panel exposure-panel">
          <div class="panel-header">
            <div class="panel-title">SECTOR EXPOSURE</div>
          </div>
          <div class="panel-body">
            <div v-for="sector in riskStore.sectorExposure" :key="sector.sector" class="exposure-item">
              <div class="exposure-label">{{ sector.sector }}</div>
              <div class="exposure-bar-container">
                <div class="exposure-bar" :style="{ width: sector.weight + '%', background: sector.color }"></div>
              </div>
              <div class="exposure-value mono">{{ sector.weight }}%</div>
            </div>
          </div>
        </div>

        <!-- Stress Tests -->
        <div class="panel stress-panel">
          <div class="panel-header">
            <div class="panel-title">STRESS TEST SCENARIOS</div>
          </div>
          <div class="panel-body">
            <table class="risk-table">
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Portfolio Impact</th>
                  <th>Worst Position</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="scenario in riskStore.stressScenarios" :key="scenario.id">
                  <td>{{ scenario.name }}</td>
                  <td class="mono" :class="scenario.impact >= 0 ? 'text-profit' : 'text-loss'">
                    {{ scenario.impact >= 0 ? '+' : '' }}${{ Math.abs(scenario.impact).toLocaleString() }}
                    ({{ scenario.impactPct >= 0 ? '+' : '' }}{{ scenario.impactPct.toFixed(1) }}%)
                  </td>
                  <td class="mono">{{ scenario.worstPosition }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Risk Rules Engine -->
      <div class="panel rules-panel">
        <div class="panel-header">
          <div class="panel-title">RISK RULES ENGINE</div>
        </div>
        <div class="panel-body">
          <table class="risk-table rules-table">
            <thead>
              <tr>
                <th>Rule</th>
                <th>Scope</th>
                <th>Status</th>
                <th>Limit</th>
                <th>Current</th>
                <th>Action</th>
                <th>Enabled</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rule in riskStore.riskRules" :key="rule.id">
                <td>{{ rule.name }}</td>
                <td>
                  <span class="scope-badge">{{ rule.scope }}</span>
                </td>
                <td>
                  <span :class="['status-badge', 'status-' + rule.status.toLowerCase()]">
                    {{ rule.status }}
                  </span>
                </td>
                <td class="mono">{{ rule.limit }}{{ rule.unit || '' }}</td>
                <td class="mono">{{ rule.current }}{{ rule.unit || '' }}</td>
                <td>
                  <span class="action-badge">{{ rule.action }}</span>
                </td>
                <td>
                  <label class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :checked="rule.enabled"
                      @change="riskStore.toggleRule(rule.id)"
                    />
                    <span class="toggle-slider"></span>
                  </label>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRiskStore } from '@/stores/risk'

const riskStore = useRiskStore()
</script>

<style scoped>
.risk-dashboard {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
}

/* Risk Banner */
.risk-banner {
  background: var(--bg-secondary);
  border: 2px solid var(--border-accent);
  border-radius: var(--radius-lg);
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 0 20px rgba(255, 149, 0, 0.3);
}

.banner-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.banner-divider {
  width: 1px;
  height: 40px;
  background: var(--border-secondary);
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.metric-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.risk-score-section {
  flex: 1;
  margin-left: auto;
}

.risk-score-container {
  width: 100%;
}

.risk-score-bar {
  width: 100%;
  height: 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.risk-score-fill {
  height: 100%;
  background: linear-gradient(90deg, #00ff00, #ffff00, #ff9500, #ff0000);
  box-shadow: 0 0 10px var(--accent-primary);
  transition: width 0.3s ease;
}

.risk-score-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-align: right;
}

/* Risk Content */
.risk-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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
}

.panel-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.15em;
  text-shadow: 0 0 8px var(--accent-primary);
}

.panel-body {
  padding: 1rem;
}

/* Greeks Summary */
.greeks-summary {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.greek-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.greek-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.greek-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* Tables */
.risk-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'VT323', monospace;
}

.risk-table thead {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-secondary);
}

.risk-table th {
  padding: 0.75rem 0.5rem;
  text-align: left;
  color: var(--text-secondary);
  font-size: 0.85rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.risk-table td {
  padding: 0.75rem 0.5rem;
  color: var(--text-primary);
  font-size: 1rem;
  border-bottom: 1px solid var(--border-primary);
}

.risk-table tbody tr:hover {
  background: var(--bg-hover);
}

.options-table-wrapper {
  overflow-x: auto;
}

/* Badges */
.type-badge {
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  letter-spacing: 0.1em;
}

.type-badge.call {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
  border: 1px solid #00ff00;
}

.type-badge.put {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
  border: 1px solid #ff0000;
}

.scope-badge {
  padding: 0.25rem 0.5rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.1em;
}

.status-ok {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
  border: 1px solid #00ff00;
}

.status-warn {
  background: rgba(255, 255, 0, 0.2);
  color: #ffff00;
  border: 1px solid #ffff00;
  animation: pulse-warn 2s infinite;
}

.status-breach {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
  border: 1px solid #ff0000;
  animation: pulse-breach 1s infinite;
}

@keyframes pulse-warn {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-breach {
  0%, 100% { opacity: 1; box-shadow: 0 0 10px #ff0000; }
  50% { opacity: 0.7; box-shadow: 0 0 20px #ff0000; }
}

.action-badge {
  padding: 0.25rem 0.5rem;
  background: rgba(255, 149, 0, 0.2);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  transition: 0.3s;
  border-radius: 20px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 2px;
  bottom: 2px;
  background-color: var(--text-muted);
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: rgba(255, 149, 0, 0.3);
  border-color: var(--accent-primary);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
  background-color: var(--accent-primary);
  box-shadow: 0 0 10px var(--accent-primary);
}

/* Analysis Row */
.analysis-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
}

/* Exposure Panel */
.exposure-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.exposure-label {
  width: 150px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.exposure-bar-container {
  flex: 1;
  height: 20px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.exposure-bar {
  height: 100%;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px currentColor;
}

.exposure-value {
  width: 50px;
  text-align: right;
  font-size: 0.9rem;
  color: var(--text-primary);
}
</style>
