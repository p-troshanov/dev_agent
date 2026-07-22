// frontend/src/views/StatisticsView.vue
<template>
  <div class="statistics-page custom-scrollbar">
    <div class="statistics-wrapper">
      <div class="header-actions">
        <h3 class="card-title">Статистика вызовов LLM</h3>
        <div style="display: flex; gap: 8px;">
          <router-link to="/statistics/aggregated" class="action-btn outline">📈 Сводная статистика</router-link>
          <button @click="fetchStats" class="action-btn primary">🔄 Обновить</button>
        </div>
      </div>

      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Дата и Время</th>
              <th>Агент</th>
              <th>Провайдер</th>
              <th>Ключ (ID)</th>
              <th>Модель</th>
              <th class="text-right">Токены</th>
              <th class="text-right">Стоимость</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="stats.length === 0">
              <td colspan="8" class="empty-state">Нет данных о запросах.</td>
            </tr>
            <tr v-for="row in stats" :key="row.id">
              <td class="col-id">#{{ row.id }}</td>
              <td class="col-date">{{ formatDate(row.created_at) }}</td>
              <td class="col-agent" style="color: var(--accent-purple); font-weight: 500;">{{ row.agent_name || '-' }}</td>
              <td class="col-provider">
                <span class="provider-badge" :class="row.provider">{{ row.provider }}</span>
              </td>
              <td class="col-key">{{ row.key_id ? `ID: ${row.key_id}` : '.env (Базовый)' }}</td>
              <td class="col-model mono">{{ row.model }}</td>
              <td class="col-tokens text-right">{{ row.tokens || 0 }}</td>
              <td class="col-cost text-right">${{ row.cost != null ? row.cost.toFixed(6) : '0.000000' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'

const stats = ref([])

const fetchStats = async () => {
  try {
    stats.value = await api.getStatistics()
  } catch (e) {
    console.error("Не удалось загрузить статистику:", e)
  }
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleString('ru-RU', { 
    day: '2-digit', month: '2-digit', year: 'numeric', 
    hour: '2-digit', minute: '2-digit', second: '2-digit' 
  })
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.statistics-page { height: 100%; padding: 24px 24px 100px; overflow-y: auto; }
.statistics-wrapper { max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 10px; padding: 24px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.header-actions { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.card-title { margin: 0; font-size: 16px; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.8px; }

.table-container { overflow-x: auto; }
.modern-table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; }
.modern-table th { padding: 12px 16px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; border-bottom: 1px solid var(--border-color); }
.modern-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); color: var(--text-main); }
.modern-table tbody tr:hover td { background: var(--bg-surface-hover); }

.col-id { color: var(--text-muted); font-size: 13px; width: 60px; }
.col-date { width: 180px; }
.col-agent { width: 120px; }
.col-provider { width: 120px; }
.col-key { font-size: 13px; color: var(--text-muted); }
.col-model { font-size: 13px; color: var(--accent-blue); }
.col-tokens { font-weight: 600; }
.col-cost { font-weight: 600; color: var(--warning); font-family: 'Consolas', monospace; font-size: 13px; }
.text-right { text-align: right; }
.mono { font-family: 'Consolas', 'Monaco', monospace; }

.provider-badge { font-size: 11px; text-transform: uppercase; font-weight: bold; padding: 4px 8px; border-radius: 4px; letter-spacing: 0.5px; }
.provider-badge.groq { background: rgba(245, 80, 54, 0.15); color: #f55036; }
.provider-badge.gemini { background: rgba(66, 133, 244, 0.15); color: #4285f4; }
.provider-badge.openrouter { background: rgba(147, 51, 234, 0.15); color: #c084fc; }

.empty-state { text-align: center; padding: 40px !important; color: var(--text-muted) !important; font-style: italic; }
</style>
