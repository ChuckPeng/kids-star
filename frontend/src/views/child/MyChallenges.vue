<template>
  <div class="my-challenges">
    <header class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>我的挑战</h1>
      <span class="points">⭐ {{ myPoints }}</span>
    </header>

    <section class="section">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-for="item in challenges" :key="item.claim_id" class="challenge-card">
        <div class="card-header">
          <span class="status" :class="getDisplayStatus(item)">{{ statusLabel(getDisplayStatus(item)) }}</span>
          <span class="multiplier">🔥 {{ item.task.multiplier }}x</span>
        </div>
        <h3>{{ item.task.title }}</h3>
        <p v-if="item.task.description" class="desc">{{ item.task.description }}</p>
        <div class="card-footer">
          <span class="total-points">⭐ {{ item.task.total_points }}</span>
          <button
            v-if="getDisplayStatus(item) === 'claimed' && !hasSubmitted(item.task.id)"
            class="btn submit-btn"
            @click="doSubmit(item)"
          >
            提交完成
          </button>
          <span v-else-if="hasSubmitted(item.task.id) && getSubStatus(item.task.id) === 'pending'" class="status-tag pending">⏳ 等待审核</span>
          <span v-else-if="hasSubmitted(item.task.id) && getSubStatus(item.task.id) === 'approved'" class="status-tag approved">✅ 已通过 (+{{ getSubPoints(item.task.id) }}⭐)</span>
          <span v-else-if="hasSubmitted(item.task.id) && getSubStatus(item.task.id) === 'rejected'" class="status-tag rejected">
            ❌ 已拒绝
            <span v-if="getSubNote(item.task.id)" class="reject-note">{{ getSubNote(item.task.id) }}</span>
          </span>
        </div>
        <p v-if="submitMsg && submitTaskId === item.task.id" class="msg">{{ submitMsg }}</p>
      </div>
      <p v-if="!loading && challenges.length === 0" class="empty">
        还没有领取任何挑战，去 <a @click="$router.push('/challenge-board')" style="color:#f39c12;cursor:pointer">挑战广场</a> 看看吧！
      </p>
    </section>

    <nav class="bottom-nav">
      <a @click="$router.push('/child')">📋 我的任务</a>
      <a @click="$router.push('/challenge-board')">🏆 挑战广场</a>
      <a class="active">🔥 我的挑战</a>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const router = useRouter()
const familyStore = useFamilyStore()
const auth = useAuthStore()

const challenges = ref<any[]>([])
const loading = ref(false)
const submitMsg = ref('')
const submitTaskId = ref<string | null>(null)
const mySubmissions = ref<Map<string, any>>(new Map())

const myPoints = computed(() => {
  const member = familyStore.family?.members?.find((m: any) => m.id === auth.user?.id)
  return member?.points || 0
})

function statusLabel(s: string) {
  return s === 'claimed' ? '待完成' : s === 'pending' ? '等待审核' : s === 'approved' ? '已完成' : s === 'rejected' ? '已拒绝' : s
}

function getDisplayStatus(item: any): string {
  const sub = mySubmissions.value.get(item.task.id)
  if (sub) return sub.status
  return item.claim_status
}

function hasSubmitted(taskId: string): boolean {
  return mySubmissions.value.has(taskId)
}

function getSubStatus(taskId: string): string {
  return mySubmissions.value.get(taskId)?.status || ''
}

function getSubPoints(taskId: string): number {
  return mySubmissions.value.get(taskId)?.points_earned || 0
}

function getSubNote(taskId: string): string {
  return mySubmissions.value.get(taskId)?.parent_note || ''
}

onMounted(async () => {
  loading.value = true
  try {
    const { data: chData } = await api.get('/challenges/my')
    challenges.value = chData
    await fetchMySubmissions()
  } catch {}
  loading.value = false
})

async function fetchMySubmissions() {
  try {
    const { data } = await api.get('/tasks/my-submissions')
    const map = new Map<string, any>()
    for (const s of data) {
      const existing = map.get(s.task_id)
      if (!existing || new Date(s.submitted_at) > new Date(existing.submitted_at)) {
        map.set(s.task_id, s)
      }
    }
    mySubmissions.value = map
  } catch {}
}

async function doSubmit(item: any) {
  submitMsg.value = ''
  try {
    const res = await familyStore.submitTask(item.task.id)
    mySubmissions.value.set(item.task.id, { status: 'pending', points_earned: 0, parent_note: '' })
    submitMsg.value = '已提交，等待家长审核'
    submitTaskId.value = item.task.id
  } catch (e: any) {
    submitMsg.value = e.response?.data?.detail || '提交失败'
    submitTaskId.value = item.task.id
  }
}

function goBack() {
  router.push('/child')
}
</script>

<style scoped>
.my-challenges { min-height: 100vh; background: #f0f2f5; padding-bottom: 60px; }
.header { padding: 16px 20px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; display: flex; align-items: center; gap: 12px; }
.header h1 { font-size: 18px; margin: 0; flex: 1; }
.back-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; padding: 0; }
.points { font-weight: 700; font-size: 16px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.challenge-card { background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.status { font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.status.claimed { background: #fef3e2; color: #f39c12; }
.status.pending { background: #fef3e2; color: #f39c12; }
.status.approved { background: #e8f8e8; color: #27ae60; }
.status.rejected { background: #fde8e8; color: #e74c3c; }
.multiplier { font-weight: 700; color: #e74c3c; font-size: 14px; }
.my-challenges h3 { margin: 0 0 6px; font-size: 16px; color: #333; }
.desc { color: #666; font-size: 13px; margin: 0 0 12px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.total-points { font-size: 18px; font-weight: 700; color: #f39c12; }
.btn { padding: 8px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.submit-btn { background: #27ae60; color: white; }
.status-tag { font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 6px; }
.status-tag.pending { background: #fef3e2; color: #f39c12; }
.status-tag.approved { background: #e8f8e8; color: #27ae60; }
.status-tag.rejected { background: #fde8e8; color: #e74c3c; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.reject-note { font-size: 12px; color: #999; font-weight: 400; }
.msg { font-size: 12px; color: #27ae60; margin-top: 6px; display: block; }
.loading, .empty { text-align: center; color: #999; padding: 24px; font-size: 14px; }
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; background: white;
  display: flex; border-top: 1px solid #eee; z-index: 10;
}
.bottom-nav a {
  flex: 1; text-align: center; padding: 12px 8px; font-size: 13px;
  color: #888; cursor: pointer; text-decoration: none;
}
.bottom-nav a.active { color: #e74c3c; font-weight: 600; }
</style>
