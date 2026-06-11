<template>
  <div class="dashboard">
    <header class="header">
      <h1>{{ family?.name || 'Kids-Star' }}</h1>
      <div class="header-actions">
        <button class="btn-sm bell-btn" @click="showNotifs = !showNotifs; fetchNotifs()">🔔<span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span></button><button class="btn-sm" @click="auth.logout()">退出</button>
      </div>
    </header>

    <!-- Notification dropdown -->
    <div v-if="showNotifs" class="notif-dropdown">
      <div class="notif-header">
        <strong>通知</strong>
        <button class="btn-sm-outline" @click="markAllNotifsRead">全部已读</button>
      </div>
      <div v-for="n in notificationList" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }" @click="markNotifRead(n.id)">
        <strong>{{ n.title }}</strong>
        <p v-if="n.body">{{ n.body }}</p>
        <span class="notif-time">{{ formatTime(n.created_at) }}</span>
      </div>
      <p v-if="notificationList.length === 0" class="empty">暂无通知</p>
    </div>

    <!-- Invite code -->
    <section class="section">
      <div class="invite-box">
        <span>邀请码: <strong>{{ family?.invite_code }}</strong></span>
        <span class="hint">孩子用此码登录</span>
      </div>
    </section>

    <!-- Tab Bar -->
    <section class="section">
      <div class="tab-bar">
        <button :class="{ active: tab === 'tasks' }" @click="tab = 'tasks'">📋 任务</button>
        <button :class="{ active: tab === 'rewards' }" @click="tab = 'rewards'; fetchRewards()">🎁 奖励</button>
        <button :class="{ active: tab === 'review' }" @click="tab = 'review'; fetchAllReviews()">✅ 审核</button>
        <button :class="{ active: tab === 'stats' }" @click="tab = 'stats'; fetchStats()">📊 统计</button>
      </div>
    </section>

    <template v-if="tab === 'tasks'">

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
          <select v-model="form.repeat_type">
            <option value="once">一次性</option>
            <option value="daily">每日</option>
            <option value="weekly">每周</option>
            <option value="monthly">每月</option>
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
          <span v-if="t.repeat_type && t.repeat_type !== 'once'" class="repeat-badge">{{ t.repeat_type === 'daily' ? '每日' : t.repeat_type === 'weekly' ? '每周' : '每月' }}</span>
          <span v-if="t.repeat_type && t.repeat_type !== 'once'" class="repeat-badge">{{ t.repeat_type === 'daily' ? '每日' : t.repeat_type === 'weekly' ? '每周' : '每月' }}</span>
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
          <span v-if="t.repeat_type && t.repeat_type !== 'once'" class="repeat-badge">{{ t.repeat_type === 'daily' ? '每日' : t.repeat_type === 'weekly' ? '每周' : '每月' }}</span>
          <span v-if="t.repeat_type && t.repeat_type !== 'once'" class="repeat-badge">{{ t.repeat_type === 'daily' ? '每日' : t.repeat_type === 'weekly' ? '每周' : '每月' }}</span>
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

    </template>

    <!-- ========== Rewards Tab ========== -->
    <template v-if="tab === 'rewards'">
    <section class="section">
      <div class="section-header">
        <h3>奖励商品管理</h3>
        <button class="btn primary small" @click="showRewardForm = !showRewardForm">
          {{ showRewardForm ? '取消' : '+ 添加商品' }}
        </button>
      </div>
      <div v-if="showRewardForm" class="create-form">
        <input v-model="rewardForm.name" placeholder="商品名称（如：30分钟游戏时间）" />
        <textarea v-model="rewardForm.description" placeholder="描述（可选）" rows="2"></textarea>
        <div class="form-row">
          <input v-model.number="rewardForm.points_cost" type="number" placeholder="所需星星" min="1" />
          <input v-model.number="rewardForm.stock" type="number" placeholder="库存(-1无限)" min="-1" />
        </div>
        <button class="btn primary" @click="doCreateReward" :disabled="!rewardForm.name">创建</button>
      </div>
      <div v-for="r in rewardList" :key="r.id" class="task-card">
        <div class="task-header">
          <strong>{{ r.name }}</strong>
          <span class="task-points">⭐{{ r.points_cost }}</span>
        </div>
        <p v-if="r.description" class="task-desc">{{ r.description }}</p>
        <div class="task-actions">
          <span class="task-status">库存: {{ r.stock === -1 ? '无限' : r.stock }}</span>
          <div class="action-btns">
            <button class="btn secondary small" @click="editReward(r)">编辑</button>
            <button class="btn danger small" @click="delReward(r.id)">下架</button>
          </div>
        </div>
      </div>
      <p v-if="rewardList.length === 0" class="empty">还没有商品，添加一些奖励吧</p>
    </section>
    </template>

    <!-- ========== Review Tab ========== -->
    <template v-if="tab === 'review'">
    <section class="section">
      <div class="section-header"><h3>兑换审核</h3></div>
      <div v-for="rd in redemptionList" :key="rd.id" class="task-card">
        <div class="task-header">
          <strong>{{ rd.child_name }} 兑换 {{ rd.reward_name }}</strong>
          <span class="task-points">⭐{{ rd.points_spent }}</span>
        </div>
        <span class="sub-status" :class="rd.status">{{ rd.status === 'pending' ? '待审核' : rd.status === 'approved' ? '已通过' : '已拒绝' }}</span>
        <div v-if="rd.status === 'pending'" class="review-actions">
          <button class="btn success small" @click="approveRedemption(rd.id)">通过</button>
          <button class="btn danger small" @click="rejectRedemption(rd.id)">拒绝</button>
        </div>
      </div>
      <p v-if="redemptionList.length === 0" class="empty">暂无兑换申请</p>
    </section>

    <section class="section">
      <div class="section-header"><h3>申请审核</h3></div>
      <div v-for="a in appList" :key="a.id" class="task-card">
        <div class="task-header">
          <span class="task-badge" :class="a.type === 'reward' ? 'challenge' : 'required'">
            {{ a.type === 'reward' ? '奖励' : '提议' }}
          </span>
          <strong>{{ a.child_name }}: {{ a.title }}</strong>
          <span class="task-points">⭐{{ a.points_requested }}</span>
        </div>
        <p v-if="a.description" class="task-desc">{{ a.description }}</p>
        <span class="sub-status" :class="a.status">{{ a.status === 'pending' ? '待审核' : a.status === 'approved' ? '已通过' : '已拒绝' }}</span>
        <div v-if="a.status === 'pending'" class="review-actions">
          <input v-model="appPoints[a.id]" type="number" :placeholder="'星星('+a.points_requested+')'" min="1" class="pts-input" />
          <button class="btn success small" @click="approveApp(a)">通过</button>
          <button class="btn danger small" @click="rejectApp(a)">拒绝</button>
        </div>
      </div>
      <p v-if="appList.length === 0" class="empty">暂无申请</p>
    </section>
    </template>

    <!-- ========== Stats Tab ========== -->
    <template v-if="tab === 'stats'">
    <section class="section">
      <div class="section-header"><h3>家庭统计</h3></div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-num">{{ statsData.total_tasks_created }}</div><div class="stat-label">总任务数</div></div>
        <div class="stat-card"><div class="stat-num">{{ statsData.active_required }}</div><div class="stat-label">活跃必修</div></div>
        <div class="stat-card"><div class="stat-num">{{ statsData.active_challenges }}</div><div class="stat-label">活跃挑战</div></div>
      </div>
    </section>

    <section class="section">
      <div class="section-header"><h3>孩子表现</h3></div>
      <div v-for="c in statsData.children" :key="c.child_id" class="task-card">
        <div class="task-header">
          <strong>{{ c.child_name }}</strong>
          <span class="task-points">⭐ {{ c.total_points }}</span>
        </div>
        <div class="stats-row">
          <span>必修完成率: <b>{{ c.required_completion_rate }}%</b></span>
          <span>已完成: <b class="green">{{ c.approved_count }}</b></span>
          <span>已拒绝: <b class="red">{{ c.rejected_count }}</b></span>
          <span>挑战参与: <b>{{ c.challenge_count }}</b></span>
        </div>
      </div>
    </section>

    <!-- Manual Penalty -->
    <section class="section">
      <div class="section-header"><h3>手动扣星</h3></div>
      <div class="create-form">
        <select v-model="penalty.child_id">
          <option value="">选择孩子</option>
          <option v-for="c in children" :key="c.id" :value="c.id">{{ c.nickname || c.name }}</option>
        </select>
        <div class="form-row">
          <input v-model.number="penalty.amount" type="number" placeholder="扣除星星数" min="1" />
        </div>
        <input v-model="penalty.reason" placeholder="扣星原因" />
        <button class="btn danger" @click="doPenalty" :disabled="!penalty.child_id || !penalty.amount">确认扣星</button>
        <p v-if="penaltyMsg" :class="penaltyMsgType">{{ penaltyMsg }}</p>
      </div>
    </section>
    </template>

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
import { useNotifications } from '@/composables/useNotifications'

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
const tab = ref('tasks')
const showRewardForm = ref(false)
const rewardForm = ref({ name: '', description: '', points_cost: 10, stock: -1 })
const rewardList = ref<any[]>([])
const redemptionList = ref<any[]>([])
const appList = ref<any[]>([])
const appPoints = ref<Record<string, number>>({})
const statsData = ref<any>({ children: [], total_tasks_created: 0, active_required: 0, active_challenges: 0 })
const penalty = ref({ child_id: '', amount: 5, reason: '' })
const penaltyMsg = ref('')
const penaltyMsgType = ref('success')
const showTemplates = ref(false)
const templateList = ref<any[]>([])
const { unreadCount, notifications: notificationList, fetchAll: fetchNotifs, markRead: markNotifRead, markAllRead: markAllNotifsRead, fetchUnread } = useNotifications()
const showNotifs = ref(false)

const childForm = ref({ nickname: '' })
const form = ref({ title: '', description: '', difficulty: 'required', base_points: 5, assigned_to: [] as string[], task_type: 'custom', repeat_type: 'once' })

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
  form.value = { title: '', description: '', difficulty: 'required', base_points: 5, assigned_to: [], task_type: 'custom', repeat_type: 'once' }
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

// ── Tab data fetchers ──
async function fetchRewards() {
  try { const resp = await api.get("/rewards"); rewardList.value = resp.data } catch {}
}
async function fetchAllReviews() {
  try {
    const rdResp = await api.get("/rewards/redemptions")
    const appResp = await api.get("/applications")
    redemptionList.value = rdResp.data; appList.value = appResp.data
  } catch {}
}
async function fetchStats() {
  try { const resp = await api.get("/stats/family"); statsData.value = resp.data } catch {}
}

// ── Reward CRUD ──
async function doCreateReward() {
  try {
    await api.post("/rewards", rewardForm.value)
    rewardForm.value = { name: "", description: "", points_cost: 10, stock: -1 }
    showRewardForm.value = false
    await fetchRewards()
  } catch {}
}
async function delReward(id: string) {
  try { await api.delete("/rewards/" + id); await fetchRewards() } catch {}
}

// ── Redemption review ──
async function approveRedemption(id: string) {
  try { await api.post("/rewards/redemptions/" + id + "/review", { status_req: "approved" }); await fetchAllReviews() } catch {}
}
async function rejectRedemption(id: string) {
  try { await api.post("/rewards/redemptions/" + id + "/review", { status_req: "rejected" }); await fetchAllReviews() } catch {}
}

// ── Application review ──
async function approveApp(a: any) {
  try {
    await api.post("/applications/" + a.id + "/review", { status: "approved", points_approved: appPoints.value[a.id] || a.points_requested })
    await fetchAllReviews()
  } catch {}
}
async function rejectApp(a: any) {
  try { await api.post("/applications/" + a.id + "/review", { status: "rejected" }); await fetchAllReviews() } catch {}
}

// ── Manual penalty ──
async function doPenalty() {
  penaltyMsg.value = ""
  try {
    await api.post("/stats/penalty", penalty.value)
    penaltyMsg.value = "扣星成功"; penaltyMsgType.value = "success"
    penalty.value = { child_id: "", amount: 5, reason: "" }
    await familyStore.fetchMyFamily()
    if (tab.value === "stats") await fetchStats()
  } catch (e: any) {
    penaltyMsg.value = e.response?.data?.detail || "操作失败"; penaltyMsgType.value = "error"
  }
}

// ── Templates ──
async function fetchTemplates() {
  try { const resp = await api.get("/templates"); templateList.value = resp.data } catch {}
}
function useTemplate(t: any) {
  form.value.title = t.title
  form.value.description = t.description || ""
  form.value.difficulty = t.difficulty
  form.value.base_points = t.base_points
  form.value.task_type = t.task_type
  form.value.repeat_type = t.repeat_type
  showTemplates.value = false
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
.msg.error { color: #e74c3c; }`n
/* Tabs */
.tab-bar { display: flex; gap: 6px; flex-wrap: wrap; }
.tab-bar button { flex: 1; min-width: 60px; padding: 8px 6px; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; background: white; color: #888; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.tab-bar button.active { background: #667eea; color: white; }

/* Stats */
.stats-grid { display: flex; gap: 10px; }
.stat-card { flex: 1; background: white; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-num { font-size: 28px; font-weight: 700; color: #667eea; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }
.stats-row { display: flex; flex-wrap: wrap; gap: 10px; font-size: 13px; color: #666; margin-top: 8px; }
.stats-row .green { color: #27ae60; }
.stats-row .red { color: #e74c3c; }

/* Penalty */
.pts-input { width: 70px; padding: 6px 8px; border: 1px solid #d9d9d9; border-radius: 6px; font-size: 13px; }`n/* Notification */
.bell-btn { position: relative; }
.badge { position: absolute; top: -4px; right: -6px; background: #e74c3c; color: white; font-size: 10px; padding: 1px 5px; border-radius: 10px; min-width: 16px; text-align: center; }
.notif-dropdown { position: fixed; top: 56px; right: 8px; left: 8px; max-width: 400px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 200; max-height: 60vh; overflow-y: auto; }
.notif-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid #eee; }
.notif-header strong { font-size: 16px; }
.notif-item { padding: 12px 16px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.notif-item.unread { background: #f0f4ff; }
.notif-item strong { font-size: 14px; display: block; }
.notif-item p { color: #666; font-size: 12px; margin: 4px 0; }
.notif-time { font-size: 11px; color: #999; }

.repeat-badge { font-size: 11px; background: #e8f8e8; color: #27ae60; padding: 2px 6px; border-radius: 4px; margin-left: 6px; }

</style>











