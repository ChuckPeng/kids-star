<template>
  <div class="shop">
    <header class="header">
      <button class="back-btn" @click="$router.push('/child')">←</button>
      <h1>星星商店</h1>
      <span class="points">⭐ {{ myPoints }}</span>
    </header>

    <section class="section">
      <p v-if="loading" class="loading">加载中...</p>
      <div v-for="r in rewards" :key="r.id" class="reward-card">
        <div class="card-header">
          <h3>{{ r.name }}</h3>
          <span class="cost">⭐ {{ r.points_cost }}</span>
        </div>
        <p v-if="r.description" class="desc">{{ r.description }}</p>
        <div class="card-footer">
          <span v-if="r.stock > 0" class="stock">库存 {{ r.stock }}</span>
          <span v-else-if="r.stock === 0" class="stock out">已售罄</span>
          <button
            class="btn redeem-btn"
            :disabled="myPoints < r.points_cost || r.stock === 0 || redeeming === r.id"
            @click="doRedeem(r)"
          >
            {{ redeeming === r.id ? '兑换中...' : myPoints < r.points_cost ? '星星不足' : r.stock === 0 ? '已售罄' : '兑换' }}
          </button>
        </div>
        <p v-if="msgs.get(r.id)" class="msg" :class="msgTypes.get(r.id)">{{ msgs.get(r.id) }}</p>
      </div>
      <p v-if="!loading && rewards.length === 0" class="empty">商店还没有商品，等待家长上架！</p>
    </section>

    <!-- My redemptions -->
    <section class="section">
      <h3>我的兑换记录</h3>
      <div v-for="rd in redemptions" :key="rd.id" class="redemption-card">
        <span>{{ rd.reward_name }}</span>
        <span class="rd-status" :class="rd.status">{{ rd.status === 'pending' ? '待审核' : rd.status === 'approved' ? '已通过' : '已拒绝' }}</span>
        <span class="rd-cost">⭐ {{ rd.points_spent }}</span>
      </div>
      <p v-if="redemptions.length === 0" class="empty">暂无兑换记录</p>
    </section>

    <nav class="bottom-nav">
      <a @click="$router.push('/child')">📋 任务</a>
      <a @click="$router.push('/challenge-board')">🏆 挑战</a>
      <a @click="$router.push('/shop')" class="active">🛒 商店</a>
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
const rewards = ref<any[]>([])
const redemptions = ref<any[]>([])
const loading = ref(false)
const redeeming = ref<string | null>(null)
const msgs = ref(new Map<string, string>())
const msgTypes = ref(new Map<string, string>())

const myPoints = computed(() => {
  const m = familyStore.family?.members?.find((x: any) => x.id === auth.user?.id)
  return m?.points || 0
})

onMounted(async () => {
  loading.value = true
  try {
    const [rRes, rdRes] = await Promise.all([api.get('/rewards'), api.get('/rewards/redemptions')])
    rewards.value = rRes.data
    redemptions.value = rdRes.data
  } catch {}
  loading.value = false
})

async function doRedeem(r: any) {
  redeeming.value = r.id
  msgs.value.set(r.id, '')
  try {
    await api.post(`/rewards/${r.id}/redeem`)
    msgs.value.set(r.id, '兑换申请已提交，等待家长审核')
    msgTypes.value.set(r.id, 'success')
    await familyStore.fetchMyFamily()
    const { data } = await api.get('/rewards/redemptions')
    redemptions.value = data
  } catch (e: any) {
    msgs.value.set(r.id, e.response?.data?.detail || '兑换失败')
    msgTypes.value.set(r.id, 'error')
  } finally {
    redeeming.value = null
  }
}
</script>

<style scoped>
.shop { min-height: 100vh; background: #f0f2f5; padding-bottom: 70px; }
.header { padding: 16px 20px; background: linear-gradient(135deg, #8e44ad, #6c3483); color: white; display: flex; align-items: center; gap: 12px; }
.header h1 { font-size: 18px; margin: 0; flex: 1; }
.back-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
.points { font-weight: 700; font-size: 16px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.section h3 { font-size: 15px; margin: 0 0 10px; }
.reward-card { background: white; border-radius: 12px; padding: 16px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 16px; }
.cost { font-size: 18px; font-weight: 700; color: #f39c12; }
.desc { color: #666; font-size: 13px; margin: 8px 0; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.stock { font-size: 12px; color: #999; }
.stock.out { color: #e74c3c; }
.btn { padding: 8px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.redeem-btn { background: #8e44ad; color: white; }
.redeem-btn:disabled { opacity: 0.4; cursor: default; }
.msg { font-size: 12px; margin-top: 6px; }
.msg.success { color: #27ae60; }
.msg.error { color: #e74c3c; }
.redemption-card { background: white; border-radius: 8px; padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.rd-status { font-weight: 600; }
.rd-status.pending { color: #f39c12; }
.rd-status.approved { color: #27ae60; }
.rd-status.rejected { color: #e74c3c; }
.rd-cost { color: #f39c12; font-weight: 600; }
.loading, .empty { text-align: center; color: #999; padding: 20px; font-size: 14px; }
.bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: white; display: flex; border-top: 1px solid #eee; z-index: 10; }
.bottom-nav a { flex: 1; text-align: center; padding: 10px 4px; font-size: 12px; color: #888; cursor: pointer; text-decoration: none; }
.bottom-nav a.active { color: #8e44ad; font-weight: 600; }
</style>
