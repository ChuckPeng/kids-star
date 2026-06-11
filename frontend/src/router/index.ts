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
    {
      path: '/shop',
      name: 'Shop',
      component: () => import('@/views/child/Shop.vue'),
      meta: { requiresAuth: true, role: 'child' },
    },
    {
      path: '/requests',
      name: 'Requests',
      component: () => import('@/views/child/Requests.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.meta.role) {
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        if (to.meta.role === 'parent' && user.role !== 'parent' && user.role !== 'admin') {
          return next('/child')
        }
        if (to.meta.role === 'child' && user.role !== 'child') {
          return next('/parent')
        }
      }
    } catch {}
  }

  next()
})

export default router
