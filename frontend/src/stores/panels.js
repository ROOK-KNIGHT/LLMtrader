import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const MAX_PANELS = 3

export const usePanelStore = defineStore('panels', () => {
  // Array of panel objects: { id, title, htmlContent, isPinned, isExpanded }
  const panels = ref([])

  // Track dismissed panel IDs so renderMessage won't re-open them
  const dismissedIds = ref(new Set())

  const hasAnyPanel = computed(() => panels.value.length > 0)

  /**
   * Add or update a panel.
   * - If a panel with this id already exists, update its content and expand it.
   * - Otherwise, collapse all currently expanded panels, then add the new one expanded.
   * - If at max capacity, remove the oldest unpinned panel first.
   *   If all are pinned, remove the oldest pinned one.
   */
  function open(title, htmlContent, id) {
    const panelId = id || _hashContent(title + htmlContent)

    // If this panel was dismissed, remove from dismissed set (new content = fresh open)
    dismissedIds.value.delete(panelId)

    // Check if panel already exists — update content and expand
    const existing = panels.value.find(p => p.id === panelId)
    if (existing) {
      existing.htmlContent = htmlContent
      existing.title = title
      _collapseAll()
      existing.isExpanded = true
      return
    }

    // Collapse all currently expanded panels
    _collapseAll()

    // Enforce max panel limit
    if (panels.value.length >= MAX_PANELS) {
      // Remove oldest unpinned first
      const unpinnedIdx = panels.value.findIndex(p => !p.isPinned)
      if (unpinnedIdx !== -1) {
        panels.value.splice(unpinnedIdx, 1)
      } else {
        // All pinned — remove oldest pinned
        panels.value.shift()
      }
    }

    // Add new panel (expanded)
    panels.value.push({
      id: panelId,
      title,
      htmlContent,
      isPinned: false,
      isExpanded: true
    })
  }

  /**
   * Close (remove) a panel by id.
   * Marks it as dismissed so renderMessage won't reopen it.
   */
  function close(panelId) {
    dismissedIds.value.add(panelId)
    const idx = panels.value.findIndex(p => p.id === panelId)
    if (idx !== -1) {
      panels.value.splice(idx, 1)
    }
    // If there are remaining panels and none are expanded, expand the last one
    if (panels.value.length > 0 && !panels.value.some(p => p.isExpanded)) {
      panels.value[panels.value.length - 1].isExpanded = true
    }
  }

  /**
   * Toggle pin state for a panel.
   */
  function togglePin(panelId) {
    const panel = panels.value.find(p => p.id === panelId)
    if (panel) {
      panel.isPinned = !panel.isPinned
    }
  }

  /**
   * Toggle expand/collapse for a panel (accordion style).
   * Expanding one collapses all others.
   */
  function toggleExpand(panelId) {
    const panel = panels.value.find(p => p.id === panelId)
    if (!panel) return
    if (panel.isExpanded) {
      panel.isExpanded = false
    } else {
      _collapseAll()
      panel.isExpanded = true
    }
  }

  /**
   * Check if a panel ID has been dismissed (so renderMessage skips it).
   */
  function isDismissed(panelId) {
    return dismissedIds.value.has(panelId)
  }

  /**
   * Clear all panels (e.g. on logout or new conversation).
   */
  function clearAll() {
    panels.value = []
    dismissedIds.value.clear()
  }

  function _collapseAll() {
    panels.value.forEach(p => { p.isExpanded = false })
  }

  function _hashContent(str) {
    let hash = 0
    for (let i = 0; i < Math.min(str.length, 200); i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i)
      hash |= 0
    }
    return 'panel_' + Math.abs(hash).toString(36)
  }

  return {
    panels,
    hasAnyPanel,
    open,
    close,
    togglePin,
    toggleExpand,
    isDismissed,
    clearAll,
    // Legacy compat (used in old code)
    isOpen: computed(() => panels.value.length > 0),
  }
})
