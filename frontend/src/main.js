// frontend/src/main.js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import SettingsView from './views/SettingsView.vue'
import StatisticsView from './views/StatisticsView.vue'
import AggregatedStatsView from './views/AggregatedStatsView.vue'
import AgentsView from './views/AgentsView.vue'
import ToolsView from './views/ToolsView.vue'
import TasksView from './views/TasksView.vue'
import ProjectsView from './views/ProjectsView.vue'
import AuthView from './views/AuthView.vue'

import './assets/main.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: TasksView, meta: { requiresAuth: true } },
    { path: '/settings', name: 'Settings', component: SettingsView, meta: { requiresAuth: true } },
    { path: '/statistics', name: 'Statistics', component: StatisticsView, meta: { requiresAuth: true } },
    { path: '/statistics/aggregated', name: 'AggregatedStats', component: AggregatedStatsView, meta: { requiresAuth: true } },
    { path: '/agents', name: 'Agents', component: AgentsView, meta: { requiresAuth: true } },
    { path: '/tools', name: 'Tools', component: ToolsView, meta: { requiresAuth: true } },
    { path: '/projects', name: 'Projects', component: ProjectsView, meta: { requiresAuth: true } },
    { path: '/tasks', name: 'Tasks', component: TasksView, meta: { requiresAuth: true } },
    { path: '/auth', name: 'Auth', component: AuthView }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('rita_token');
  if (to.meta.requiresAuth && !token) {
    next('/auth');
  } else if (to.path === '/auth' && token) {
    next('/');
  } else {
    next();
  }
})

createApp(App).use(router).mount('#app')
