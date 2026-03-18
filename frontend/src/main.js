import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import './assets/global.css'

const routes = [
  { path: '/', redirect: '/backtest' },
  { path: '/backtest', component: () => import('./views/Backtest.vue') },
  { path: '/realtime', component: () => import('./views/Realtime.vue') },
  { path: '/portfolio', component: () => import('./views/Portfolio.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
