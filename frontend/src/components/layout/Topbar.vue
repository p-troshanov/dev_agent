// frontend/src/components/layout/Topbar.vue
<template>
  <header class="topbar">
    <div class="topbar-left">
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>
    <div class="topbar-right">
      <button @click="appStore.openIde('', '')" class="action-btn outline" title="Облако (Файловый менеджер)">☁️ Облако</button>
      <div class="status-badge" :class="{ 'connected': appStore.isConnected }" :title="appStore.isConnected ? 'Ядро подключено' : 'Ожидание ядра...'">
        <span class="pulse-dot"></span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { appStore } from '../../stores/appStore'

const route = useRoute()

const pageTitle = computed(() => {
  if (route.path === '/settings') return 'Настройки системы'
  if (route.path === '/statistics' || route.path === '/statistics/aggregated') return 'Статистика LLM'
  if (route.path === '/agents') return 'Управление агентами'
  if (route.path === '/tools') return 'Реестр Инструментов'
  if (route.path === '/tasks' || route.path === '/') return 'Выполнение задач'
  if (route.path === '/projects') return 'Управление проектами'
  return 'Панель управления'
})
</script>
