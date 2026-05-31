import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const isParent = computed(() => user.value?.role === 'parent' || user.value?.role === 'admin')
  const isChild = computed(() => user.value?.role === 'child')

  async function login(email: string, password: string) {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchMe()
  }

  async function register(email: string, password: string, name: string) {
    await api.post('/auth/register', { email, password, name })
    await login(email, password)
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
    } catch {
      user.value = null
    }
  }

  function logout() {
    localStorage.clear()
    user.value = null
  }

  return { user, loading, isLoggedIn, isParent, isChild, login, register, fetchMe, logout }
})
