<template>
  <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-primary);">
    <div class="card" style="max-width: 400px; width: 90%;">
      <div class="card-header" style="text-align: center;">
        <h1 class="retro-title" style="font-size: 2rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 0.5rem;">
          VOLFLOW AGENT
        </h1>
        <p style="color: var(--text-secondary); font-size: 0.875rem;">
          AI-Powered Portfolio Management
        </p>
      </div>
      
      <div class="card-body" style="padding-top: 2rem;">
        <!-- Toggle between Sign In / Sign Up -->
        <div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem;">
          <button 
            class="btn" 
            :class="isSignup ? 'btn-secondary' : 'btn-primary'"
            @click="isSignup = false"
            style="flex: 1;"
          >
            Sign In
          </button>
          <button 
            class="btn" 
            :class="isSignup ? 'btn-primary' : 'btn-secondary'"
            @click="isSignup = true"
            style="flex: 1;"
          >
            Sign Up
          </button>
        </div>
        
        <!-- Error message -->
        <div v-if="authStore.error" style="padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 4px; margin-bottom: 1rem;">
          <p style="color: #ef4444; font-size: 0.875rem; margin: 0;">{{ authStore.error }}</p>
        </div>
        
        <!-- Form -->
        <form @submit.prevent="handleSubmit">
          <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-secondary);">
              Email
            </label>
            <input 
              v-model="email"
              type="email"
              class="input"
              placeholder="you@example.com"
              required
              :disabled="authStore.isLoading"
            />
          </div>
          
          <div v-if="isSignup" style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-secondary);">
              Display Name
            </label>
            <input 
              v-model="displayName"
              type="text"
              class="input"
              placeholder="Your Name"
              :disabled="authStore.isLoading"
            />
          </div>
          
          <div style="margin-bottom: 1.5rem;">
            <label style="display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-secondary);">
              Password
            </label>
            <input 
              v-model="password"
              type="password"
              class="input"
              placeholder="••••••••"
              required
              :disabled="authStore.isLoading"
            />
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary btn-lg" 
            style="width: 100%;"
            :disabled="authStore.isLoading"
          >
            <span v-if="authStore.isLoading">
              <div class="spinner" style="width: 16px; height: 16px; display: inline-block; margin-right: 0.5rem;"></div>
              {{ isSignup ? 'Creating Account...' : 'Signing In...' }}
            </span>
            <span v-else>
              {{ isSignup ? 'Create Account' : 'Sign In' }}
            </span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isSignup = ref(false)
const email = ref('')
const password = ref('')
const displayName = ref('')

async function handleSubmit() {
  let result
  
  if (isSignup.value) {
    result = await authStore.signup(email.value, password.value, displayName.value || null)
  } else {
    result = await authStore.login(email.value, password.value)
  }
  
  if (result.success) {
    // Check if user needs to complete onboarding
    if (!authStore.user.schwab_connected) {
      router.push('/onboarding')
    } else {
      router.push('/dashboard')
    }
  }
}
</script>
