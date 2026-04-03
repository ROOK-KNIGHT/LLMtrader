import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import { usePanelStore } from './panels'

const API_BASE = '/api'

export const useAIStore = defineStore('ai', () => {
  // State
  const messages = ref([])
  const isProcessing = ref(false)
  const selectedModel = ref('claude') // claude, grok, gemini
  const selectedPersona = ref('portfolio_manager')
  const debateMode = ref(false)
  const error = ref(null)

  // Welcome message
  const welcomeMessage = {
    id: 1,
    role: 'assistant',
    model: 'claude',
    content: 'Welcome to VolFlow Agent! I\'m your AI trading assistant powered by Claude. I have direct access to your Schwab account — I can pull live quotes, check your positions, analyze options chains, and execute trades. What would you like to do?',
    timestamp: new Date(Date.now() - 3600000)
  }

  // Getters
  const conversationHistory = computed(() => messages.value)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])

  // Build conversation history for the API (last 20 messages, user/assistant only)
  function buildHistory() {
    return messages.value
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .slice(-20)
      .map(m => ({
        role: m.role,
        content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content)
      }))
  }

  // Actions
  async function sendMessage(content) {
    if (!content?.trim()) return

    error.value = null

    // Add user message to UI immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    isProcessing.value = true

    try {
      const authStore = useAuthStore()
      const token = authStore.sessionToken

      if (!token) {
        throw new Error('Not authenticated. Please log in.')
      }

      // Build history BEFORE adding the current message (it's already in messages)
      const history = buildHistory().slice(0, -1) // exclude the message we just added

      const response = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: content.trim(),
          model: selectedModel.value,
          persona: selectedPersona.value,
          conversation_history: history
        })
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error ${response.status}`)
      }

      const data = await response.json()

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        model: data.model || selectedModel.value,
        content: data.response,
        timestamp: new Date()
      }
      messages.value.push(aiMessage)

    } catch (err) {
      error.value = err.message
      // Add error message to chat so user sees it inline
      messages.value.push({
        id: Date.now() + 2,
        role: 'assistant',
        model: selectedModel.value,
        content: `⚠️ Error: ${err.message}`,
        timestamp: new Date(),
        isError: true
      })
    } finally {
      isProcessing.value = false
    }
  }

  function clearConversation() {
    messages.value = [{ ...welcomeMessage, timestamp: new Date() }]
    error.value = null
  }

  function setModel(model) {
    selectedModel.value = model
  }

  function setPersona(persona) {
    selectedPersona.value = persona
  }

  function toggleDebateMode() {
    debateMode.value = !debateMode.value
  }

  // Initialize with welcome message
  messages.value = [{ ...welcomeMessage }]

  return {
    messages,
    isProcessing,
    selectedModel,
    selectedPersona,
    debateMode,
    error,
    conversationHistory,
    lastMessage,
    sendMessage,
    clearConversation,
    setModel,
    setPersona,
    toggleDebateMode
  }
})
