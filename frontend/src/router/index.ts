import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
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
      path: '/parent/dashboard',
      name: 'ParentDashboard',
      component: () => import('@/views/parent/Dashboard.vue'),
      meta: { requiresAuth: true, role: 'parent' },
    },
    {
      path: '/child/my-tasks',
      name: 'ChildMyTasks',
      component: () => import('@/views/child/MyTasks.vue'),
      meta: { requiresAuth: true, role: 'child' },
    },
  ],
})

export default router
