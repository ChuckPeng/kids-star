<template>
  <div class="register-container">
    <div class="register-card">
      <h1>创建账号</h1>
      <p class="subtitle">注册成为家长，开始管理孩子的习惯养成</p>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label>昵称</label>
          <input v-model="form.name" type="text" placeholder="如何称呼您" required />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="form.email" type="email" placeholder="请输入邮箱" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="至少6位密码" required minlength="6" />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="link-text">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = ref({ name: '', email: '', password: '' })

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    console.log('Register:', form.value)
    router.push('/parent/dashboard')
  } catch {
    error.value = '注册失败，请稍后再试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.register-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
h1 { text-align: center; color: #333; margin: 0 0 4px; }
.subtitle { text-align: center; color: #888; margin: 0 0 24px; font-size: 14px; }
.register-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; color: #555; font-weight: 500; }
.form-group input { padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: #667eea; }
.btn-primary { padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; }
.btn-primary:hover { background: #5a6fd6; }
.btn-primary:disabled { background: #aab; cursor: not-allowed; }
.link-text { text-align: center; font-size: 13px; color: #888; }
.link-text a { color: #667eea; text-decoration: none; }
.error-msg { color: #e74c3c; font-size: 13px; text-align: center; margin-top: 12px; }
</style>
