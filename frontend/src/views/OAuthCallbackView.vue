<template>
  <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--bg-primary);">
    <div v-if="status === 'success'" style="text-align: center;">
      <div style="width: 64px; height: 64px; border-radius: 50%; background: rgba(16, 185, 129, 0.1); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      <h2 style="font-size: 1.5rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
        Successfully Connected!
      </h2>
      <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
        Your Schwab account has been connected. Redirecting to terminal...
      </p>
    </div>
    
    <div v-else-if="status === 'error'" style="text-align: center; max-width: 400px;">
      <div style="width: 64px; height: 64px; border-radius: 50%; background: rgba(239, 68, 68, 0.1); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
      </div>
      <h2 style="font-size: 1.5rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
        Connection Failed
      </h2>
      <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
        {{ errorMessage }}
      </p>
      <button class="btn btn-primary" @click="router.push('/onboarding')">
        Try Again
      </button>
    </div>
    
    <div v-else style="text-align: center;">
      <div class="spinner" style="width: 48px; height: 48px; margin-bottom: 1rem;"></div>
      <p style="color: var(--text-secondary);">Processing OAuth callback...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const status = ref('loading')
const errorMessage = ref('')

onMounted(async () => {
  // Check if this is a success or error callback
  const path = route.path
  
  if (path === '/oauth/success') {
    status.value = 'success'
    
    // Refresh user data to update schwab_connected status
    await authStore.fetchCurrentUser()
    
    // Redirect to terminal after 2 seconds
    setTimeout(() => {
      router.push('/terminal')
    }, 2000)
  } else if (path === '/oauth/error') {
    status.value = 'error'
    errorMessage.value = route.query.message || 'An unknown error occurred during OAuth'
  } else {
    // Shouldn't happen, but redirect to onboarding
    router.push('/onboarding')
  }
})
</script>
