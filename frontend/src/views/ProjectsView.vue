// frontend/src/views/ProjectsView.vue
<template>
  <div class="projects-page custom-scrollbar">
    <div class="projects-wrapper">
      <div class="header-actions">
        <div>
          <h3 class="card-title">Управление проектами</h3>
          <p class="subtitle">Создавайте проекты, чтобы привязывать задачи к конкретным директориям и хранить настройки окружения.</p>
        </div>
        <button @click="openCreateModal" class="action-btn primary">➕ Добавить проект</button>
      </div>

      <div class="projects-grid">
        <div v-if="projects.length === 0" class="empty-state">
          Проектов пока нет.
        </div>
        
        <div v-for="proj in projects" :key="proj.id" class="project-card">
          <div class="project-header">
            <h4>{{ proj.name }}</h4>
            <div class="project-actions">
              <button @click="editProject(proj)" class="action-icon-btn" title="Редактировать">✏️</button>
              <button @click="deleteProject(proj.id)" class="action-icon-btn delete-btn" title="Удалить">✖</button>
            </div>
          </div>
          <p class="project-desc">{{ proj.description || 'Описание отсутствует' }}</p>
          <div class="project-meta">
            <span class="meta-tag">📁 {{ proj.folder_name }}</span>
          </div>
        </div>
      </div>

      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content custom-scrollbar">
          <h3 class="modal-title">{{ editingProjectId ? 'Редактировать проект' : 'Новый проект' }}</h3>
          
          <div class="form-group">
            <label>Название проекта *</label>
            <input type="text" v-model="form.name" class="modern-input" placeholder="Например: ScalpTerminal" />
          </div>

          <div class="form-group mt-2">
            <label>Описание</label>
            <textarea v-model="form.description" rows="2" class="modern-input text-small" placeholder="Суть проекта..."></textarea>
          </div>

          <div class="form-group mt-2">
            <label>Папка проекта (Относительно песочницы: /workspace/user_x) *</label>
            <input type="text" v-model="form.folder_name" class="modern-input mono" placeholder="Например: backend/api" />
          </div>

          <div class="form-row mt-2">
            <div class="form-group">
              <label>GitHub Репозиторий</label>
              <input type="text" v-model="form.github_repo" class="modern-input mono" placeholder="PavelTroshanov/repo" />
            </div>
            <div class="form-group">
              <label>Ветка</label>
              <input type="text" v-model="form.default_branch" class="modern-input mono" placeholder="main" />
            </div>
          </div>

          <div class="form-group mt-2">
            <label>Telegram Chat ID (Опционально)</label>
            <input type="text" v-model="form.telegram_chat_id" class="modern-input mono" placeholder="Например: -1001234567890" />
          </div>

          <div class="form-group mt-2">
            <label>Дополнительные настройки (JSON)</label>
            <textarea v-model="form.settingsStr" rows="4" class="modern-input text-small mono" placeholder='{"env": "prod"}'></textarea>
            <span v-if="settingsError" style="color: #ff4444; font-size: 11px;">Невалидный JSON</span>
          </div>

          <div class="modal-footer">
            <button @click="closeModal" class="action-btn">Отмена</button>
            <button @click="saveProject" class="action-btn primary" :disabled="settingsError">💾 Сохранить</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from '../services/api'

const projects = ref([])
const showModal = ref(false)
const editingProjectId = ref(null)

const form = ref({
  name: '',
  description: '',
  folder_name: '',
  github_repo: '',
  default_branch: 'main',
  telegram_chat_id: '',
  settingsStr: '{}'
})
const settingsError = ref(false)

watch(() => form.value.settingsStr, (newVal) => {
  try {
    JSON.parse(newVal)
    settingsError.value = false
  } catch (e) {
    settingsError.value = true
  }
})

const fetchProjects = async () => {
  try {
    projects.value = await api.getProjects()
  } catch (e) {
    console.error("Ошибка загрузки проектов:", e)
  }
}

const openCreateModal = () => {
  editingProjectId.value = null
  form.value = {
    name: '',
    description: '',
    folder_name: '',
    github_repo: '',
    default_branch: 'main',
    telegram_chat_id: '',
    settingsStr: '{}'
  }
  showModal.value = true
}

const editProject = (proj) => {
  editingProjectId.value = proj.id
  const settingsObj = proj.settings || {}
  
  form.value = {
    name: proj.name,
    description: proj.description || '',
    folder_name: proj.folder_name || '',
    github_repo: settingsObj.github_repo || '',
    default_branch: settingsObj.default_branch || 'main',
    telegram_chat_id: settingsObj.telegram_chat_id || '',
    settingsStr: JSON.stringify(settingsObj, null, 2)
  }
  showModal.value = true
}

const closeModal = () => showModal.value = false

const saveProject = async () => {
  if (!form.value.name.trim()) return alert("Название проекта обязательно!")
  if (!form.value.folder_name.trim()) return alert("Папка проекта обязательна! Укажите путь относительно корня вашей песочницы.")
  if (settingsError.value) return
  
  let parsedSettings = {}
  try {
    parsedSettings = JSON.parse(form.value.settingsStr)
  } catch (e) { return }

  if (form.value.github_repo.trim()) {
    parsedSettings.github_repo = form.value.github_repo.trim()
  } else {
    delete parsedSettings.github_repo
  }
  
  if (form.value.default_branch.trim()) {
    parsedSettings.default_branch = form.value.default_branch.trim()
  } else {
    delete parsedSettings.default_branch
  }

  if (form.value.telegram_chat_id.trim()) {
    parsedSettings.telegram_chat_id = form.value.telegram_chat_id.trim()
  } else {
    delete parsedSettings.telegram_chat_id
  }

  const payload = {
    name: form.value.name,
    description: form.value.description,
    folder_name: form.value.folder_name.trim(),
    settings: parsedSettings
  }

  try {
    if (editingProjectId.value) {
      await api.updateProject(editingProjectId.value, payload)
    } else {
      await api.createProject(payload)
    }
    closeModal()
    await fetchProjects()
  } catch (e) {
    console.error("Ошибка сохранения проекта:", e)
  }
}

const deleteProject = async (id) => {
  if (!confirm("Точно удалить этот проект? Это не удалит файлы на диске, но отвяжет задачи и контакты.")) return
  try {
    await api.deleteProject(id)
    await fetchProjects()
  } catch (e) { console.error("Ошибка удаления:", e) }
}

onMounted(() => fetchProjects())
</script>

<style scoped>
.projects-page { height: 100%; padding: 24px 24px 100px; overflow-y: auto; }
.projects-wrapper { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
.header-actions { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.card-title { margin: 0; font-size: 16px; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.8px; }
.subtitle { margin: 6px 0 0 0; font-size: 13px; color: var(--text-muted); }

.projects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.project-card { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; transition: 0.2s; }
.project-card:hover { border-color: var(--accent-blue); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }
.project-header { display: flex; justify-content: space-between; align-items: flex-start; }
.project-header h4 { margin: 0; font-size: 16px; color: var(--text-main); }
.project-actions { display: flex; gap: 4px; }
.project-desc { font-size: 13px; color: var(--text-muted); margin: 0; flex: 1; }
.project-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; border-top: 1px solid var(--border-color); padding-top: 12px; }
.meta-tag { background: var(--bg-base); border: 1px solid var(--border-color); font-size: 12px; padding: 4px 8px; border-radius: 6px; color: var(--text-muted); font-family: 'Consolas', monospace; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-content { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); }
.modal-title { margin: 0 0 16px 0; font-size: 16px; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-row { display: flex; gap: 16px; }
.form-row .form-group { flex: 1; }

label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.modern-input { background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; resize: vertical; outline: none; }
.modern-input:focus { border-color: var(--accent-blue); }
.mono { font-family: 'Consolas', 'Monaco', monospace; }
.text-small { font-size: 13px; padding: 8px 12px; }
.mt-2 { margin-top: 16px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.empty-state { grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted); font-style: italic; background: var(--bg-surface); border-radius: 10px; border: 1px dashed var(--border-color); }
</style>
