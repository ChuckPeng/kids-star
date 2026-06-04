import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/Login.vue'),
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/auth/Register.vue'),
    },
    {
      path: '/child-login',
      name: 'ChildLogin',
      component: () => import('@/views/auth/ChildLogin.vue'),
    },
    {
      path: '/setup',
      name: 'Setup',
      component: () => import('@/views/Setup.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/parent',
      name: 'ParentDashboard',
      component: () => import('@/views/parent/Dashboard.vue'),
      meta: { requiresAuth: true, role: 'parent' },
    },
    {
      path: '/child',
      name: 'ChildMyTasks',
      component: () => import('@/views/child/MyTasks.vue'),
      meta: { requiresAuth: true, role: 'child' },
    },
    {
      path: '/challenge-board',
      name: 'ChallengeBoard',
      component: () => import('@/views/child/ChallengeBoard.vue'),
      meta: { requiresAuth: true, role: 'child' },
    },
    {
      path: '/my-challenges',
      redirect: '/child',
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (token) {
    const { useAuthStore } = await import('@/stores/auth')
    const auth = useAuthStore()
    if (!auth.user) {
      try {
        await auth.fetchMe()
      } catch {
        return next('/login')
      }
    }

    if (to.meta.role && auth.user?.role !== to.meta.role && auth.user?.role !== 'admin') {
      if (auth.user?.role === 'parent') return next('/parent')
      if (auth.user?.role === 'child') return next('/child')
    }

    if (!to.path.startsWith('/setup') && !to.path.startsWith('/login') && !to.path.startsWith('/register') && !to.path.startsWith('/child-login')) {
      const { useFamilyStore } = await import('@/stores/family')
      const f = useFamilyStore()
      if (!f.family) {
        try { await f.fetchMyFamily() } catch {}
      }
      if (!f.family) {
        return next('/setup')
      }
    }
  }

  next()
})

export default router

