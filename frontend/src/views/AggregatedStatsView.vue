// frontend/src/views/AggregatedStatsView.vue
<template>
  <div class="statistics-page custom-scrollbar">
    <div class="statistics-wrapper">
      <div class="header-actions">
        <div style="display: flex; align-items: center; gap: 12px;">
          <router-link to="/statistics" class="action-btn outline">⬅ Назад</router-link>
          <h3 class="card-title">Сводная статистика</h3>
        </div>
        <button @click="fetchAggregatedStats" class="action-btn primary">🔄 Обновить</button>
      </div>

      <div class="controls-panel">
        <div class="form-group">
          <label>Период</label>
          <select v-model="period" @change="fetchAggregatedStats" class="modern-input select-input">
            <option value="day">По дням</option>
            <option value="week">По неделям</option>
            <option value="month">По месяцам</option>
          </select>
        </div>
        <div class="form-group">
          <label>Группировка</label>
          <select v-model="groupBy" @change="fetchAggregatedStats" class="modern-input select-input">
            <option value="provider">По провайдеру</option>
            <option value="agent_name">По агенту</option>
            <option value="key_id">По ключу (ID)</option>
          </select>
        </div>
      </div>

      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>Период (Дата)</th>
              <th>Группа ({{ groupByLabel }})</th>
              <th class="text-right">Запросы</th>
              <th class="text-right">Токены</th>
              <th class="text-right">Затраты</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="stats.length === 0">
              <td colspan="5" class="empty-state">Нет данных для отображения.</td>
            </tr>
            <tr v-for="(row, idx) in stats" :key="idx">
              <td class="col-date">{{ row.period_date }}</td>
              <td class="col-group">
                <span v-if="groupBy === 'provider'" class="provider-badge" :class="row.group.toLowerCase()">{{ row.group }}</span>
                <span v-else-if="groupBy === 'agent_name'" style="color: var(--accent-purple); font-weight: 500;">{{ row.group }}</span>
                <span v-else class="mono">{{ row.group === 'None' ? '.env (Базовый)' : 'ID: ' + row.group }}</span>
              </td>
              <td class="text-right">{{ row.total_requests }}</td>
              <td class="col-tokens text-right">{{ row.total_tokens }}</td>
              <td class="col-cost text-right">${{ row.total_cost != null ? row.total_cost.toFixed(4) : '0.0000' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../services/api'

const stats = ref([])
const period = ref('day')
const groupBy = ref('provider')

const groupByLabel = computed(() => {
  if (groupBy.value === 'provider') return 'Провайдер'
  if (groupBy.value === 'agent_name') return 'Агент'
  if (groupBy.value === 'key_id') return 'Ключ'
  return 'Группа'
})

const fetchAggregatedStats = async () => {
  try {
    stats.value = await api.getAggregatedStatistics(period.value, groupBy.value)
  } catch (e) {
    console.error("Не удалось загрузить сводную статистику:", e)
  }
}

onMounted(() => {
  fetchAggregatedStats()
})
</script>

<style scoped>
.statistics-page { height: 100%; padding: 24px 24px 100px; overflow-y: auto; }
.statistics-wrapper { max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 10px; padding: 24px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.header-actions { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.card-title { margin: 0; font-size: 16px; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.8px; }

.controls-panel { display: flex; gap: 16px; background: var(--bg-base); padding: 16px; border-radius: 8px; border: 1px dashed var(--border-color); }
.form-group { display: flex; flex-direction: column; gap: 8px; flex: 1; max-width: 300px; }
label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.modern-input { background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; outline: none; }
.modern-input:focus { border-color: var(--accent-blue); }
.select-input { cursor: pointer; height: 42px; }

.table-container { overflow-x: auto; }
.modern-table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; }
.modern-table th { padding: 12px 16px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; border-bottom: 1px solid var(--border-color); }
.modern-table td { padding: 14px 16px; border-bottom: 1px solid var(--border-color); color: var(--text-main); }
.modern-table tbody tr:hover td { background: var(--bg-surface-hover); }

.col-date { width: 200px; font-weight: 500; }
.col-group { width: auto; }
.col-tokens { font-weight: 600; color: var(--accent-blue); }
.col-cost { font-weight: 600; color: var(--warning); font-family: 'Consolas', monospace; font-size: 13px; }
.text-right { text-align: right; }
.mono { font-family: 'Consolas', 'Monaco', monospace; }

.provider-badge { font-size: 11px; text-transform: uppercase; font-weight: bold; padding: 4px 8px; border-radius: 4px; letter-spacing: 0.5px; }
.provider-badge.groq { background: rgba(245, 80, 54, 0.15); color: #f55036; }
.provider-badge.gemini { background: rgba(66, 133, 244, 0.15); color: #4285f4; }
.provider-badge.openrouter { background: rgba(147, 51, 234, 0.15); color: #c084fc; }

.empty-state { text-align: center; padding: 40px !important; color: var(--text-muted) !important; font-style: italic; }
</style>
