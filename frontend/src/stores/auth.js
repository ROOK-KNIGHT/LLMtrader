import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// Use relative URLs so requests go through nginx proxy
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('session_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const sessionToken = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Getters
  const isAuthenticated = computed(() => !!user.value && !!sessionToken.value)
  const userEmail = computed(() => user.value?.email || '')
  const userName = computed(() => user.value?.display_name || 'User')
  
  // Actions
  function setUser(userData) {
    user.value = userData
  }
  
  function setSessionToken(token) {
    sessionToken.value = token
    if (token) {
      localStorage.setItem('session_token', token)
    } else {
      localStorage.removeItem('session_token')
    }
  }
  
  async function signup(email, password, displayName = null) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/auth/signup', {
        email,
        password,
        display_name: displayName
      })
      
      const { token, user: userData } = response.data
      
      setSessionToken(token)
      setUser(userData)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Signup failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  async function login(email, password) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/auth/login', {
        email,
        password
      })
      
      const { token, user: userData } = response.data
      
      setSessionToken(token)
      setUser(userData)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  async function fetchCurrentUser() {
    if (!sessionToken.value) return
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch user'
      // Token might be invalid, clear it
      logout()
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  function logout() {
    user.value = null
    sessionToken.value = null
    localStorage.removeItem('session_token')
  }
  
  async function loadSession() {
    const token = localStorage.getItem('session_token')
    if (token) {
      sessionToken.value = token
      await fetchCurrentUser()
    }
  }
  
  // Initialize
  loadSession()
  
  return {
    user,
    sessionToken,
    isLoading,
    error,
    isAuthenticated,
    userEmail,
    userName,
    setUser,
    setSessionToken,
    signup,
    login,
    logout,
    loadSession,
    fetchCurrentUser
  }
})
