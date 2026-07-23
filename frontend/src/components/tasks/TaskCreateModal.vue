// frontend/src/components/tasks/TaskCreateModal.vue
<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3 class="modal-title">Постановка новой задачи</h3>
      
      <div class="form-group">
        <label>Короткое название</label>
        <input type="text" v-model="form.title" class="modern-input" placeholder="Например: Спарсить HH.ru" />
      </div>
      
      <div class="form-row mt-2" style="display: flex; gap: 16px;">
        <div class="form-group" style="flex: 1; min-width: 0;">
          <label>Проект</label>
          <select v-model="form.project_id" class="modern-input select-input">
            <option :value="null">Без проекта</option>
            <option v-for="proj in projects" :key="proj.id" :value="proj.id">{{ proj.name }}</option>
          </select>
        </div>
        <div class="form-group" style="flex: 1; min-width: 0;">
          <label>Назначить агента</label>
          <select v-model="form.agent_id" class="modern-input select-input">
            <option v-for="agent in agents" :key="agent.id" :value="agent.id">
              🤖 {{ agent.name }} {{ agent.profession ? '— ' + agent.profession : '' }} ({{ agent.model || 'Auto' }})
            </option>
          </select>
        </div>
      </div>

      <div class="form-group mt-2">
        <label>Режим выполнения</label>
        <div style="display: flex; gap: 16px; margin-top: 4px;">
          <label class="radio-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: var(--text-main); font-size: 13px;">
            <input type="radio" v-model="form.type" value="standard" style="accent-color: var(--accent-blue);" /> Свободный агент
          </label>
          <label class="radio-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: var(--text-main); font-size: 13px;">
            <input type="radio" v-model="form.type" value="step_by_step" style="accent-color: var(--accent-blue);" /> Пошаговый (Анализ -> План -> Код)
          </label>
        </div>
      </div>

      <div class="form-group mt-2" v-if="form.type === 'step_by_step'">
        <label>Конечная цель задачи</label>
        <select v-model="form.target_action" class="modern-input select-input">
          <option value="plan_only">Только составить план (без внесения изменений)</option>
          <option value="full_execution">Полная реализация (написать код по плану)</option>
        </select>
      </div>

      <div class="form-group mt-2" v-if="form.type === 'standard'">
        <label class="checkbox-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: var(--text-main); font-size: 13px; font-weight: 500; text-transform: none;">
          <input type="checkbox" v-model="form.auto_approve_tools" style="accent-color: var(--accent-blue); width: 16px; height: 16px; flex-shrink: 0;" />
          <span>Разрешить выполнять все инструменты без человека в контуре (кроме ask_user)</span>
        </label>
      </div>

      <div class="form-group mt-2">
        <label>Подробное ТЗ (Промпт)</label>
        <textarea v-model="form.initial_prompt" rows="5" class="modern-input text-small custom-scrollbar" placeholder="Опишите, что именно нужно сделать..."></textarea>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="action-btn">Отмена</button>
        <button @click="submit" class="action-btn primary">🚀 Запустить</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  agents: Array,
  projects: Array,
  initialData: Object
});

const emit = defineEmits(['close', 'submit']);
const form = ref({});

watch(() => props.show, (newVal) => {
  if (newVal && props.initialData) {
    form.value = { ...props.initialData };
  }
});

const submit = () => {
  emit('submit', form.value);
};
</script>

<style scoped>
.modal-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-content { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 100%; max-width: 600px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); }
.modal-title { margin: 0 0 16px 0; font-size: 16px; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.modern-input { width: 100%; box-sizing: border-box; background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; outline: none; }
.modern-input:focus { border-color: var(--accent-blue); }
.select-input { cursor: pointer; height: 42px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.text-small { font-size: 13px; padding: 12px; resize: vertical; }
.mt-2 { margin-top: 16px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: 0.2s; }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.primary:hover { background: var(--accent-blue-hover); }
</style>
