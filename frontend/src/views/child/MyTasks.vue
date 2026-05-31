<template>
  <div class="my-tasks">
    <header class="header">
      <h1>我的任务</h1>
      <div class="header-actions">
        <span class="points">⭐ {{ myPoints }}</span>
        <button class="btn-sm" @click="auth.logout()">退出</button>
      </div>
    </header>

    <section class="section">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-for="t in tasks" :key="t.id" class="task-card">
        <div class="task-header">
          <span class="task-badge" :class="t.difficulty">{{ t.difficulty === 'required' ? '必修' : '挑战' }}</span>
          <strong>{{ t.title }}</strong>
          <span class="task-points">⭐{{ t.base_points }}</span>
        </div>
        <p v-if="t.description" class="task-desc">{{ t.description }}</p>
        <button
          class="btn primary"
          @click="doSubmit(t)"
          :disabled="submittedTasks.has(t.id)"
        >
          {{ submittedTasks.has(t.id) ? '已提交' : '提交完成' }}
        </button>
        <span v-if="msg" class="msg">{{ msg }}</span>
      </div>
      <p v-if="!loading && tasks.length === 0" class="empty">暂无任务，去提醒家长分配吧！</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'

const familyStore = useFamilyStore()
const auth = useAuthStore()

const tasks = ref<any[]>([])
const loading = ref(false)
const msg = ref('')
const submittedTasks = ref(new Set<string>())

const myPoints = computed(() => {
  const member = familyStore.family?.members?.find((m: any) => m.id === auth.user?.id)
  return member?.points || 0
})

onMounted(async () => {
  loading.value = true
  await familyStore.fetchTasks()
  tasks.value = familyStore.tasks
  loading.value = false
})

async function doSubmit(task: any) {
  try {
    await familyStore.submitTask(task.id)
    submittedTasks.value.add(task.id)
    msg.value = '已提交，等待家长审核'
  } catch (e: any) {
    msg.value = e.response?.data?.detail || '提交失败'
  }
}
</script>

<style scoped>
.my-tasks { min-height: 100vh; background: #f0f2f5; padding-bottom: 40px; }
.header { padding: 16px 20px; background: #f39c12; color: white; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 18px; margin: 0; }
.header-actions { display: flex; gap: 12px; align-items: center; font-size: 14px; }
.points { font-weight: 700; font-size: 16px; }
.btn-sm { padding: 4px 12px; border: 1px solid rgba(255,255,255,0.5); border-radius: 6px; background: transparent; color: white; cursor: pointer; font-size: 12px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.task-card { background: white; border-radius: 10px; padding: 16px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.task-header { display: flex; align-items: center; gap: 8px; }
.task-badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.task-badge.required { background: #e8f0fe; color: #667eea; }
.task-badge.challenge { background: #fef3e2; color: #f39c12; }
.task-points { margin-left: auto; color: #f39c12; font-weight: 600; }
.task-desc { color: #666; font-size: 13px; margin: 8px 0; }
.btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; }
.btn.primary { background: #f39c12; color: white; }
.btn:disabled { opacity: 0.4; cursor: default; }
.msg { font-size: 12px; color: #27ae60; margin-left: 8px; }
.loading, .empty { text-align: center; color: #999; padding: 20px; }
</style>
