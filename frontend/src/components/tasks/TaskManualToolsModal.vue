// frontend/src/components/tasks/TaskManualToolsModal.vue
<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3 class="modal-title">Ручной запуск инструментов</h3>

      <div class="tools-grid">
        <button @click="runAction('clear_folder')" class="action-btn outline" :disabled="isRunning">🗑 Очистить папку проекта</button>
        <button @click="runAction('github_pull')" class="action-btn outline" :disabled="isRunning">📥 Обновить из репозитория</button>
        <button @click="runAction('github_push')" class="action-btn outline" :disabled="isRunning">📤 Запушить в GitHub</button>
        <button @click="runAction('check_syntax')" class="action-btn outline" :disabled="isRunning">✓ Проверить синтаксис</button>
      </div>

      <div class="form-group mt-2">
        <label>Лог выполнения</label>
        <div class="log-output custom-scrollbar">
          <div v-if="isRunning" class="loading-text">Выполнение операции...</div>
          <pre v-else>{{ logText || 'Выберите инструмент для запуска. Убедитесь, что к задаче привязан проект.' }}</pre>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="action-btn">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { api } from '../../services/api'

const props = defineProps({
  show: Boolean,
  taskId: Number
});

const emit = defineEmits(['close']);
const isRunning = ref(false);
const logText = ref("");

watch(() => props.show, (newVal) => {
  if (newVal) {
    logText.value = "";
    isRunning.value = false;
  }
});

const runAction = async (action) => {
  if (!props.taskId) return;
  isRunning.value = true;
  logText.value = "";
  try {
    const res = await api.executeManualAction(props.taskId, action);
    logText.value = res.result || "Выполнено без вывода";
  } catch (e) {
    logText.value = `Ошибка API: ${e.message}`;
  } finally {
    isRunning.value = false;
  }
};
</script>

<style scoped>
.modal-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-content { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 100%; max-width: 650px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); }
.modal-title { margin: 0 0 16px 0; font-size: 16px; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.mt-2 { margin-top: 16px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: 0.2s; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.outline { border-color: var(--accent-blue); color: var(--accent-blue); }
.action-btn.outline:hover:not(:disabled) { background: rgba(64, 104, 148, 0.1); }
.tools-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.log-output { background: #0d0d12; border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; height: 300px; overflow-y: auto; }
.log-output pre { margin: 0; font-family: 'Consolas', monospace; font-size: 13px; color: #a3b8cc; white-space: pre-wrap; word-wrap: break-word; }
.loading-text { color: var(--accent-blue); font-size: 13px; font-weight: bold; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
</style>
