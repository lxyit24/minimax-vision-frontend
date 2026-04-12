import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ApiDocs from '@/views/ApiDocs.vue'

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
    }
  ]
})

export default router
