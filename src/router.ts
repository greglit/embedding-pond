import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

const normalizeLang = (value: unknown): 'en' | 'de' => (value === 'de' ? 'de' : 'en')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: (to) => ({
        name: 'home',
        params: { lang: 'en' },
        query: to.query,
        hash: to.hash,
      }),
    },
    {
      path: '/:lang(en|de)',
      name: 'home',
      component: App,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: (to) => ({
        name: 'home',
        params: { lang: normalizeLang(to.params.lang) },
        query: to.query,
        hash: to.hash,
      }),
    },
  ],
})

router.beforeEach((to) => {
  if (to.name !== 'home') return true
  const normalized = normalizeLang(to.params.lang)
  if (to.params.lang === normalized) return true
  return {
    name: 'home',
    params: { lang: normalized },
    query: to.query,
    hash: to.hash,
    replace: true,
  }
})

export default router
