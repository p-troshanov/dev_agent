// frontend/src/views/AgentsView.vue
<template>
  <div class="agents-page custom-scrollbar">
    <div class="agents-wrapper">
      <div class="header-actions">
        <h3 class="card-title">Управление Агентами (MAS)</h3>
        <button @click="openCreateModal" class="action-btn primary">➕ Создать агента</button>
      </div>

      <div class="agents-grid">
        <div v-if="agents.length === 0" class="empty-state">
          Нет созданных агентов. Создайте первого, чтобы автоматизировать задачи в диалогах!
        </div>
        
        <div v-for="agent in agents" :key="agent.id" class="agent-card">
          <div class="agent-header">
            <div style="display: flex; align-items: center; gap: 12px;">
               <img v-if="agent.avatar" :src="agent.avatar" class="agent-avatar-small" />
               <div v-else class="agent-avatar-small" style="display: flex; align-items: center; justify-content: center; font-size: 20px;">🤖</div>
               <div>
                 <h4 class="agent-name-title">{{ agent.name }}</h4>
                 <div v-if="agent.profession" class="agent-prof">{{ agent.profession }}</div>
               </div>
            </div>
            <div class="agent-actions">
              <button @click="editAgent(agent)" class="action-icon-btn" title="Редактировать">✏️</button>
              <button @click="deleteAgent(agent.id)" class="action-icon-btn delete-btn" title="Удалить">✖</button>
            </div>
          </div>
          <p class="agent-desc">{{ agent.description || 'Нет описания' }}</p>
          
          <div class="agent-meta">
            <span class="meta-tag">🧠 {{ getAgentModelDisplay(agent.model) }}</span>
            <span v-if="agent.is_main" class="meta-tag main-tag">👑 Основной</span>
            <span v-if="agent.is_default" class="meta-tag default-tag">🌟 По умолчанию</span>
            <span v-if="agent.tools && agent.tools.length" class="meta-tag" style="color: var(--accent-blue);">🔧 {{ agent.tools.length }} инстр.</span>
            <span v-for="sk in Object.keys(agent.skills)" :key="sk" class="meta-tag active-skill">
              ⚙️ {{ getSkillName(sk) }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content custom-scrollbar">
          <h3 class="modal-title">{{ editingAgentId ? 'Редактировать агента' : 'Новый агент' }}</h3>
          
          <div class="agent-header-row" style="display: flex; gap: 16px; align-items: center; margin-bottom: 16px;">
             <div class="avatar-upload">
                <label class="avatar-circle">
                   <img v-if="form.avatar" :src="form.avatar" alt="Avatar" />
                   <span v-else style="font-size: 24px; color: var(--text-muted);">📷</span>
                   <input type="file" accept="image/*" @change="handleAvatarUpload" style="display: none;" />
                </label>
             </div>
             <div class="form-group" style="flex: 1;">
               <label>Имя агента</label>
               <input type="text" v-model="form.name" class="modern-input" placeholder="Например: Алиса" />
             </div>
             <div class="form-group" style="flex: 1;">
               <label>Должность (Роль)</label>
               <input type="text" v-model="form.profession" class="modern-input" placeholder="Например: Дизайнер" />
             </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Провайдер (LLM)</label>
              <select v-model="uiProvider" class="modern-input select-input">
                <option value="auto">Авто (базовая)</option>
                <option value="groq">Groq</option>
                <option value="gemini">Gemini</option>
                <option value="openrouter">OpenRouter</option>
              </select>
            </div>
            <div v-if="uiProvider === 'openrouter'" class="form-group" style="flex: 1; border: 1px dashed rgba(147, 51, 234, 0.3); padding: 8px; border-radius: 8px; background: rgba(147, 51, 234, 0.05);">
              <label style="color: #c084fc;">Модель OpenRouter</label>
              <select v-model="uiOrModel" class="modern-input select-input" style="width: 100%; margin-bottom: 8px;">
                <option v-for="m in popularOrModels" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
              <input v-if="uiOrModel === 'custom'" type="text" v-model="uiOrCustomId" class="modern-input" style="width: 100%;" placeholder="Провайдер/название-модели" />
            </div>
          </div>
          
          <div class="form-group mt-2">
            <label>Настройки LLM (JSON)</label>
            <textarea v-model="form.settingsStr" rows="2" class="modern-input text-small mono" placeholder='{"temperature": 0.7, "top_p": 0.9}'></textarea>
            <span v-if="settingsError" style="color: #ff4444; font-size: 11px;">Невалидный формат JSON</span>
          </div>

          <div class="form-group mt-2">
            <label>Должностные инструкции (Описание роли)</label>
            <input type="text" v-model="form.description" class="modern-input" placeholder="Для чего нужен этот агент..." />
          </div>

          <div class="form-group mt-2">
            <label>Системный промпт (Только для Основного агента)</label>
            <textarea v-model="form.system_prompt" rows="3" class="modern-input text-small" placeholder="Например: Ты системный администратор. Твоя задача..."></textarea>
          </div>

          <div class="form-row mt-2">
            <div class="form-group">
              <label class="checkbox-inline mt-2 font-weight-bold">
                <input type="checkbox" v-model="form.is_main" /> 👑 Основной (Управляющий)
              </label>
            </div>
            <div class="form-group">
              <label class="checkbox-inline mt-2 font-weight-bold">
                <input type="checkbox" v-model="form.is_default" /> 🌟 По умолчанию для новых чатов
              </label>
            </div>
          </div>

          <div class="form-group mt-2" style="background: rgba(163, 114, 50, 0.1); padding: 10px; border-radius: 8px;">
            <label class="checkbox-inline" style="color: var(--warning);">
              <input type="checkbox" v-model="form.apply_to_all" /> ⚠️ Применить этого агента КО ВСЕМ существующим чатам?
            </label>
          </div>

          <div class="form-group mt-3">
            <label>Разрешенные инструменты (Для делегирования)</label>
            <input type="text" v-model="toolSearchQuery" class="modern-input text-small" placeholder="Поиск по названию, описанию или категории..." style="margin-bottom: 8px;" />
            <div class="skills-checkbox-group custom-scrollbar" style="max-height: 180px;">
              <div v-if="toolsList.length === 0" style="padding: 8px; font-size: 12px; color: var(--text-muted);">
                Нет доступных инструментов. Загрузите реестр.
              </div>
              <div v-else-if="filteredTools.length === 0" style="padding: 8px; font-size: 12px; color: var(--text-muted);">
                По вашему запросу ничего не найдено.
              </div>
              <label v-for="t in filteredTools" :key="t.name" class="skill-checkbox-item" :title="t.description">
                <input type="checkbox" :value="t.name" v-model="form.activeTools"> 
                <span>🔧 {{ t.name }} <span style="opacity:0.5; font-size:11px; margin-left: 4px;">— {{ t.category || 'Система' }}</span></span>
              </label>
            </div>
          </div>

          <div class="form-group mt-3">
            <label>Способности Ввода/Вывода (I/O)</label>
            <div class="skills-checkbox-group">
              <div class="skill-item-container">
                <label class="skill-checkbox-item">
                  <input type="checkbox" v-model="form.hasTTS"> 
                  <span>🔊 Синтез речи (Отвечает голосом)</span>
                </label>
                <div v-if="form.hasTTS" class="skill-prompt-area">
                  <select v-model="form.ttsVoice" class="modern-input select-input text-small">
                    <option value="ru-RU-SvetlanaNeural">👩 Женский (Светлана)</option>
                    <option value="ru-RU-DmitryNeural">👨 Мужской (Дмитрий)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="closeModal" class="action-btn">Отмена</button>
            <button @click="saveAgent" class="action-btn primary" :disabled="settingsError">💾 Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../services/api'

const agents = ref([])
const toolsList = ref([])

const showModal = ref(false)
const editingAgentId = ref(null)

const uiProvider = ref('auto')
const uiOrModel = ref('openrouter/anthropic/claude-3.5-sonnet')
const uiOrCustomId = ref('')
const toolSearchQuery = ref('')

const popularOrModels = [
  { id: 'openrouter/anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet' },
  { id: 'openrouter/openai/gpt-4o', name: 'GPT-4o' },
  { id: 'openrouter/openai/gpt-4o-mini', name: 'GPT-4o Mini' },
  { id: 'openrouter/meta-llama/llama-3.1-70b-instruct', name: 'Llama 3.1 70B' },
  { id: 'openrouter/meta-llama/llama-3.1-8b-instruct', name: 'Llama 3.1 8B' },
  { id: 'openrouter/google/gemini-1.5-pro', name: 'Gemini 1.5 Pro' },
  { id: 'openrouter/google/gemini-1.5-flash', name: 'Gemini 1.5 Flash' },
  { id: 'openrouter/qwen/qwen-2.5-72b-instruct', name: 'Qwen 2.5 72B' },
  { id: 'custom', name: 'Свой вариант (Ввести ID)...' }
]

const form = ref({
  name: '', profession: '', description: '', model: null, system_prompt: '',
  activeTools: [], settingsStr: '{}',
  is_default: false, is_main: false, apply_to_all: false,
  hasTTS: false, ttsVoice: 'ru-RU-SvetlanaNeural',
  avatar: null
})

const settingsError = ref(false)

const filteredTools = computed(() => {
  let list = toolsList.value;

  if (toolSearchQuery.value) {
    const query = toolSearchQuery.value.toLowerCase()
    list = list.filter(t => {
      const nameMatch = t.name?.toLowerCase().includes(query)
      const descMatch = t.description?.toLowerCase().includes(query)
      const catMatch = (t.category || 'Система').toLowerCase().includes(query)
      return nameMatch || descMatch || catMatch
    })
  }

  // Сортировка: сначала выбранные инструменты (true), затем не выбранные (false). Внутри группы - по алфавиту.
  return list.slice().sort((a, b) => {
    const isASelected = form.value.activeTools.includes(a.name)
    const isBSelected = form.value.activeTools.includes(b.name)

    if (isASelected && !isBSelected) return -1
    if (!isASelected && isBSelected) return 1
    
    return (a.name || '').localeCompare(b.name || '')
  })
})

watch(() => form.value.settingsStr, (newVal) => {
  try {
    JSON.parse(newVal || '{}')
    settingsError.value = false
  } catch(e) {
    settingsError.value = true
  }
})

const getSkillName = (id) => {
  const ioNames = { 'tts': '🔊 Голос' }
  if (ioNames[id]) return ioNames[id]
  return id
}

const getAgentModelDisplay = (model) => {
  if (!model) return 'Auto'
  if (model === 'groq') return 'Groq'
  if (model === 'gemini') return 'Gemini'
  if (model.startsWith('openrouter/')) {
    const known = popularOrModels.find(m => m.id === model)
    return known ? `OR: ${known.name}` : `OR: ${model.replace('openrouter/', '')}`
  }
  return model
}

const handleAvatarUpload = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    form.value.avatar = ev.target.result;
  };
  reader.readAsDataURL(file);
};

const fetchAgents = async () => {
  try { agents.value = await api.getAgents() } catch (e) { console.error("Ошибка загрузки агентов:", e) }
}

const fetchTools = async () => {
  try { toolsList.value = await api.getTools() } catch (e) { console.error("Ошибка загрузки инструментов:", e) }
}

const openCreateModal = () => {
  editingAgentId.value = null
  uiProvider.value = 'auto'
  uiOrModel.value = 'openrouter/anthropic/claude-3.5-sonnet'
  uiOrCustomId.value = ''
  toolSearchQuery.value = ''

  form.value = { 
    name: '', profession: '', description: '', model: null, system_prompt: '',
    activeTools: [], settingsStr: '{}',
    is_default: false, is_main: false, apply_to_all: false,
    hasTTS: false, ttsVoice: 'ru-RU-SvetlanaNeural',
    avatar: null
  }
  showModal.value = true
}

const editAgent = (agent) => {
  editingAgentId.value = agent.id
  toolSearchQuery.value = ''
  
  if (!agent.model) {
    uiProvider.value = 'auto'
    uiOrModel.value = 'openrouter/anthropic/claude-3.5-sonnet'
    uiOrCustomId.value = ''
  } else if (['groq', 'gemini'].includes(agent.model)) {
    uiProvider.value = agent.model
    uiOrModel.value = 'openrouter/anthropic/claude-3.5-sonnet'
    uiOrCustomId.value = ''
  } else if (agent.model.startsWith('openrouter/')) {
    uiProvider.value = 'openrouter'
    if (popularOrModels.find(m => m.id === agent.model)) {
      uiOrModel.value = agent.model
      uiOrCustomId.value = ''
    } else {
      uiOrModel.value = 'custom'
      uiOrCustomId.value = agent.model.replace('openrouter/', '')
    }
  }

  const skillsObj = agent.skills || {}
  form.value = {
    name: agent.name, profession: agent.profession || '', description: agent.description, model: agent.model,
    system_prompt: agent.system_prompt || '', 
    activeTools: agent.tools || [],
    settingsStr: JSON.stringify(agent.settings || {}, null, 2),
    is_default: agent.is_default, is_main: agent.is_main, apply_to_all: false,
    hasTTS: !!skillsObj.tts,
    ttsVoice: skillsObj.tts ? (skillsObj.tts.voice || 'ru-RU-SvetlanaNeural') : 'ru-RU-SvetlanaNeural',
    avatar: agent.avatar || null
  }
  showModal.value = true
}

const closeModal = () => showModal.value = false

const saveAgent = async () => {
  if (settingsError.value) return alert("Исправьте ошибки в JSON настройках LLM")
  if (!form.value.name.trim()) return alert("Имя агента обязательно!")

  if (uiProvider.value === 'auto') {
    form.value.model = null
  } else if (uiProvider.value === 'openrouter') {
    let selectedId = uiOrModel.value === 'custom' ? uiOrCustomId.value.trim() : uiOrModel.value
    if (selectedId && !selectedId.startsWith('openrouter/')) {
      selectedId = 'openrouter/' + selectedId
    }
    form.value.model = selectedId
  } else {
    form.value.model = uiProvider.value
  }

  const payloadSkills = {}
  if (form.value.hasTTS) {
    payloadSkills.tts = { voice: form.value.ttsVoice }
  }

  let parsedSettings = {}
  try {
    parsedSettings = JSON.parse(form.value.settingsStr || '{}')
  } catch (e) {
    return alert("Ошибка парсинга JSON настроек")
  }

  const payload = {
    name: form.value.name, profession: form.value.profession, description: form.value.description, model: form.value.model,
    system_prompt: form.value.system_prompt, skills: payloadSkills,
    tools: form.value.activeTools, settings: parsedSettings,
    is_default: form.value.is_default, is_main: form.value.is_main, apply_to_all: form.value.apply_to_all,
    avatar: form.value.avatar
  }
  
  try {
    if (editingAgentId.value) await api.updateAgent(editingAgentId.value, payload)
    else await api.createAgent(payload)
    closeModal()
    await fetchAgents()
  } catch (e) { console.error("Ошибка сохранения:", e) }
}

const deleteAgent = async (id) => {
  if (!confirm("Точно удалить этого агента?")) return
  try { await api.deleteAgent(id); await fetchAgents() } catch (e) {}
}

onMounted(() => {
  fetchAgents()
  fetchTools()
})
</script>

<style scoped>
.agents-page { height: 100%; padding: 24px 24px 100px; overflow-y: auto; }
.agents-wrapper { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
.header-actions { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.card-title { margin: 0; font-size: 16px; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.8px; }
.agents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.agent-card { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; transition: 0.2s; }
.agent-card:hover { border-color: var(--accent-blue); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }
.agent-header { display: flex; justify-content: space-between; align-items: flex-start; }
.agent-name-title { margin: 0; font-size: 16px; color: var(--text-main); line-height: 1.2; }
.agent-prof { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.agent-actions { display: flex; gap: 4px; }
.agent-desc { font-size: 13px; color: var(--text-muted); margin: 0; flex: 1; }
.agent-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; border-top: 1px solid var(--border-color); padding-top: 12px; }
.meta-tag { background: var(--bg-base); border: 1px solid var(--border-color); font-size: 11px; padding: 4px 8px; border-radius: 6px; color: var(--text-muted); }
.meta-tag.active-skill { color: var(--accent-purple); border-color: rgba(107, 76, 154, 0.4); background: rgba(107, 76, 154, 0.1); }
.meta-tag.default-tag { color: var(--warning); border-color: rgba(163, 114, 50, 0.4); background: rgba(163, 114, 50, 0.1); }
.meta-tag.main-tag { background: var(--accent-blue); border-color: transparent; color: #fff; font-weight: bold; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-content { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; width: 100%; max-width: 650px; max-height: 90vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); }
.modal-title { margin: 0 0 16px 0; font-size: 16px; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }

/* Аватар и форма */
.avatar-upload { flex-shrink: 0; }
.avatar-circle { display: flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; background: var(--bg-base); border: 2px dashed var(--border-color); cursor: pointer; overflow: hidden; transition: 0.2s; }
.avatar-circle:hover { border-color: var(--accent-blue); }
.avatar-circle img { width: 100%; height: 100%; object-fit: cover; }
.agent-avatar-small { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: var(--bg-panel); border: 1px solid var(--border-color); flex-shrink: 0; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-row { display: flex; gap: 16px; align-items: center; }
.form-row .form-group { flex: 1; }
label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
.modern-input { box-sizing: border-box; background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; resize: vertical; outline: none; width: 100%; }
.modern-input:focus { border-color: var(--accent-blue); }
.mono { font-family: 'Consolas', 'Monaco', monospace; }
.text-small { font-size: 13px; padding: 8px 12px; }
.select-input { cursor: pointer; height: 42px; }
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 16px; }
.mt-3 { margin-top: 24px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.skills-checkbox-group { display: flex; flex-direction: column; gap: 8px; background: var(--bg-base); padding: 12px; border-radius: 8px; border: 1px dashed var(--border-color); overflow-y: auto; }
.skill-item-container { display: flex; flex-direction: column; border-bottom: 1px solid var(--bg-surface-hover); padding-bottom: 10px; margin-bottom: 6px; }
.skill-item-container:last-child { border-bottom: none; padding-bottom: 0; margin-bottom: 0; }
.skill-checkbox-item { display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: 13px; color: var(--text-main); padding: 4px 0; transition: 0.2s; }
.skill-checkbox-item:hover { color: var(--accent-blue); }
.skill-checkbox-item input { accent-color: var(--accent-purple); cursor: pointer; width: 16px; height: 16px; }
.skill-prompt-area { margin-top: 8px; padding-left: 26px; padding-right: 8px; }
.skill-prompt-area textarea { width: 100%; min-height: 80px; box-sizing: border-box; }
.checkbox-inline { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 13px; }
.checkbox-inline input { accent-color: var(--warning); width: 16px; height: 16px; cursor: pointer; }
.empty-state { grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted); font-style: italic; background: var(--bg-surface); border-radius: 10px; border: 1px dashed var(--border-color); }
</style>
