<template>
  <div class="dashboard">
    <header class="header">
      <h1>{{ family?.name || 'Kids-Star' }}</h1>
      <div class="header-actions">
        <span class="invite">邀请码: <strong>{{ family?.invite_code }}</strong></span>
        <button class="btn-sm" @click="auth.logout()">退出</button>
      </div>
    </header>

    <!-- Children -->
    <section v-if="family?.members" class="section">
      <h3>家庭成员</h3>
      <div class="member-list">
        <div v-for="m in children" :key="m.id" class="member-card">
          <div class="member-name">{{ m.nickname || m.name }}</div>
          <div class="member-points">⭐ {{ m.points }}</div>
        </div>
      </div>
    </section>

    <!-- Create Task -->
    <section class="section">
      <h3>{{ showCreate ? '创建任务' : '任务列表' }}</h3>
      <button v-if="!showCreate" class="btn primary" @click="showCreate = true">+ 新建任务</button>
      <div v-else class="create-form">
        <input v-model="form.title" placeholder="任务标题" />
        <select v-model="form.difficulty">
          <option value="required">必修任务</option>
          <option value="challenge">挑战任务</option>
        </select>
        <input v-model.number="form.base_points" type="number" placeholder="星星数" />
        <div class="member-select">
          <label v-for="c in children" :key="c.id">
            <input type="checkbox" :value="c.id" v-model="form.assigned_to" /> {{ c.nickname || c.name }}
          </label>
        </div>
        <div class="btn-row">
          <button class="btn primary" @click="doCreateTask">创建</button>
          <button class="btn secondary" @click="showCreate = false">取消</button>
        </div>
      </div>
    </section>

    <!-- Tasks -->
    <section class="section">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-for="t in tasks" :key="t.id" class="task-card">
        <div class="task-header">
          <span class="task-badge" :class="t.difficulty">{{ t.difficulty === 'required' ? '必修' : '挑战' }}</span>
          <strong>{{ t.title }}</strong>
          <span class="task-points">⭐{{ t.base_points }}</span>
        </div>
        <div class="task-status">{{ t.status }}</div>
        <button v-if="t.status === 'active'" class="btn-sm" @click="openReview(t)">查看提交</button>
      </div>
    </section>

    <!-- Review Modal -->
    <div v-if="reviewTask" class="modal">
      <div class="modal-content">
        <h3>{{ reviewTask.title }} - 提交记录</h3>
        <div v-if="reviewSubmissions.length === 0">暂无提交</div>
        <div v-for="s in reviewSubmissions" :key="s.id" class="submission-card">
          <p><strong>状态:</strong> {{ s.status }}</p>
          <p v-if="s.child_note">备注: {{ s.child_note }}</p>
          <div v-if="s.status === 'pending'" class="btn-row">
            <button class="btn primary" @click="doReview(s, 'approved')">✓ 通过</button>
            <button class="btn danger" @click="doReview(s, 'rejected')">✕ 拒绝</button>
          </div>
        </div>
        <button class="btn secondary" @click="reviewTask = null; reviewSubmissions = []">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'

const familyStore = useFamilyStore()
const auth = useAuthStore()

const family = computed(() => familyStore.family)
const tasks = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const reviewTask = ref<any>(null)
const reviewSubmissions = ref<any[]>([])

const children = computed(() => family.value?.members?.filter((m: any) => m.role === 'child') || [])

const form = ref({ title: '', difficulty: 'required', base_points: 5, assigned_to: [] as string[] })

onMounted(async () => {
  loading.value = true
  await familyStore.fetchTasks()
  tasks.value = familyStore.tasks
  loading.value = false
})

async function doCreateTask() {
  await familyStore.createTask(form.value)
  form.value = { title: '', difficulty: 'required', base_points: 5, assigned_to: [] }
  showCreate.value = false
  await familyStore.fetchTasks()
  tasks.value = familyStore.tasks
}

async function openReview(task: any) {
  reviewTask.value = task
  reviewSubmissions.value = await familyStore.fetchSubmissions(task.id)
}

async function doReview(sub: any, status: string) {
  await familyStore.reviewTask(sub.task_id, status)
  openReview(reviewTask.value)
}
</script>

<style scoped>
.dashboard { min-height: 100vh; background: #f0f2f5; padding-bottom: 40px; }
.header { padding: 16px 20px; background: #667eea; color: white; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 18px; margin: 0; }
.header-actions { display: flex; gap: 12px; align-items: center; font-size: 13px; }
.invite strong { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; }
.btn-sm { padding: 4px 12px; border: 1px solid rgba(255,255,255,0.5); border-radius: 6px; background: transparent; color: white; cursor: pointer; font-size: 12px; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.section h3 { font-size: 16px; margin-bottom: 12px; }
.member-list { display: flex; gap: 10px; flex-wrap: wrap; }
.member-card { background: white; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); text-align: center; min-width: 80px; }
.member-name { font-weight: 600; font-size: 14px; }
.member-points { color: #f39c12; font-size: 18px; font-weight: 700; margin-top: 4px; }
.create-form { background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 10px; }
.create-form input, .create-form select { padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 14px; }
.member-select { display: flex; gap: 12px; flex-wrap: wrap; font-size: 13px; }
.member-select label { display: flex; align-items: center; gap: 4px; cursor: pointer; }
.btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn.primary { background: #667eea; color: white; }
.btn.secondary { background: #f0f2f5; color: #333; }
.btn.danger { background: #e74c3c; color: white; }
.btn-row { display: flex; gap: 8px; }
.task-card { background: white; border-radius: 10px; padding: 14px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.task-header { display: flex; align-items: center; gap: 8px; }
.task-badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.task-badge.required { background: #e8f0fe; color: #667eea; }
.task-badge.challenge { background: #fef3e2; color: #f39c12; }
.task-points { margin-left: auto; color: #f39c12; font-weight: 600; }
.task-status { font-size: 12px; color: #999; margin-top: 4px; }
.loading { text-align: center; color: #999; padding: 20px; }
.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-content { background: white; border-radius: 12px; padding: 24px; max-width: 440px; width: 90%; max-height: 80vh; overflow-y: auto; }
.submission-card { border: 1px solid #eee; border-radius: 8px; padding: 12px; margin: 8px 0; }
</style>
