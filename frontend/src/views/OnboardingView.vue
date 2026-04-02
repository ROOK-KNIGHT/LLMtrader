<template>
  <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-primary);">
    <div class="card" style="max-width: 600px; width: 90%;">
      <div class="card-header">
        <h2 class="card-title">Connect Schwab Account</h2>
      </div>
      <div class="card-body">
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
          To enable live trading, you'll need to provide your Schwab API credentials. You can get these from the <a href="https://developer.schwab.com" target="_blank" style="color: var(--accent-primary);">Schwab Developer Portal</a>.
        </p>
        
        <!-- Error message -->
        <div v-if="error" style="padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 4px; margin-bottom: 1rem;">
          <p style="color: #ef4444; font-size: 0.875rem; margin: 0;">{{ error }}</p>
        </div>
        
        <!-- Success message -->
        <div v-if="success" style="padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 4px; margin-bottom: 1rem;">
          <p style="color: #10b981; font-size: 0.875rem; margin: 0;">Credentials saved! Click "Connect Schwab" to authorize.</p>
        </div>
        
        <!-- Step 1: Enter Credentials -->
        <div v-if="step === 1">
          <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem;">Step 1: Enter API Credentials</h3>
          
          <form @submit.prevent="saveCredentials">
            <div style="margin-bottom: 1rem;">
              <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-secondary);">
                App Key (Client ID)
              </label>
              <input 
                v-model="appKey"
                type="text"
                class="input"
                placeholder="Your Schwab App Key"
                required
                :disabled="isLoading"
              />
            </div>
            
            <div style="margin-bottom: 1rem;">
              <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-secondary);">
                App Secret (Client Secret)
              </label>
              <input 
                v-model="appSecret"
                type="password"
                class="input"
                placeholder="Your Schwab App Secret"
                required
                :disabled="isLoading"
              />
            </div>
            
            <div style="margin-bottom: 1.5rem;">
              <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-secondary);">
                Callback URL
              </label>
              <input 
                v-model="callbackUrl"
                type="text"
                class="input"
                readonly
                style="background: var(--bg-secondary);"
              />
              <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                Add this URL to your Schwab app's redirect URIs
              </p>
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary" 
              style="width: 100%;"
              :disabled="isLoading"
            >
              <span v-if="isLoading">Saving...</span>
              <span v-else>Save Credentials</span>
            </button>
          </form>
        </div>
        
        <!-- Step 2: Connect to Schwab -->
        <div v-if="step === 2">
          <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem;">Step 2: Authorize Access</h3>
          
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            Click the button below to authorize LLMtrader to access your Schwab account. You'll be redirected to Schwab's login page.
          </p>
          
          <button 
            class="btn btn-primary btn-lg" 
            style="width: 100%;"
            @click="connectSchwab"
            :disabled="isLoading"
          >
            <span v-if="isLoading">Loading...</span>
            <span v-else>Connect Schwab Account</span>
          </button>
          
          <button 
            class="btn btn-secondary" 
            style="width: 100%; margin-top: 1rem;"
            @click="step = 1"
          >
            Back to Credentials
          </button>
        </div>
        
        <!-- Skip option -->
        <div style="margin-top: 2rem; text-align: center;">
          <button class="btn btn-secondary" @click="$router.push('/dashboard')">
            Skip for Now
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const step = ref(1)
const appKey = ref('')
const appSecret = ref('')
const callbackUrl = ref('https://volflowagent.com')
const isLoading = ref(false)
const error = ref(null)
const success = ref(false)

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

async function saveCredentials() {
  isLoading.value = true
  error.value = null
  success.value = false
  
  try {
    await api.post('/api/schwab/credentials', {
      app_key: appKey.value,
      app_secret: appSecret.value,
      callback_url: callbackUrl.value
    })
    
    success.value = true
    step.value = 2
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save credentials'
  } finally {
    isLoading.value = false
  }
}

async function connectSchwab() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await api.get('/api/schwab/auth-url')
    const authUrl = response.data.auth_url
    
    // Redirect to Schwab OAuth page
    window.location.href = authUrl
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to get authorization URL'
    isLoading.value = false
  }
}
</script>
