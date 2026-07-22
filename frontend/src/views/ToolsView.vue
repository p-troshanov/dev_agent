// frontend/src/views/ToolsView.vue
<template>
  <div class="tools-page custom-scrollbar">
    <div class="tools-wrapper">
      <div class="header-actions">
        <div>
          <h3 class="card-title">Реестр системных инструментов</h3>
          <p class="subtitle">Инструменты предоставляют функционал для системных агентов. Здесь вы можете управлять ими.</p>
        </div>
        <div class="form-group" style="width: 250px;">
          <select v-model="selectedCategory" class="modern-input select-input">
             <option value="">Все категории</option>
             <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div class="tools-list">
        <div v-if="filteredTools.length === 0" class="empty-state">
          Инструменты не найдены. Убедитесь, что бэкенд синхронизировал реестр.
        </div>
        
        <div v-for="tool in filteredTools" :key="tool.id" class="tool-list-item" :class="{'inactive': !tool.is_active}">
          <div class="tool-main-info">
            <div class="tool-header">
              <h4 class="tool-name">{{ tool.name }}</h4>
              <div class="tool-category-badge">{{ tool.category || 'Без категории' }}</div>
              <span v-if="tool.requires_approval" class="meta-tag alert">✋ Аппрув</span>
            </div>
            <p class="tool-desc">{{ tool.description || 'Описание отсутствует' }}</p>
          </div>

          <div class="tool-controls">
            <div class="tool-actions">
              <button @click="openEditModal(tool)" class="action-btn outline">Настройки</button>
              <button @click="openSchemaModal(tool)" class="action-btn">Схема</button>
            </div>
            <div class="toggle-switch">
              <label class="switch">
                <input type="checkbox" :checked="tool.is_active" @change="toggleTool(tool)">
                <span class="slider round"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <div v-if="editingTool" class="modal-overlay" @click.self="closeModals">
        <div class="modal-content custom-scrollbar">
          <h3 class="modal-title">Настройка: {{ editingTool.name }}</h3>
          
          <div class="form-group">
            <label>Категория (Тег для группировки)</label>
            <input type="text" v-model="editForm.category" class="modern-input" placeholder="Система, Файлы, Изображения..." />
          </div>
          
          <div class="form-group mt-2">
            <label>Пользовательское описание</label>
            <textarea v-model="editForm.description" rows="3" class="modern-input text-small" placeholder="Описание того, что делает функция..."></textarea>
          </div>

          <div class="form-group mt-2">
            <label>Дополнительные параметры (JSON)</label>
            <textarea v-model="editForm.settingsStr" rows="4" class="modern-input text-small mono" placeholder='{"model": "provider/model_name"}'></textarea>
            <span v-if="settingsError" style="color: #ff4444; font-size: 11px;">Невалидный JSON</span>
          </div>

          <div class="form-group mt-2">
            <label class="checkbox-inline mt-2 font-weight-bold" style="color: var(--warning)">
              <input type="checkbox" v-model="editForm.requires_approval" /> 
              ✋ Человек-в-контуре (Требовать разрешения при каждом вызове)
            </label>
          </div>

          <div class="modal-footer">
            <button @click="closeModals" class="action-btn">Отмена</button>
            <button @click="saveToolMeta" class="action-btn primary" :disabled="settingsError">💾 Сохранить</button>
          </div>
        </div>
      </div>

      <div v-if="viewingSchema" class="modal-overlay" @click.self="closeModals">
        <div class="modal-content custom-scrollbar" style="max-width: 800px;">
          <h3 class="modal-title">Схема: {{ viewingSchema.name }}</h3>
          <p class="schema-notice">Это техническое представление инструмента для LLM. Изменяется только через код бэкенда.</p>
          <pre class="schema-code custom-scrollbar">{{ JSON.stringify(viewingSchema.schema_json, null, 2) }}</pre>
          <div class="modal-footer">
            <button @click="closeModals" class="action-btn primary">Закрыть</button>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../services/api'

const tools = ref([])
const selectedCategory = ref('')

const categories = computed(() => {
  const cats = tools.value.map(t => t.category).filter(Boolean)
  return [...new Set(cats)].sort()
})

const filteredTools = computed(() => {
  if (!selectedCategory.value) return tools.value
  return tools.value.filter(t => t.category === selectedCategory.value)
})

const editingTool = ref(null)
const viewingSchema = ref(null)

const editForm = ref({
  description: '',
  category: '',
  requires_approval: false,
  settingsStr: '{}'
})
const settingsError = ref(false)

watch(() => editForm.value.settingsStr, (newVal) => {
  try {
    JSON.parse(newVal)
    settingsError.value = false
  } catch (e) {
    settingsError.value = true
  }
})

const fetchTools = async () => {
  try {
    tools.value = await api.getTools()
  } catch (e) {
    console.error("Ошибка загрузки инструментов:", e)
  }
}

const toggleTool = async (tool) => {
  try {
    const newStatus = !tool.is_active
    await api.updateTool(tool.id, { is_active: newStatus })
    tool.is_active = newStatus
  } catch (e) {
    console.error("Ошибка обновления статуса инструмента:", e)
  }
}

const openEditModal = (tool) => {
  editingTool.value = tool
  editForm.value = {
    description: tool.description || '',
    category: tool.category || '',
    requires_approval: tool.requires_approval || false,
    settingsStr: JSON.stringify(tool.settings || {}, null, 2)
  }
}

const openSchemaModal = (tool) => {
  viewingSchema.value = tool
}

const closeModals = () => {
  editingTool.value = null
  viewingSchema.value = null
}

const saveToolMeta = async () => {
  if (!editingTool.value || settingsError.value) return
  
  let parsedSettings = {}
  try {
    parsedSettings = JSON.parse(editForm.value.settingsStr)
  } catch (e) { return }

  try {
    await api.updateTool(editingTool.value.id, {
      description: editForm.value.description,
      category: editForm.value.category,
      requires_approval: editForm.value.requires_approval,
      settings: parsedSettings
    })
    closeModals()
    await fetchTools()
  } catch (e) {
    console.error("Ошибка сохранения метаданных:", e)
  }
}

onMounted(() => {
  fetchTools()
})
</script>

<style scoped>
.tools-page { height: 100%; padding: 24px 24px 100px; overflow-y: auto; }
.tools-wrapper { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
.header-actions { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.card-title { margin: 0; font-size: 18px; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.8px; }
.subtitle { margin: 6px 0 0 0; font-size: 13px; color: var(--text-muted); }

.tools-list { display: flex; flex-direction: column; gap: 12px; }

.tool-list-item { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; gap: 24px; transition: 0.2s; }
.tool-list-item:hover { border-color: var(--accent-blue); }
.tool-list-item.inactive { opacity: 0.5; filter: grayscale(0.5); }

.tool-main-info { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.tool-header { display: flex; align-items: center; gap: 12px; }
.tool-name { font-family: 'Consolas', 'Monaco', monospace; font-size: 15px; margin: 0; color: var(--text-main); font-weight: 600; }
.tool-category-badge { display: inline-block; background: rgba(64, 104, 148, 0.15); color: var(--accent-blue); padding: 4px 8px; border-radius: 4px; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }

.tool-desc { font-size: 13px; color: var(--text-muted); margin: 0; line-height: 1.4; }

.tool-controls { display: flex; align-items: center; gap: 24px; }
.tool-actions { display: flex; gap: 8px; }
.tool-actions button { font-size: 12px; padding: 6px 12px; }

.meta-tag { font-size: 11px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.1); }
.meta-tag.alert { background: rgba(163, 114, 50, 0.2); color: var(--warning); border: 1px solid rgba(163, 114, 50, 0.4); }

/* Тоггл */
.switch { position: relative; display: inline-block; width: 34px; height: 20px; margin-bottom: 0; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--bg-base); transition: .2s; border: 1px solid var(--border-color); }
.slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px; background-color: var(--text-muted); transition: .2s; }
input:checked + .slider { background-color: var(--success); border-color: var(--success); }
input:checked + .slider:before { transform: translateX(14px); background-color: white; }
.slider.round { border-radius: 20px; }
.slider.round:before { border-radius: 50%; }

/* Модалки */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-content { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); }
.modal-title { margin: 0 0 16px 0; font-size: 16px; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
.schema-notice { font-size: 12px; color: var(--warning); margin-top: -10px; margin-bottom: 16px; }
.schema-code { background: var(--bg-base); border: 1px solid var(--border-color); padding: 16px; border-radius: 8px; font-family: 'Consolas', monospace; font-size: 13px; color: #a3b8cc; overflow-x: auto; max-height: 400px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.modern-input { background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; resize: vertical; outline: none; }
.modern-input:focus { border-color: var(--accent-blue); }
.mono { font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; }
.text-small { font-size: 13px; padding: 8px 12px; }
.mt-2 { margin-top: 16px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.empty-state { grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted); font-style: italic; background: var(--bg-surface); border-radius: 10px; border: 1px dashed var(--border-color); }
.checkbox-inline { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; }
.checkbox-inline input { accent-color: var(--warning); width: 16px; height: 16px; cursor: pointer; }
</style>
