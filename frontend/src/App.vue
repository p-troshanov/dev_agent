// frontend/src/App.vue
<template>
  <div v-if="route.path !== '/auth'" class="dashboard-layout">
    
    <MainNav />

    <div class="main-wrapper">
      <Topbar />

      <main class="content-area">
        <router-view v-slot="{ Component, route }">
          <keep-alive>
            <component :is="Component" :key="route.name" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
  
  <router-view v-else></router-view>

  <IdeModal v-if="appStore.isIdeOpen" />
</template>

<script setup>
import { onMounted, markRaw } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { appStore } from './stores/appStore'

import MainNav from './components/layout/MainNav.vue'
import Topbar from './components/layout/Topbar.vue'
import IdeModal from './components/ide/IdeModal.vue'

const router = useRouter()
const route = useRoute()

onMounted(() => {
  appStore.router = markRaw(router)
  appStore.init()
})
</script>

<style scoped>
</style>
