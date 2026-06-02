<template>
  <div class="challenge-board">
    <header class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>挑战广场</h1>
      <span class="points">⭐ {{ myPoints }}</span>
    </header>

    <section class="section">
      <p class="hint">发现感兴趣的挑战？领取后完成可获得倍率星星奖励！</p>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-for="c in challenges" :key="c.id" class="challenge-card" :class="{ claimed: c.claimed }">
        <div class="card-header">
          <span class="category" v-if="c.category">{{ c.category }}</span>
          <span class="multiplier">🔥 {{ c.multiplier }}x</span>
        </div>
        <h3>{{ c.title }}</h3>
        <p v-if="c.description" class="desc">{{ c.description }}</p>
        <div class="card-footer">
          <span class="total-points">⭐ {{ c.total_points }}</span>
          <button
            v-if="!c.claimed"
            class="btn claim-btn"
            @click="doClaim(c)"
            :disabled="claimingId === c.id"
          >
            {{ claimingId === c.id ? '领取中...' : '领取挑战' }}
          </button>
          <span v-else class="claimed-badge">已领取</span>
        </div>
        <p v-if="msg && msgTaskId === c.id" class="msg">{{ msg }}</p>
      </div>
      <p v-if="!loading && challenges.length === 0" class="empty">
        暂无挑战任务，等待家长发布！
      </p>
    </section>

    <nav class="bottom-nav">
      <a @click="$router.push('/child')">📋 我的任务</a>
      <a class="active">🏆 挑战广场</a>
      <a @click="$router.push('/my-challenges')">🔥 我的挑战</a>
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
const claimingId = ref<string | null>(null)
const msg = ref('')
const msgTaskId = ref<string | null>(null)

const myPoints = computed(() => {
  const member = familyStore.family?.members?.find((m: any) => m.id === auth.user?.id)
  return member?.points || 0
})

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/challenges/board')
    challenges.value = data
  } catch {}
  loading.value = false
})

async function doClaim(challenge: any) {
  claimingId.value = challenge.id
  msg.value = ''
  try {
    await api.post(`/challenges/${challenge.id}/claim`)
    challenge.claimed = true
    msg.value = '领取成功！去 "我的挑战" 完成任务吧'
    msgTaskId.value = challenge.id
  } catch (e: any) {
    msg.value = e.response?.data?.detail || '领取失败'
    msgTaskId.value = challenge.id
  } finally {
    claimingId.value = null
  }
}

function goBack() {
  router.push('/child')
}
</script>

<style scoped>
.challenge-board { min-height: 100vh; background: #f0f2f5; padding-bottom: 60px; }
.header { padding: 16px 20px; background: linear-gradient(135deg, #f39c12, #e67e22); color: white; display: flex; align-items: center; gap: 12px; }
.header h1 { font-size: 18px; margin: 0; flex: 1; }
.back-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; padding: 0; }
.points { font-weight: 700; font-size: 16px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.hint { color: #888; font-size: 13px; margin-bottom: 12px; }
.challenge-card { background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: opacity 0.2s; }
.challenge-card.claimed { opacity: 0.6; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.category { font-size: 11px; padding: 2px 8px; background: #fef3e2; color: #f39c12; border-radius: 10px; }
.multiplier { font-weight: 700; color: #e74c3c; font-size: 14px; }
.challenge-card h3 { margin: 0 0 6px; font-size: 16px; color: #333; }
.desc { color: #666; font-size: 13px; margin: 0 0 12px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.total-points { font-size: 18px; font-weight: 700; color: #f39c12; }
.btn { padding: 8px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.claim-btn { background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }
.claim-btn:disabled { opacity: 0.5; cursor: default; }
.claimed-badge { padding: 6px 16px; background: #e0e0e0; color: #999; border-radius: 8px; font-size: 13px; }
.msg { font-size: 12px; color: #27ae60; margin-top: 6px; }
.loading, .empty { text-align: center; color: #999; padding: 24px; font-size: 14px; }
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; background: white;
  display: flex; border-top: 1px solid #eee; z-index: 10;
}
.bottom-nav a {
  flex: 1; text-align: center; padding: 12px 8px; font-size: 13px;
  color: #888; cursor: pointer; text-decoration: none;
}
.bottom-nav a.active { color: #f39c12; font-weight: 600; }
</style>
