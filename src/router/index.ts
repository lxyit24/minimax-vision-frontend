import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import PrivacyPolicy from '@/views/PrivacyPolicy.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: PrivacyPolicy
    }
  ]
})

export default router
