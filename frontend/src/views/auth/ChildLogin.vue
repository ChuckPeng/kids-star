<template>
  <div class="child-login">
    <div class="login-card">
      <h1>👦 Kids-Star</h1>
      <p class="subtitle">儿童登录</p>

      <!-- Step 1: Enter invite code -->
      <div v-if="step === 1">
        <p class="hint">请输入家长分享的家庭邀请码</p>
        <input
          v-model="inviteCode"
          placeholder="邀请码"
          style="text-transform:uppercase; letter-spacing:4px; text-align:center; font-size:18px"
          maxlength="8"
          @keyup.enter="doLookup"
        />
        <button class="btn primary" @click="doLookup" :disabled="!inviteCode || lookingUp">
          {{ lookingUp ? '查找中...' : '查找家庭' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </div>

      <!-- Step 2: Select child profile -->
      <div v-else-if="step === 2">
        <p class="hint">选择你的头像进入</p>
        <div class="child-list">
          <div
            v-for="c in children"
            :key="c.id"
            class="child-card"
            @click="doLogin(c)"
          >
            <div class="child-avatar">👦</div>
            <div class="child-name">{{ c.nickname || c.name }}</div>
          </div>
        </div>
        <p v-if="children.length === 0" class="empty">这个家庭还没有孩子，请联系家长添加</p>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn secondary" @click="step = 1; error = ''">← 重新输入</button>
      </div>

      <p class="link-text">
        <router-link to="/login">家长登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

const step = ref(1)
const inviteCode = ref('')
const lookingUp = ref(false)
const error = ref('')
const children = ref<any[]>([])

async function doLookup() {
  lookingUp.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/families/lookup/${inviteCode.value.toUpperCase()}`)
    children.value = data
    if (children.value.length === 0) {
      error.value = '该家庭还没有孩子，请联系家长在设置中添加'
    } else {
      step.value = 2
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '邀请码无效'
  } finally {
    lookingUp.value = false
  }
}

async function doLogin(child: any) {
  error.value = ''
  try {
    const { data } = await api.post('/auth/login-child', {
      invite_code: inviteCode.value.toUpperCase(),
      child_id: child.id,
    })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await authStore.fetchMe()
    router.push('/child')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  }
}
</script>

<style scoped>
.child-login {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); padding: 20px;
}
.login-card {
  background: white; border-radius: 16px; padding: 32px 28px; width: 100%;
  max-width: 380px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); text-align: center;
}
h1 { font-size: 24px; color: #333; margin: 0 0 4px; }
.subtitle { color: #888; margin: 0 0 20px; font-size: 14px; }
.hint { color: #666; font-size: 13px; margin-bottom: 12px; }
input { width: 100%; padding: 12px; border: 2px solid #f0c78e; border-radius: 10px; font-size: 15px; outline: none; box-sizing: border-box; margin-bottom: 12px; }
input:focus { border-color: #f39c12; }
.btn { width: 100%; padding: 12px; border: none; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; margin-bottom: 8px; }
.btn:disabled { opacity: 0.5; cursor: default; }
.primary { background: #f39c12; color: white; }
.secondary { background: #f0f2f5; color: #333; }
.child-list { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-bottom: 16px; }
.child-card { background: #fef9f2; border: 2px solid #fde4c2; border-radius: 12px; padding: 16px 12px; cursor: pointer; transition: all 0.2s; min-width: 80px; }
.child-card:hover { border-color: #f39c12; transform: translateY(-2px); }
.child-avatar { font-size: 36px; }
.child-name { font-size: 14px; font-weight: 600; margin-top: 6px; color: #333; }
.empty { color: #999; font-size: 13px; padding: 12px; }
.error { color: #e74c3c; font-size: 13px; margin: 8px 0; }
.link-text { margin-top: 12px; font-size: 13px; color: #888; }
.link-text a { color: #f39c12; text-decoration: none; }
</style>
