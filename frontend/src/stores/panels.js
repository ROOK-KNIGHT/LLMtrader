import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePanelStore = defineStore('panels', () => {
  const isOpen = ref(false)
  const title = ref('')
  const htmlContent = ref('')
  const isPinned = ref(false)
  
  function open(panelTitle, html) {
    title.value = panelTitle
    htmlContent.value = html
    isOpen.value = true
  }
  
  function close() {
    if (!isPinned.value) {
      isOpen.value = false
      // Clear content after animation
      setTimeout(() => {
        if (!isOpen.value) {
          title.value = ''
          htmlContent.value = ''
        }
      }, 300)
    }
  }
  
  function togglePin() {
    isPinned.value = !isPinned.value
  }
  
  function clear() {
    isOpen.value = false
    isPinned.value = false
    title.value = ''
    htmlContent.value = ''
  }
  
  return {
    isOpen,
    title,
    htmlContent,
    isPinned,
    open,
    close,
    togglePin,
    clear
  }
})
