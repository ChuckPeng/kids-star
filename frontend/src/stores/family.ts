import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useFamilyStore = defineStore('family', () => {
  const family = ref<any>(null)
  const tasks = ref<any[]>([])
  const submissions = ref<any[]>([])

  async function fetchMyFamily() {
    const { data } = await api.get('/families/me')
    family.value = data
  }

  async function createFamily(name: string) {
    const { data } = await api.post('/families', { name })
    family.value = data
  }

  async function joinFamily(inviteCode: string) {
    const { data } = await api.post('/families/join', { invite_code: inviteCode })
    family.value = data
  }

  async function fetchTasks(filters?: any) {
    const { data } = await api.get('/tasks', { params: filters })
    tasks.value = data
  }

  async function createTask(taskData: any) {
    const { data } = await api.post('/tasks', taskData)
    return data
  }

  async function submitTask(taskId: string, note?: string) {
    const { data } = await api.post(`/tasks/${taskId}/submit`, { child_note: note })
    return data
  }

  async function reviewTask(taskId: string, status: string, note?: string) {
    const { data } = await api.post(`/tasks/${taskId}/review`, { status, parent_note: note })
    return data
  }

  async function fetchSubmissions(taskId: string) {
    const { data } = await api.get(`/tasks/${taskId}/submissions`)
    submissions.value = data
    return data
  }

  return { family, tasks, submissions, fetchMyFamily, createFamily, joinFamily, fetchTasks, createTask, submitTask, reviewTask, fetchSubmissions }
})
