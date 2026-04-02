import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/onboarding',
      name: 'Onboarding',
      component: () => import('@/views/OnboardingView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/terminal',
      name: 'Terminal',
      component: () => import('@/views/TerminalView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/TradingDashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/oauth/schwab/callback',
      name: 'SchwabCallback',
      component: () => import('@/views/OAuthCallbackView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/oauth/success',
      name: 'OAuthSuccess',
      component: () => import('@/views/OAuthCallbackView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/oauth/error',
      name: 'OAuthError',
      component: () => import('@/views/OAuthCallbackView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Intercept Schwab OAuth callback - code lands on root URL
  if (to.path === '/' && to.query.code) {
    next({ name: 'SchwabCallback', query: to.query })
    return
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/terminal')
  } else {
    next()
  }
})

export default router
