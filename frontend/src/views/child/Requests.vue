<template>
  <div class="requests">
    <header class="header">
      <button class="back-btn" @click="$router.push('/child')">←</button>
      <h1>发起申请</h1>
      <span class="points">⭐ {{ myPoints }}</span>
    </header>

    <!-- Type selector -->
    <section class="section">
      <div class="tab-bar">
        <button :class="{ active: reqType === 'reward' }" @click="reqType = 'reward'">🌟 奖励申请</button>
        <button :class="{ active: reqType === 'proposal' }" @click="reqType = 'proposal'">💡 任务提议</button>
      </div>

      <!-- Reward application form -->
      <div v-if="reqType === 'reward'" class="form-card">
        <input v-model="rewardForm.title" placeholder="申请标题（如：数学考试满分）" />
        <textarea v-model="rewardForm.description" placeholder="描述你的成就" rows="2"></textarea>
        <div class="form-row">
          <label>申请星星</label>
          <input v-model.number="rewardForm.points_requested" type="number" min="1" max="50" />
        </div>
        <button class="btn primary" @click="submitReward" :disabled="!rewardForm.title">提交申请</button>
        <p v-if="msg" :class="msgType">{{ msg }}</p>
      </div>

      <!-- Task proposal form -->
      <div v-if="reqType === 'proposal'" class="form-card">
        <input v-model="proposalForm.title" placeholder="任务标题（如：每天阅读30分钟）" />
        <textarea v-model="proposalForm.description" placeholder="任务描述" rows="2"></textarea>
        <div class="form-row">
          <label>期望星星</label>
          <input v-model.number="proposalForm.points_requested" type="number" min="1" max="100" />
        </div>
        <button class="btn primary" @click="submitProposal" :disabled="!proposalForm.title">提交提议</button>
        <p v-if="msg" :class="msgType">{{ msg }}</p>
      </div>
    </section>

    <!-- History -->
    <section class="section">
      <h3>申请记录</h3>
      <div v-for="a in applications" :key="a.id" class="app-card">
        <div class="app-header">
          <span class="app-type" :class="a.type">{{ a.type === 'reward' ? '🌟 奖励' : '💡 提议' }}</span>
          <span class="app-status" :class="a.status">{{ statusLabel(a.status) }}</span>
        </div>
        <strong>{{ a.title }}</strong>
        <p v-if="a.description" class="desc">{{ a.description }}</p>
        <div class="app-footer">
          <span>申请 ⭐{{ a.points_requested }}</span>
          <span v-if="a.points_approved">批准 ⭐{{ a.points_approved }}</span>
          <span v-if="a.parent_note" class="note">💬 {{ a.parent_note }}</span>
        </div>
      </div>
      <p v-if="applications.length === 0" class="empty">暂无申请记录</p>
    </section>

    <nav class="bottom-nav">
      <a @click="$router.push('/child')">📋 任务</a>
      <a @click="$router.push('/challenge-board')">🏆 挑战</a>
      <a @click="$router.push('/shop')">🛒 商店</a>
      <a @click="$router.push('/requests')" class="active">📝 申请</a>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFamilyStore } from '@/stores/family'
import api from '@/api/client'

const auth = useAuthStore()
const familyStore = useFamilyStore()
const reqType = ref('reward')
const applications = ref<any[]>([])
const msg = ref('')
const msgType = ref('success')

const myPoints = ref(0)
const rewardForm = ref({ title: '', description: '', points_requested: 5 })
const proposalForm = ref({ title: '', description: '', points_requested: 10 })

function statusLabel(s: string) { return s === 'pending' ? '待审核' : s === 'approved' ? '已通过' : s === 'rejected' ? '已拒绝' : s }

onMounted(async () => {
  await familyStore.fetchMyFamily()
  const m = familyStore.family?.members?.find((x: any) => x.id === auth.user?.id)
  myPoints.value = m?.points || 0
  try { const { data } = await api.get('/applications'); applications.value = data } catch {}
})

async function submitReward() {
  msg.value = ''; msgType.value = 'success'
  try {
    await api.post('/applications/reward', rewardForm.value)
    msg.value = '奖励申请已提交！'; msgType.value = 'success'
    rewardForm.value = { title: '', description: '', points_requested: 5 }
    const { data } = await api.get('/applications'); applications.value = data
  } catch (e: any) { msg.value = e.response?.data?.detail || '提交失败'; msgType.value = 'error' }
}

async function submitProposal() {
  msg.value = ''; msgType.value = 'success'
  try {
    await api.post('/applications/proposal', proposalForm.value)
    msg.value = '任务提议已提交！'; msgType.value = 'success'
    proposalForm.value = { title: '', description: '', points_requested: 10 }
    const { data } = await api.get('/applications'); applications.value = data
  } catch (e: any) { msg.value = e.response?.data?.detail || '提交失败'; msgType.value = 'error' }
}
</script>

<style scoped>
.requests { min-height: 100vh; background: #f0f2f5; padding-bottom: 70px; }
.header { padding: 16px 20px; background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; display: flex; align-items: center; gap: 12px; }
.header h1 { font-size: 18px; margin: 0; flex: 1; }
.back-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
.points { font-weight: 700; font-size: 16px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.section h3 { font-size: 15px; margin: 16px 0 10px; }
.tab-bar { display: flex; gap: 8px; margin-bottom: 12px; }
.tab-bar button { flex: 1; padding: 10px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; background: white; color: #888; }
.tab-bar button.active { background: #2ecc71; color: white; }
.form-card { background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 10px; }
.form-card input, .form-card textarea { padding: 10px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 14px; font-family: inherit; }
.form-row { display: flex; align-items: center; gap: 8px; }
.form-row label { font-size: 13px; color: #666; white-space: nowrap; }
.form-row input { width: 80px; padding: 8px; }
.btn { padding: 10px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn.primary { background: #2ecc71; color: white; }
.btn.primary:disabled { opacity: 0.4; }
.msg { font-size: 13px; }
.msg.success { color: #27ae60; }
.msg.error { color: #e74c3c; }
.app-card { background: white; border-radius: 10px; padding: 14px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.app-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.app-type { font-size: 12px; font-weight: 600; }
.app-type.reward { color: #f39c12; }
.app-type.proposal { color: #3498db; }
.app-status { font-size: 12px; font-weight: 600; }
.app-status.pending { color: #f39c12; }
.app-status.approved { color: #27ae60; }
.app-status.rejected { color: #e74c3c; }
.desc { color: #666; font-size: 13px; margin: 4px 0; }
.app-footer { display: flex; gap: 12px; font-size: 12px; color: #999; margin-top: 6px; flex-wrap: wrap; }
.app-footer .note { color: #666; }
.loading, .empty { text-align: center; color: #999; padding: 20px; font-size: 14px; }
.bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: white; display: flex; border-top: 1px solid #eee; z-index: 10; }
.bottom-nav a { flex: 1; text-align: center; padding: 10px 4px; font-size: 12px; color: #888; cursor: pointer; text-decoration: none; }
.bottom-nav a.active { color: #2ecc71; font-weight: 600; }
</style>
