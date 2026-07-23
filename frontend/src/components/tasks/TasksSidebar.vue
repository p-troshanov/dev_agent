// frontend/src/components/tasks/TasksSidebar.vue
<template>
  <div class="tasks-sidebar">
    <div class="tasks-sidebar-header">
      <h3 class="card-title">Активные задачи</h3>
      <button @click="$emit('create-task')" class="action-icon-btn primary-icon-btn" title="Создать задачу">+</button>
    </div>

    <div class="tasks-list custom-scrollbar">
      <div v-if="tasks.length === 0" class="empty-state-mini">
        Нет активных задач.
      </div>
      
      <div 
        v-for="task in tasks" 
        :key="task.id" 
        class="task-item"
        :class="{'active': activeTaskId === task.id}"
        @click="$emit('select-task', task.id)"
      >
        <div class="task-info">
          <span class="task-title">{{ task.title }}</span>
          <div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-end;">
            <span class="task-type">{{ task.project_name }}</span>
            <span v-if="task.type === 'step_by_step'" class="task-phase-badge">{{ formatPhase(task.current_phase) }}</span>
          </div>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: -2px; display: flex; align-items: center; gap: 4px;">
          <span>🤖 Исполнитель:</span> <span style="color: var(--accent-blue); font-weight: 500;">{{ task.agent_name || 'Не назначен' }}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="task-status" :class="task.status">
            {{ formatStatus(task.status) }}
          </div>
          <div v-if="task.total_cost !== undefined" style="font-size: 11px; color: var(--warning); font-family: 'Consolas', monospace; font-weight: 600;" title="Расход на задачу">
            ${{ task.total_cost.toFixed(6) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  tasks: { type: Array, required: true },
  activeTaskId: { type: Number, default: null }
});

defineEmits(['select-task', 'create-task']);

const formatStatus = (status) => {
  const map = {
    'pending': '⏳ В очереди',
    'running': '⚙️ В работе',
    'waiting_user': '✋ Ждет вас',
    'completed': '✅ Готово',
    'failed': '❌ Остановлена / Ошибка'
  }
  return map[status] || status
}

const formatPhase = (phase) => {
  const map = {
    'discovery': '🔍 Анализ',
    'planning': '📝 План',
    'execution': '💻 Кодинг'
  }
  return map[phase] || phase;
}
</script>

<style scoped>
.tasks-sidebar { width: 320px; background: var(--bg-panel); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; }
.tasks-sidebar-header { padding: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); }
.card-title { margin: 0; font-size: 15px; color: var(--text-main); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.primary-icon-btn { background: var(--accent-blue); color: #fff; border: none; border-radius: 6px; width: 28px; height: 28px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.primary-icon-btn:hover { background: var(--accent-blue-hover); }

.tasks-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.task-item { background: var(--bg-surface); border: 1px solid var(--border-color); padding: 12px; border-radius: 8px; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; gap: 8px; }
.task-item:hover { border-color: var(--accent-blue); }
.task-item.active { border-color: var(--accent-purple); background: rgba(107, 76, 154, 0.1); }

.task-info { display: flex; justify-content: space-between; align-items: flex-start; }
.task-title { font-size: 14px; font-weight: 500; color: var(--text-main); word-wrap: break-word; flex: 1; }
.task-type { font-size: 11px; background: var(--bg-base); border: 1px solid var(--border-color); padding: 2px 6px; border-radius: 4px; color: var(--text-muted); margin-left: 8px; white-space: nowrap; }
.task-phase-badge { font-size: 10px; background: rgba(107, 76, 154, 0.2); color: #c4b5fd; padding: 2px 6px; border-radius: 4px; white-space: nowrap; border: 1px solid rgba(107, 76, 154, 0.4); }

.task-status { font-size: 12px; font-weight: 600; }
.task-status.pending { color: var(--warning); }
.task-status.running { color: var(--accent-blue); }
.task-status.waiting_user { color: var(--warning); }
.task-status.completed { color: var(--success); }
.task-status.failed { color: #ff4444; }

.empty-state-mini { text-align: center; color: var(--text-muted); font-size: 13px; font-style: italic; padding: 20px; }
</style>
