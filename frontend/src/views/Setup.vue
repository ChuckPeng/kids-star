<template>
  <div class="setup">
    <header class="header">
      <h1>Kids-Star</h1>
      <span>加入或创建家庭</span>
    </header>
    <main class="content">
      <div class="card">
        <h2>创建家庭</h2>
        <p>作为家长，创建一个新家庭来管理孩子的任务</p>
        <input v-model="familyName" placeholder="家庭名称" />
        <button class="btn primary" @click="doCreate" :disabled="!familyName">创建</button>
      </div>
      <div class="divider">或</div>
      <div class="card">
        <h2>加入家庭</h2>
        <p>通过家长分享的邀请码加入已有家庭</p>
        <input v-model="inviteCode" placeholder="邀请码" style="text-transform:uppercase" />
        <button class="btn secondary" @click="doJoin" :disabled="!inviteCode">加入</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const familyStore = useFamilyStore()
const auth = useAuthStore()

const familyName = ref('')
const inviteCode = ref('')
const error = ref('')

async function doCreate() {
  try {
    error.value = ''
    await familyStore.createFamily(familyName.value)
    router.push(auth.isParent ? '/parent' : '/child')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '创建失败'
  }
}

async function doJoin() {
  try {
    error.value = ''
    await familyStore.joinFamily(inviteCode.value)
    router.push(auth.isParent ? '/parent' : '/child')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加入失败'
  }
}
</script>

<style scoped>
.setup { min-height: 100vh; background: #f0f2f5; }
.header { padding: 24px; background: #667eea; color: white; text-align: center; }
.header span { opacity: 0.8; font-size: 14px; }
.content { max-width: 420px; margin: 40px auto; padding: 0 16px; }
.card { background: white; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.card h2 { margin: 0 0 8px; font-size: 18px; }
.card p { color: #666; font-size: 14px; margin: 0 0 16px; }
.card input { width: 100%; padding: 10px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 15px; box-sizing: border-box; margin-bottom: 12px; }
.btn { width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn:disabled { opacity: 0.5; cursor: default; }
.primary { background: #667eea; color: white; }
.secondary { background: #f0f2f5; color: #333; }
.divider { text-align: center; color: #999; padding: 8px; font-size: 13px; }
.error { color: #e74c3c; text-align: center; font-size: 14px; }
</style>
