import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const isParent = computed(() => user.value?.role === 'parent' || user.value?.role === 'admin')
  const isChild = computed(() => user.value?.role === 'child')

  async function login(username: string, password: string) {
    const { data } = await api.post('/auth/login', { username, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchMe()
  }

  async function register(username: string, password: string, name: string) {
    await api.post('/auth/register', { username, password, name })
    await login(username, password)
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
    window.location.href = '/login'
  }

  return { user, loading, isLoggedIn, isParent, isChild, login, register, fetchMe, logout }
})
