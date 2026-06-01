<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">Kids-Star</h1>
      <p class="subtitle">儿童习惯养成系统</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="form.email" type="email" placeholder="请输入邮箱" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <p class="link-text">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </p>
      </form>

      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')

const form = ref({ email: '', password: '' })

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push(authStore.isParent ? '/parent' : '/child')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.title { text-align: center; font-size: 28px; color: #333; margin: 0 0 4px; }
.subtitle { text-align: center; color: #888; margin: 0 0 24px; font-size: 14px; }
.login-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; color: #555; font-weight: 500; }
.form-group input {
  padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px;
  font-size: 14px; outline: none; transition: border-color 0.2s;
}
.form-group input:focus { border-color: #667eea; }
.btn-primary {
  padding: 12px; background: #667eea; color: white; border: none;
  border-radius: 8px; font-size: 15px; cursor: pointer; font-weight: 500;
}
.btn-primary:disabled { background: #aab; cursor: not-allowed; }
.link-text { text-align: center; font-size: 13px; color: #888; }
.link-text a { color: #667eea; text-decoration: none; }
.error-msg { color: #e74c3c; font-size: 13px; text-align: center; margin-top: 12px; }
</style>
