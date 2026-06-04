<template>
  <div class="dashboard">
    <header class="header">
      <h1>{{ family?.name || 'Kids-Star' }}</h1>
      <div class="header-actions">
        <button class="btn-sm" @click="auth.logout()">退出</button>
      </div>
    </header>

    <!-- Invite code -->
    <section class="section">
      <div class="invite-box">
        <span>邀请码: <strong>{{ family?.invite_code }}</strong></span>
        <span class="hint">孩子用此码登录</span>
      </div>
    </section>

    <!-- Children -->
    <section class="section">
      <div class="section-header">
        <h3>家庭成员</h3>
        <button class="btn-sm-outline" @click="showAddChild = !showAddChild">
          {{ showAddChild ? '取消' : '+ 添加孩子' }}
        </button>
      </div>
      <div v-if="showAddChild" class="add-child-form">
        <input v-model="childForm.nickname" placeholder="孩子昵称（如：小明）" />
        <button class="btn primary small" @click="doAddChild" :disabled="!childForm.nickname">创建</button>
        <p v-if="addChildMsg" class="msg">{{ addChildMsg }}</p>
      </div>
      <div class="member-list">
        <div v-for="m in children" :key="m.id" class="member-card">
          <div class="member-avatar">👦</div>
          <div class="member-name">{{ m.nickname || m.name }}</div>
          <div class="member-points">⭐ {{ m.points }}</div>
        </div>
        <div v-if="children.length === 0" class="empty-hint">还没有添加孩子，点击上方按钮添加</div>
      </div>
    </section>

    <!-- Create task -->
    <section class="section">
      <div class="section-header">
        <h3>{{ showCreate ? '创建任务' : '任务管理' }}</h3>
        <button v-if="!showCreate" class="btn primary small" @click="showCreate = true">+ 新建任务</button>
        <button v-else class="btn-sm-outline" @click="showCreate = false">取消</button>
      </div>
      <div v-if="showCreate" class="create-form">
        <input v-model="form.title" placeholder="任务标题" />
        <textarea v-model="form.description" placeholder="任务描述（可选）" rows="2"></textarea>
        <div class="form-row">
          <select v-model="form.difficulty">
            <option value="required">必修任务</option>
            <option value="challenge">挑战任务</option>
          </select>
          <input v-model.number="form.base_points" type="number" placeholder="星星数" min="1" max="100" />
        </div>
        <div v-if="form.difficulty === 'required' && children.length > 0" class="member-select">
          <span class="label">分配给:</span>
          <label v-for="c in children" :key="c.id">
            <input type="checkbox" :value="c.id" v-model="form.assigned_to" /> {{ c.nickname || c.name }}
          </label>
        </div>
        <p v-if="form.difficulty === 'challenge'" class="hint">挑战任务将发布到挑战广场，孩子自主领取</p>
        <div class="btn-row">
          <button class="btn primary" @click="doCreateTask" :disabled="!form.title">创建任务</button>
        </div>
      </div>
    </section>

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
        <div class="assigned-children">
          <span class="label">分配给：</span>
          <span v-for="cid in t.assigned_to" :key="cid" class="child-chip">{{ getChildName(cid) }}</span>
          <span v-if="!t.assigned_to || t.assigned_to.length === 0" class="no-assign">未指定</span>
        </div>
        <div class="task-actions">
          <span class="task-status">{{ statusLabel(t.status) }}</span>
          <div class="action-btns">
            <button class="btn secondary small" @click="openReview(t)">查看提交</button>
            <button class="btn outline small" @click="openEdit(t)">编辑</button>
            <button class="btn danger small" @click="confirmDelete(t)">删除</button>
          </div>
        </div>
      </div>
      <p v-if="!loading && requiredTasks.length === 0" class="empty">暂无必修任务</p>
    </section>

    <!-- ========== 挑战任务 ========== -->
    <section class="section">
      <div class="section-header">
        <h3>🏆 挑战任务</h3>
        <span class="count-badge challenge-count">{{ challengeTasks.length }}</span>
      </div>
      <div v-for="t in challengeTasks" :key="t.id" class="task-card challenge-card">
        <div class="task-header">
          <span class="task-badge challenge">挑战</span>
          <strong>{{ t.title }}</strong>
          <span class="task-points">⭐{{ t.base_points }} ×{{ getMultiplier(t) }} = {{ getTotalPoints(t) }}</span>
        </div>
        <p v-if="t.description" class="task-desc">{{ t.description }}</p>
        <div class="challenge-meta">
          <span class="claim-count">👥 {{ getClaimCount(t.id) }} 人已领取</span>
        </div>
        <div class="task-actions">
          <span class="task-status">{{ statusLabel(t.status) }}</span>
          <div class="action-btns">
            <button class="btn secondary small" @click="openReview(t)">查看提交</button>
            <button class="btn outline small" @click="openEdit(t)">编辑</button>
            <button class="btn danger small" @click="confirmDelete(t)">删除</button>
          </div>
        </div>
      </div>
      <p v-if="!loading && challengeTasks.length === 0" class="empty">暂无挑战任务，发布一个到挑战广场吧！</p>
    </section>

    <!-- Review Modal -->
    <div v-if="reviewTask" class="modal" @click.self="closeReview">
      <div class="modal-content">
        <h3>
          <span :class="reviewTask.difficulty === 'challenge' ? 'badge-challenge' : 'badge-required'">
            {{ reviewTask.difficulty === 'challenge' ? '挑战' : '必修' }}
          </span>
          {{ reviewTask.title }} - 提交记录
        </h3>
        <div v-if="subLoading" class="loading">加载中...</div>
        <div v-else-if="reviewSubmissions.length === 0" class="empty">暂无提交记录</div>
        <div v-for="s in reviewSubmissions" :key="s.id" class="submission-card">
          <div class="sub-header">
            <span class="sub-child">👤 {{ s.child_name || '未知' }}</span>
            <span class="sub-status" :class="s.status">{{ s.status === 'pending' ? '待审核' : s.status === 'approved' ? '已通过' : '已拒绝' }}</span>
            <span class="sub-time">{{ formatTime(s.submitted_at) }}</span>
          </div>
          <p v-if="s.child_note">📝 {{ s.child_note }}</p>
          <div v-if="s.status === 'pending'" class="review-actions">
            <button class="btn success small" @click="doApprove(s)">✓ 通过</button>
            <button class="btn danger small" @click="startReject(s)">✕ 拒绝</button>
          </div>
          <div v-if="rejecting?.id === s.id" class="reject-form">
            <textarea v-model="rejectNote" placeholder="请输入拒绝原因（可选）" rows="2"></textarea>
            <div class="btn-row">
              <button class="btn danger small" @click="doReject(s)">确认拒绝</button>
              <button class="btn secondary small" @click="cancelReject()">取消</button>
            </div>
          </div>
          <p v-if="s.parent_note" class="review-note">💬 家长评语: {{ s.parent_note }}</p>
        </div>
        <p v-if="reviewMsg" class="review-feedback" :class="reviewMsgType">{{ reviewMsg }}</p>
        <button class="btn secondary" @click="closeReview">关闭</button>
      </div>
    </div>

    <!-- Edit Task Modal -->
    <div v-if="editingTask" class="modal" @click.self="cancelEdit">
      <div class="modal-content">
        <h3>编辑任务</h3>
        <div class="edit-form">
          <label>标题</label>
          <input v-model="editForm.title" placeholder="任务标题" />
          <label>描述</label>
          <textarea v-model="editForm.description" placeholder="任务描述（可选）" rows="2"></textarea>
          <div class="form-row">
            <label>星星数</label>
            <input v-model.number="editForm.base_points" type="number" min="1" max="100" />
            <label>类型</label>
            <select v-model="editForm.difficulty">
              <option value="required">必修</option>
              <option value="challenge">挑战</option>
            </select>
          </div>
          <div v-if="editForm.difficulty === 'required' && children.length > 0" class="member-select">
            <span class="label">分配给:</span>
            <label v-for="c in children" :key="c.id">
              <input type="checkbox" :value="c.id" v-model="editForm.assigned_to" /> {{ c.nickname || c.name }}
            </label>
          </div>
          <label>状态</label>
          <select v-model="editForm.status">
            <option value="active">进行中</option>
            <option value="paused">暂停</option>
            <option value="completed">已完成</option>
          </select>
          <div class="btn-row">
            <button class="btn primary" @click="doEdit" :disabled="!editForm.title">保存</button>
            <button class="btn secondary" @click="cancelEdit">取消</button>
          </div>
          <p v-if="editMsg" class="msg" :class="editMsgType">{{ editMsg }}</p>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Dialog -->
    <div v-if="deletingTask" class="modal" @click.self="cancelDelete">
      <div class="modal-content modal-sm">
        <h3>确认删除</h3>
        <p>确定要删除任务「<strong>{{ deletingTask.title }}</strong>」吗？此操作不可撤销，所有相关提交记录也将被删除。</p>
        <div class="btn-row">
          <button class="btn danger" @click="doDelete">确认删除</button>
          <button class="btn secondary" @click="cancelDelete">取消</button>
        </div>
        <p v-if="deleteMsg" class="msg error">{{ deleteMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const familyStore = useFamilyStore()
const auth = useAuthStore()

const family = computed(() => familyStore.family)
const tasks = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const showAddChild = ref(false)
const reviewTask = ref<any>(null)
const reviewSubmissions = ref<any[]>([])
const subLoading = ref(false)
const addChildMsg = ref('')
const claimCounts = ref<Record<string, number>>({})

const rejecting = ref<any>(null)
const rejectNote = ref('')
const reviewMsg = ref('')
const reviewMsgType = ref('success')
const editingTask = ref<any>(null)
const editForm = ref({ title: '', description: '', difficulty: 'required', base_points: 5, assigned_to: [] as string[], status: 'active' })
const editMsg = ref('')
const editMsgType = ref('success')
const deletingTask = ref<any>(null)
const deleteMsg = ref('')

const childForm = ref({ nickname: '' })
const form = ref({ title: '', description: '', difficulty: 'required', base_points: 5, assigned_to: [] as string[] })

const children = computed(() => family.value?.members?.filter((m: any) => m.role === 'child') || [])

const requiredTasks = computed(() => tasks.value.filter((t: any) => t.difficulty === 'required'))
const challengeTasks = computed(() => tasks.value.filter((t: any) => t.difficulty === 'challenge'))

function getChildName(cid: string): string {
  const child = children.value.find((c: any) => c.id === cid || c.user_id === cid)
  return child?.nickname || child?.name || '未知'
}

function getMultiplier(task: any): number {
  return task.challenge_multiplier || 1.5
}

function getTotalPoints(task: any): number {
  return Math.floor(task.base_points * getMultiplier(task))
}

function getClaimCount(taskId: string): number {
  return claimCounts.value[taskId] || 0
}

function statusLabel(s: string) {
  return s === 'active' ? '进行中' : s === 'completed' ? '已完成' : s === 'paused' ? '已暂停' : s
}

function formatTime(t: string) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(async () => {
  loading.value = true
  await familyStore.fetchTasks()
  tasks.value = familyStore.tasks
  await fetchClaimCounts()
  loading.value = false
})

async function fetchClaimCounts() {
  try {
    const { data } = await api.get('/challenges/claims/counts')
    claimCounts.value = data
  } catch {}
}

async function doAddChild() {
  addChildMsg.value = ''
  try {
    await api.post('/families/children', { name: childForm.value.nickname, nickname: childForm.value.nickname })
    childForm.value.nickname = ''
    showAddChild.value = false
    addChildMsg.value = '孩子添加成功！'
    await familyStore.fetchMyFamily()
  } catch (e: any) {
    addChildMsg.value = e.response?.data?.detail || '添加失败'
  }
}

async function doCreateTask() {
  await familyStore.createTask(form.value)
  form.value = { title: '', description: '', difficulty: 'required', base_points: 5, assigned_to: [] }
  showCreate.value = false
  await familyStore.fetchTasks()
  tasks.value = familyStore.tasks
}

async function openReview(task: any) {
  reviewTask.value = task
  reviewMsg.value = ''
  rejecting.value = null
  rejectNote.value = ''
  subLoading.value = true
  try {
    reviewSubmissions.value = await familyStore.fetchSubmissions(task.id)
  } catch {}
  subLoading.value = false
}

function closeReview() {
  reviewTask.value = null
  reviewSubmissions.value = []
  reviewMsg.value = ''
  rejecting.value = null
  rejectNote.value = ''
}

async function doApprove(sub: any) {
  reviewMsg.value = ''
  try {
    await familyStore.reviewTask(sub.task_id, 'approved')
    reviewMsg.value = '✅ 已通过，星星已发放'
    reviewMsgType.value = 'success'
    await refreshReviewData()
  } catch (e: any) {
    reviewMsg.value = '❌ ' + (e.response?.data?.detail || '操作失败')
    reviewMsgType.value = 'error'
  }
}

function startReject(sub: any) {
  rejecting.value = sub
  rejectNote.value = ''
}

function cancelReject() {
  rejecting.value = null
  rejectNote.value = ''
}

async function doReject(sub: any) {
  reviewMsg.value = ''
  try {
    await familyStore.reviewTask(sub.task_id, 'rejected', rejectNote.value)
    reviewMsg.value = '❌ 已拒绝'
    reviewMsgType.value = 'error'
    rejecting.value = null
    rejectNote.value = ''
    await refreshReviewData()
  } catch (e: any) {
    reviewMsg.value = '❌ ' + (e.response?.data?.detail || '操作失败')
    reviewMsgType.value = 'error'
  }
}

// ── Edit Task ──
function openEdit(task: any) {
  editingTask.value = task
  editForm.value = {
    title: task.title,
    description: task.description || "",
    difficulty: task.difficulty,
    base_points: task.base_points,
    assigned_to: [...(task.assigned_to || [])],
    status: task.status,
  }
  editMsg.value = ""
}

function cancelEdit() {
  editingTask.value = null
  editMsg.value = ""
}

async function doEdit() {
  editMsg.value = ""
  try {
    await api.patch("/tasks/" + editingTask.value.id, editForm.value)
    editMsg.value = "已保存"
    editMsgType.value = "success"
    editingTask.value = null
    await familyStore.fetchTasks()
    tasks.value = familyStore.tasks
  } catch (e: any) {
    editMsg.value = e.response?.data?.detail || "保存失败"
    editMsgType.value = "error"
  }
}

// ── Delete Task ──
function confirmDelete(task: any) {
  deletingTask.value = task
  deleteMsg.value = ""
}

function cancelDelete() {
  deletingTask.value = null
  deleteMsg.value = ""
}

async function doDelete() {
  deleteMsg.value = ""
  try {
    await api.delete("/tasks/" + deletingTask.value.id)
    deletingTask.value = null
    await familyStore.fetchTasks()
    tasks.value = familyStore.tasks
  } catch (e: any) {
    deleteMsg.value = e.response?.data?.detail || "删除失败"
  }
}

async function refreshReviewData() {
  await openReview(reviewTask.value)
  await familyStore.fetchTasks()
  tasks.value = familyStore.tasks
}
</script>

<style scoped>
.dashboard { min-height: 100vh; background: #f0f2f5; padding-bottom: 40px; }
.header { padding: 16px 20px; background: #667eea; color: white; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 18px; margin: 0; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.btn-sm { padding: 4px 12px; border: 1px solid rgba(255,255,255,0.5); border-radius: 6px; background: transparent; color: white; cursor: pointer; font-size: 12px; }
.btn-sm-outline { padding: 6px 14px; border: 1px solid #d9d9d9; border-radius: 6px; background: white; color: #667eea; cursor: pointer; font-size: 13px; font-weight: 500; }
.section { max-width: 600px; margin: 16px auto; padding: 0 16px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-header h3 { font-size: 16px; margin: 0; }
.count-badge { background: #e8f0fe; color: #667eea; padding: 2px 10px; border-radius: 10px; font-size: 13px; font-weight: 600; }
.count-badge.challenge-count { background: #fef3e2; color: #f39c12; }
.invite-box { background: white; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); display: flex; justify-content: space-between; align-items: center; }
.invite-box strong { background: #e8f0fe; padding: 2px 10px; border-radius: 4px; color: #667eea; }
.hint { font-size: 12px; color: #999; }
.member-list { display: flex; gap: 10px; flex-wrap: wrap; }
.member-card { background: white; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); text-align: center; min-width: 80px; }
.member-avatar { font-size: 28px; }
.member-name { font-weight: 600; font-size: 14px; margin-top: 4px; }
.member-points { color: #f39c12; font-size: 16px; font-weight: 700; margin-top: 2px; }
.empty-hint { color: #999; font-size: 13px; padding: 12px; }
.add-child-form { background: white; border-radius: 10px; padding: 14px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.add-child-form input { flex: 1; min-width: 120px; padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 14px; }
.msg { font-size: 12px; color: #27ae60; width: 100%; margin: 4px 0 0; }
.create-form { background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 10px; margin-bottom: 8px; }
.create-form input, .create-form select, .create-form textarea { padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 14px; font-family: inherit; }
.form-row { display: flex; gap: 8px; }
.form-row select { flex: 1; }
.form-row input { width: 90px; }
.member-select { display: flex; gap: 12px; flex-wrap: wrap; font-size: 13px; align-items: center; }
.member-select .label { color: #888; }
.member-select label { display: flex; align-items: center; gap: 4px; cursor: pointer; }
.btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn.small { padding: 6px 14px; font-size: 13px; }
.btn.primary { background: #667eea; color: white; }
.btn.primary:disabled { opacity: 0.5; cursor: default; }
.btn.secondary { background: #f0f2f5; color: #333; }
.btn.success { background: #27ae60; color: white; }
.btn.danger { background: #e74c3c; color: white; }
.btn-row { display: flex; gap: 8px; }

/* Task cards */
.task-card { background: white; border-radius: 10px; padding: 14px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.required-card { border-left: 3px solid #667eea; }
.challenge-card { border-left: 3px solid #f39c12; }
.task-header { display: flex; align-items: center; gap: 8px; }
.task-badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.task-badge.required { background: #e8f0fe; color: #667eea; }
.task-badge.challenge { background: #fef3e2; color: #f39c12; }
.task-points { margin-left: auto; color: #f39c12; font-weight: 600; font-size: 13px; }
.task-desc { color: #666; font-size: 13px; margin: 6px 0; }
.assigned-children { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin: 6px 0; font-size: 12px; }
.assigned-children .label { color: #999; }
.child-chip { background: #e8f0fe; color: #667eea; padding: 1px 8px; border-radius: 8px; font-weight: 500; }
.no-assign { color: #ccc; font-style: italic; }
.challenge-meta { margin: 6px 0; }
.claim-count { font-size: 12px; color: #f39c12; font-weight: 500; }
.task-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.task-status { font-size: 12px; color: #999; }
.loading, .empty { text-align: center; color: #999; padding: 20px; font-size: 14px; }

/* Modal */
.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-content { background: white; border-radius: 12px; padding: 24px; max-width: 480px; width: 90%; max-height: 80vh; overflow-y: auto; }
.modal-content h3 { margin: 0 0 16px; font-size: 17px; display: flex; align-items: center; gap: 8px; }
.badge-required { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #e8f0fe; color: #667eea; }
.badge-challenge { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #fef3e2; color: #f39c12; }
.submission-card { border: 1px solid #eee; border-radius: 8px; padding: 12px; margin: 8px 0; }
.sub-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 13px; gap: 8px; flex-wrap: wrap; }
.sub-child { font-weight: 600; color: #333; }
.sub-status { font-weight: 600; }
.sub-status.pending { color: #f39c12; }
.sub-status.approved { color: #27ae60; }
.sub-status.rejected { color: #e74c3c; }
.sub-time { color: #999; }
.review-actions { display: flex; gap: 8px; margin-top: 8px; }
.review-note { font-size: 13px; color: #666; margin-top: 4px; padding: 6px 8px; background: #f8f9fa; border-radius: 6px; }
.review-feedback { font-size: 14px; font-weight: 600; padding: 8px 12px; border-radius: 8px; margin: 8px 0; }
.review-feedback.success { background: #e8f8e8; color: #27ae60; }
.review-feedback.error { background: #fde8e8; color: #e74c3c; }
.reject-form { margin-top: 8px; display: flex; flex-direction: column; gap: 8px; }
.reject-form textarea { padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 13px; font-family: inherit; resize: vertical; }

/* Edit & Delete */
.action-btns { display: flex; gap: 6px; }
.btn.outline { background: white; border: 1px solid #667eea; color: #667eea; }
.btn.danger.small { background: #e74c3c; color: white; font-size: 12px; padding: 5px 10px; }
.modal-sm { max-width: 380px; }
.modal-sm p { font-size: 14px; color: #666; line-height: 1.6; margin: 0 0 16px; }
.edit-form { display: flex; flex-direction: column; gap: 8px; }
.edit-form label { font-size: 13px; font-weight: 600; color: #555; }
.edit-form input, .edit-form select, .edit-form textarea { padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; font-size: 14px; font-family: inherit; }
.msg.error { color: #e74c3c; }`n</style>




