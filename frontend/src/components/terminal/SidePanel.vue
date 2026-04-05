<template>
  <div v-if="panelStore.hasAnyPanel" class="side-panel-overlay">
    <div
      v-for="panel in panelStore.panels"
      :key="panel.id"
      class="side-panel"
      :class="{ collapsed: !panel.isExpanded }"
    >
      <!-- Panel Header (always visible) -->
      <div class="panel-header" @click="panelStore.toggleExpand(panel.id)">
        <div class="panel-header-left">
          <span class="collapse-arrow">{{ panel.isExpanded ? '▼' : '▶' }}</span>
          <div class="panel-title">{{ panel.title }}</div>
          <span v-if="panel.isPinned" class="pin-indicator">📌</span>
        </div>
        <div class="panel-actions" @click.stop>
          <button
            class="panel-btn"
            :class="{ active: panel.isPinned }"
            @click="panelStore.togglePin(panel.id)"
            title="Pin panel"
          >
            PIN
          </button>
          <button
            class="panel-btn"
            @click="panelStore.close(panel.id)"
            title="Close panel"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- Panel Body (only when expanded) -->
      <div v-if="panel.isExpanded" class="panel-body">
        <div v-html="panel.htmlContent" class="panel-content"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePanelStore } from '@/stores/panels'

const panelStore = usePanelStore()
</script>

<style scoped>
.side-panel-overlay {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 500px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  pointer-events: none;
}

/* Mobile: full-screen overlay */
@media (max-width: 768px) {
  .side-panel-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    z-index: 500;
    background: rgba(0, 0, 0, 0.7);
  }
  .side-panel {
    width: 100% !important;
    max-height: 80vh;
    margin-top: auto;
    border-left: none !important;
    border-top: 2px solid var(--border-accent);
  }
}

.side-panel {
  width: 100%;
  background: var(--bg-secondary);
  border-left: 2px solid var(--border-accent);
  box-shadow: -5px 0 20px rgba(255, 149, 0, 0.3);
  display: flex;
  flex-direction: column;
  pointer-events: all;
  transition: flex 0.3s ease;
  animation: slideIn 0.3s ease-out;
}

/* Expanded panel takes remaining space */
.side-panel:not(.collapsed) {
  flex: 1;
  min-height: 0;
}

/* Collapsed panel is just the header */
.side-panel.collapsed {
  flex: 0 0 auto;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0);   opacity: 1; }
}

.panel-header {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
  padding: 0.6rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
}

.panel-header:hover {
  background: var(--bg-hover);
}

.panel-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.collapse-arrow {
  font-size: 0.7rem;
  color: var(--accent-primary);
  flex-shrink: 0;
}

.panel-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.12em;
  text-shadow: 0 0 8px var(--accent-primary);
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pin-indicator {
  font-size: 0.75rem;
  flex-shrink: 0;
}

.panel-actions {
  display: flex;
  gap: 0.4rem;
  flex-shrink: 0;
}

.panel-btn {
  padding: 0.2rem 0.6rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: 0.8rem;
  font-family: 'VT323', monospace;
  letter-spacing: 0.1em;
}

.panel-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.panel-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
  box-shadow: 0 0 10px var(--accent-primary);
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 0;
}

.panel-content {
  font-family: 'VT323', monospace;
  color: var(--text-primary);
}

/* ── LLM-generated content styles ── */
.panel-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.panel-content :deep(th) {
  padding: 0.5rem;
  text-align: left;
  color: var(--text-secondary);
  font-size: 0.85rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-primary);
}

.panel-content :deep(td) {
  padding: 0.5rem;
  color: var(--text-primary);
  font-size: 1rem;
  border-bottom: 1px solid var(--border-primary);
}

.panel-content :deep(tr:hover) {
  background: var(--bg-hover);
}

.panel-content :deep(h3) {
  color: var(--accent-primary);
  text-shadow: 0 0 8px var(--accent-primary);
  margin: 1rem 0 0.5rem 0;
  font-size: 1.1rem;
  letter-spacing: 0.1em;
}

.panel-content :deep(.profit) { color: var(--text-profit); }
.panel-content :deep(.loss)   { color: var(--text-loss); }
.panel-content :deep(.warning){ color: #ffff00; }

.panel-content :deep(.badge) {
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  display: inline-block;
  margin: 0 0.25rem;
}

.panel-content :deep(.badge-bullish) {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
  border: 1px solid #00ff00;
}

.panel-content :deep(.badge-bearish) {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
  border: 1px solid #ff0000;
}

.panel-content :deep(.badge-neutral) {
  background: rgba(255, 149, 0, 0.2);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

.panel-content :deep(.progress-bar) {
  width: 100%;
  height: 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin: 0.5rem 0;
}

.panel-content :deep(.progress-fill) {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  box-shadow: 0 0 10px var(--accent-primary);
  transition: width 0.3s ease;
}
</style>
