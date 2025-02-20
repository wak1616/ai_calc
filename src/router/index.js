import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'

// Define routes array separately for better maintainability
const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
  },
  {
    path: '/about',
    name: 'about',
    component: About,
    meta: {
      title: 'About'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Update document title on route change (using Vue's navigation guard)
router.beforeEach((to, from, next) => {
  document.title = `De Rojas AI Calc: ${to.meta.title}`
  next()
})

export default router