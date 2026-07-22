// frontend/src/components/layout/MainNav.vue
<template>
  <nav class="main-nav">
    <div class="nav-logo" title="RITA Core">RITA</div>
    <div class="nav-items">
      <router-link to="/tasks" class="nav-item" :class="{'router-link-active': route.path === '/' || route.path.startsWith('/tasks')}" title="Задачи"><span class="nav-icon">📋</span></router-link>
      <router-link to="/projects" class="nav-item" title="Проекты"><span class="nav-icon">📁</span></router-link>
      <router-link to="/agents" class="nav-item" title="Агенты"><span class="nav-icon">🤖</span></router-link>
      <router-link to="/tools" class="nav-item" title="Инструменты"><span class="nav-icon">🔧</span></router-link>
      <router-link to="/statistics" class="nav-item" title="Статистика"><span class="nav-icon">📊</span></router-link>
      <router-link to="/settings" class="nav-item" title="Настройки"><span class="nav-icon">⚙️</span></router-link>
    </div>
    <button @click="logout" class="nav-item logout-btn" title="Выход"><span class="nav-icon">🚪</span></button>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { appStore } from '../../stores/appStore'

const route = useRoute()

const logout = () => {
  appStore.logout()
}
</script>
