<template>
  <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-primary);">
    <div class="card" style="max-width: 500px; width: 90%; text-align: center;">
      <div class="card-body" style="padding: 2rem;">
        
        <!-- Loading state -->
        <div v-if="status === 'loading'">
          <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
          <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">Connecting to Schwab...</h2>
          <p style="color: var(--text-secondary);">Exchanging authorization code for tokens.</p>
        </div>
        
        <!-- Success state -->
        <div v-if="status === 'success'">
          <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
          <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; color: #10b981;">Connected!</h2>
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Your Schwab account has been successfully linked to LLMtrader.</p>
          <button class="btn btn-primary" @click="$router.push('/dashboard')">
            Go to Dashboard
          </button>
        </div>
        
        <!-- Error state -->
        <div v-if="status === 'error'">
          <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
          <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; color: #ef4444;">Connection Failed</h2>
          <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">{{ errorMessage }}</p>
          <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem;">
            <button class="btn btn-secondary" @click="$router.push('/onboarding')">
              Try Again
            </button>
            <button class="btn btn-primary" @click="$router.push('/dashboard')">
              Skip for Now
            </button>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const status = ref('loading')
const errorMessage = ref('')

const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('session_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

onMounted(async () => {
  const code = route.query.code
  const session = route.query.session

  if (!code) {
    // Check if this is a success redirect (no code needed)
    if (route.path === '/oauth/success') {
      status.value = 'success'
      return
    }
    status.value = 'error'
    errorMessage.value = 'No authorization code received from Schwab.'
    return
  }

  try {
    await api.post('/api/schwab/exchange-token', {
      code: code,
      session: session || null
    })
    status.value = 'success'
  } catch (err) {
    status.value = 'error'
    errorMessage.value = err.response?.data?.detail || 'Failed to exchange authorization code for tokens.'
  }
})
</script>
