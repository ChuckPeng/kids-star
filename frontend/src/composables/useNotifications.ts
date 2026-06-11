import { ref, onMounted } from 'vue'
import api from '@/api/client'

export function useNotifications() {
  const unreadCount = ref(0)
  const notifications = ref<any[]>([])

  async function fetchUnread() {
    try {
      const { data } = await api.get('/notifications/unread-count')
      unreadCount.value = data.count
    } catch {}
  }

  async function fetchAll() {
    try {
      const { data } = await api.get('/notifications?limit=30')
      notifications.value = data
    } catch {}
  }

  async function markRead(id: string) {
    try {
      await api.post(`/notifications/${id}/read`)
      const n = notifications.value.find(x => x.id === id)
      if (n) n.is_read = true
      await fetchUnread()
    } catch {}
  }

  async function markAllRead() {
    try {
      await api.post('/notifications/read-all')
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    } catch {}
  }

  onMounted(() => { fetchUnread() })

  return { unreadCount, notifications, fetchUnread, fetchAll, markRead, markAllRead }
}
