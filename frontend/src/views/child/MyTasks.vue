<template>
  <div class="my-tasks">
    <header class="header">
      <h1>我的任务</h1>
      <div class="header-actions">
        <span class="points">⭐ {{ myPoints }}</span>
        <button class="btn-sm" @click="auth.logout()">退出</button>
      </div>
    </header>

    <!-- ========== 必修任务 ========== -->
    <section class="section">
      <div class="section-header">
        <h3>📋 必修任务</h3>
        <span class="count-badge">{{ requiredTasks.length }}</span>
      </div>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-for="t in requiredTasks" :key="t.id" class="task-card required-card">
        <div class="task-header">
          <span class="task-badge required">必修</span>
          <strong>{{ t.title }}</strong>
          <span class="task-points">⭐{{ t.base_points }}</span>
        </div>
        <p v-if="t.description" class="task-desc">{{ t.description }}</p>
        <div class="task-actions">
          <button v-if="!getSubStatus(t.id)" class="btn primary" @click="doSubmit(t)">提交完成</button>
          <span v-else-if="getSubStatus(t.id) === 'pending'" class="status-tag pending">⏳ 等待审核</span>
          <span v-else-if="getSubStatus(t.id) === 'approved'" class="status-tag approved">✅ 已通过 (+{{ getSubPoints(t.id) }}⭐)</span>
          <span v-else-if="getSubStatus(t.id) === 'rejected'" class="status-tag rejected">
            ❌ 已拒绝
            <span v-if="getSubNote(t.id)" class="reject-note">{{ getSubNote(t.id) }}</span>
            <button class="btn retry-btn" @click="doResubmit(t)">重新提交</button>
          </span>
        </div>
        <p v-if="taskMsgs.get(t.id)" class="msg">{{ taskMsgs.get(t.id) }}</p>
      </div>
      <p v-if="!loading && requiredTasks.length === 0" class="empty">暂无必修任务</p>
    </section>

    <!-- ========== 挑战任务 ========== -->
    <section class="section">
      <div class="section-header">
        <h3>🏆 挑战任务</h3>
        <span class="count-badge challenge-count">{{ myChallenges.length }}</span>
      </div>
      <div v-for="item in myChallenges" :key="item.claim_id" class="task-card challenge-card">
        <div class="task-header">
          <span class="task-badge challenge">挑战</span>
          <strong>{{ item.task.title }}</strong>
          <span class="task-points">⭐{{ item.task.total_points }}</span>
        </div>
        <p v-if="item.task.description" class="task-desc">{{ item.task.description }}</p>
        <div class="challenge-meta">
          <span class="multiplier-tag">🔥 {{ item.task.multiplier }}x</span>
        </div>
        <div class="task-actions">
          <button v-if="!getSubStatus(item.task.id)" class="btn primary" @click="doSubmitChallenge(item)">提交完成</button>
          <span v-else-if="getSubStatus(item.task.id) === 'pending'" class="status-tag pending">⏳ 等待审核</span>
          <span v-else-if="getSubStatus(item.task.id) === 'approved'" class="status-tag approved">✅ 已通过 (+{{ getSubPoints(item.task.id) }}⭐)</span>
          <span v-else-if="getSubStatus(item.task.id) === 'rejected'" class="status-tag rejected">
            ❌ 已拒绝
            <span v-if="getSubNote(item.task.id)" class="reject-note">{{ getSubNote(item.task.id) }}</span>
          </span>
        </div>
        <p v-if="taskMsgs.get(item.task.id)" class="msg">{{ taskMsgs.get(item.task.id) }}</p>
      </div>
      <p v-if="!loading && myChallenges.length === 0" class="empty">
        还没领取挑战，去 <a @click="$router.push('/challenge-board')" class="link">挑战广场</a> 看看吧！
      </p>
    </section>

    <nav class="bottom-nav">
      <a class="active">📋 任务</a>
      <a @click="$router.push('/challenge-board')">🏆 挑战</a>
      <a @click="$router.push('/shop')">🛒 商店</a>
      <a @click="$router.push('/requests')">📝 申请</a>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const familyStore = useFamilyStore()
const auth = useAuthStore()

const allTasks = ref<any[]>([])
const myChallenges = ref<any[]>([])
const loading = ref(false)
const taskMsgs = ref(new Map<string, string>())
const mySubmissions = ref<Map<string, any>>(new Map())

const requiredTasks = computed(() => allTasks.value.filter((t: any) => t.difficulty === 'required'))
const myPoints = computed(() => {
  const member = familyStore.family?.members?.find((m: any) => m.id === auth.user?.id)
  return member?.points || 0
})

function getSubStatus(taskId: string): string | null {
  return mySubmissions.value.get(taskId)?.status || null
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
    const [taskRes, challengeRes] = await Promise.all([
      api.get('/tasks'),
      api.get('/challenges/my'),
    ])
    allTasks.value = taskRes.data
    myChallenges.value = challengeRes.data
  } catch {}
  await fetchMySubmissions()
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

async function doSubmit(task: any) {
  taskMsgs.value.set(task.id, '')
  try {
    await familyStore.submitTask(task.id)
    mySubmissions.value.set(task.id, { status: 'pending', points_earned: 0, parent_note: '' })
    taskMsgs.value.set(task.id, '已提交，等待家长审核')
  } catch (e: any) {
    taskMsgs.value.set(task.id, e.response?.data?.detail || '提交失败')
  }
}

async function doSubmitChallenge(item: any) {
  taskMsgs.value.set(item.task.id, '')
  try {
    await familyStore.submitTask(item.task.id)
    mySubmissions.value.set(item.task.id, { status: 'pending', points_earned: 0, parent_note: '' })
    taskMsgs.value.set(item.task.id, '已提交，等待家长审核')
  } catch (e: any) {
    taskMsgs.value.set(item.task.id, e.response?.data?.detail || '提交失败')
  }
}

async function doResubmit(task: any) {
  mySubmissions.value.delete(task.id)
  taskMsgs.value.set(task.id, '')
}
</script>

<style scoped>
.my-tasks { min-height: 100vh; background: #f0f2f5; padding-bottom: 60px; }
.header { padding: 16px 20px; background: #f39c12; color: white; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 18px; margin: 0; }
.header-actions { display: flex; gap: 12px; align-items: center; font-size: 14px; }
.points { font-weight: 700; font-size: 16px; }
.btn-sm { padding: 4px 12px; border: 1px solid rgba(255,255,255,0.5); border-radius: 6px; background: transparent; color: white; cursor: pointer; font-size: 12px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-header h3 { font-size: 16px; margin: 0; }
.count-badge { background: #e8f0fe; color: #667eea; padding: 2px 10px; border-radius: 10px; font-size: 13px; font-weight: 600; }
.count-badge.challenge-count { background: #fef3e2; color: #f39c12; }
.task-card { background: white; border-radius: 10px; padding: 16px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.required-card { border-left: 3px solid #667eea; }
.challenge-card { border-left: 3px solid #f39c12; }
.task-header { display: flex; align-items: center; gap: 8px; }
.task-badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.task-badge.required { background: #e8f0fe; color: #667eea; }
.task-badge.challenge { background: #fef3e2; color: #f39c12; }
.task-points { margin-left: auto; color: #f39c12; font-weight: 600; }
.task-desc { color: #666; font-size: 13px; margin: 8px 0; }
.challenge-meta { margin-bottom: 6px; }
.multiplier-tag { font-size: 12px; font-weight: 700; color: #e74c3c; }
.task-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; }
.btn.primary { background: #f39c12; color: white; }
.retry-btn { padding: 4px 10px; font-size: 12px; background: #667eea; color: white; border-radius: 6px; }
.status-tag { font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 6px; }
.status-tag.pending { background: #fef3e2; color: #f39c12; }
.status-tag.approved { background: #e8f8e8; color: #27ae60; }
.status-tag.rejected { background: #fde8e8; color: #e74c3c; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.reject-note { font-size: 12px; color: #999; font-weight: 400; }
.msg { font-size: 12px; color: #27ae60; margin-top: 6px; display: block; }
.link { color: #f39c12; cursor: pointer; text-decoration: underline; }
.loading, .empty { text-align: center; color: #999; padding: 20px; font-size: 14px; }
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; background: white;
  display: flex; border-top: 1px solid #eee; z-index: 10;
}
.bottom-nav a {
  flex: 1; text-align: center; padding: 12px 8px; font-size: 13px;
  color: #888; cursor: pointer; text-decoration: none;
}
.bottom-nav a.active { color: #667eea; font-weight: 600; }
</style>

