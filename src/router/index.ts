import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ApiDocs from '@/views/ApiDocs.vue'
import PrivacyPolicy from '@/views/PrivacyPolicy.vue'
import UserCenter from '@/views/UserCenter.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/docs',
      name: 'docs',
      component: ApiDocs
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: PrivacyPolicy
    },
    {
      path: '/user-center',
      name: 'user-center',
      component: UserCenter
    }
  ]
})

export default router
