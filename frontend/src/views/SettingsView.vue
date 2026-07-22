// frontend/src/views/SettingsView.vue
<template>
  <div class="settings-page custom-scrollbar">
    <div class="settings-wrapper">
      <div class="settings-header-actions">
        <p class="subtitle">Глобальные настройки системы</p>
        <button @click="saveSettings" class="action-btn primary">💾 Сохранить настройки</button>
      </div>

      <div class="settings-container">
        <div class="settings-card">
          <h3 class="card-title">Основные настройки</h3>
          <p class="desc-text" style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px; margin-top: 0;">
            Настройте базовые параметры вашего профиля и среды.
          </p>
          
          <div class="form-row">
            <div class="form-group">
              <label>Ваше Имя (для чата)</label>
              <input type="text" v-model="settings.user_name" class="modern-input" placeholder="Например: Владелец" />
            </div>
            <div class="form-group">
              <label>Город для погоды</label>
              <input type="text" v-model="settings.weather_city" class="modern-input" placeholder="Например: Москва" />
            </div>
          </div>
          
          <div class="form-group mt-2">
            <label>Часовой пояс (для окружения задач)</label>
            <select v-model="settings.timezone" class="modern-input select-input">
              <option value="Europe/Moscow">Москва (UTC+3)</option>
              <option value="Europe/Kaliningrad">Калининград (UTC+2)</option>
              <option value="Europe/Samara">Самара (UTC+4)</option>
              <option value="Asia/Yekaterinburg">Екатеринбург (UTC+5)</option>
              <option value="Asia/Omsk">Омск (UTC+6)</option>
              <option value="Asia/Krasnoyarsk">Красноярск (UTC+7)</option>
              <option value="Asia/Irkutsk">Иркутск (UTC+8)</option>
              <option value="Asia/Yakutsk">Якутск (UTC+9)</option>
              <option value="Asia/Vladivostok">Владивосток (UTC+10)</option>
              <option value="Asia/Magadan">Магадан (UTC+11)</option>
              <option value="Asia/Kamchatka">Камчатка (UTC+12)</option>
              <option value="UTC">UTC (По умолчанию)</option>
            </select>
          </div>

          <div class="form-group mt-2">
            <label>GitHub Personal Access Token</label>
            <input type="password" v-model="settings.github_token" class="modern-input" placeholder="ghp_..." />
            <p style="font-size: 11px; color: var(--text-muted); margin-top: 4px; margin-bottom: 0;">Используется агентами для безопасной синхронизации проектов с вашим GitHub.</p>
          </div>
          
          <div class="form-group mt-2">
            <label>Аватар пользователя</label>
            <div class="avatar-upload-wrapper">
              <img v-if="settings.avatar" :src="settings.avatar" class="user-avatar-preview" />
              <div v-else class="user-avatar-preview placeholder">👤</div>
              <input type="file" @change="onAvatarUpload" accept="image/*" class="modern-input file-input" />
            </div>
          </div>
        </div>

        <div class="settings-card">
          <h3 class="card-title">API Ключи (Интеграции LLM)</h3>

          <div class="add-key-form">
            <div class="form-group" style="width: 200px;">
              <label>Провайдер</label>
              <select v-model="newKeyProvider" class="modern-input select-input">
                <option value="groq">Groq</option>
                <option value="gemini">Gemini</option>
                <option value="openrouter">OpenRouter</option>
              </select>
            </div>
            <div class="form-group" style="flex: 1;">
              <label>API Ключ</label>
              <input type="text" v-model="newKeyValue" class="modern-input mono" placeholder="Вставьте ключ сюда..." />
            </div>
            <div class="form-group" style="justify-content: flex-end;">
              <button @click="addApiKey" class="action-btn primary" style="height: 47px;">➕ Добавить</button>
            </div>
          </div>

          <div class="keys-list" v-if="apiKeys.length > 0">
            <div v-for="k in apiKeys" :key="k.id" class="key-item">
              <div class="key-info">
                <span class="provider-badge" :class="k.provider">{{ k.provider }}</span>
                <span class="key-string mono">{{ formatKeyString(k.api_key) }}</span>
                <div style="display: flex; flex-direction: column; gap: 4px;">
                  <span class="key-state" :class="isKeyActive(k.provider, k.api_key) ? 'active' : 'paused'">
                    {{ formatKeyStatus(k.provider, k.api_key) }}
                  </span>
                  <span v-if="k.provider === 'openrouter' && balances[k.id]" class="key-balance">
                    Остаток: ${{ balances[k.id].remaining_balance !== null ? balances[k.id].remaining_balance.toFixed(4) : 'Безлимит' }}
                  </span>
                </div>
              </div>
              <button @click="deleteApiKey(k.id)" class="action-btn danger">Удалить</button>
            </div>
          </div>
          <div v-else class="empty-keys">
            Нет добавленных ключей. Базовые ключи будут браться из .env (если есть).
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from '../services/api'
import { appStore } from '../stores/appStore'

const settings = ref({
  user_name: "Вы",
  weather_city: "Москва",
  avatar: null,
  timezone: "Europe/Moscow",
  github_token: "",
})

const keyStatuses = ref({ groq: {}, gemini: {}, openrouter: {} })
const apiKeys = ref([])
const balances = ref({})

const newKeyProvider = ref("groq")
const newKeyValue = ref("")

let statusInterval = null

const fetchSettings = async () => {
  try {
    const data = await api.getSettings()
    settings.value = { ...settings.value, ...data }
  } catch (e) {
    console.error("Failed to load settings:", e)
  }
}

const onAvatarUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    settings.value.avatar = evt.target.result
  }
  reader.readAsDataURL(file)
}

const fetchApiKeys = async () => {
  try {
    apiKeys.value = await api.getKeys()
  } catch (e) {
    console.error("Failed to load keys:", e)
  }
}

const saveSettings = async () => {
  try {
    await api.updateSettings(settings.value)
    appStore.settings = { ...appStore.settings, ...settings.value }
    alert("Настройки сохранены успешно!")
  } catch(e) {
    console.error("Failed to save settings:", e)
    alert("Ошибка при сохранении настроек")
  }
}

const addApiKey = async () => {
  if (!newKeyValue.value.trim()) return
  try {
    await api.addKey({ provider: newKeyProvider.value, api_key: newKeyValue.value.trim() })
    newKeyValue.value = ""
    await fetchApiKeys()
    await fetchKeyBalances()
  } catch(e) {
    console.error("Failed to add key:", e)
  }
}

const deleteApiKey = async (id) => {
  if (!confirm("Удалить этот ключ?")) return
  try {
    await api.deleteKey(id)
    await fetchApiKeys()
  } catch(e) {
    console.error("Failed to delete key:", e)
  }
}

const fetchKeyStatuses = async () => {
  try { keyStatuses.value = await api.getKeysStatus() } catch (e) {}
}

const fetchKeyBalances = async () => {
  try {
    const data = await api.getKeyBalances()
    balances.value = data
  } catch(e) {}
}

const isKeyActive = (provider, keyStr) => {
  const timestamp = keyStatuses.value[provider]?.[keyStr]
  return !timestamp || timestamp * 1000 < Date.now()
}

const formatKeyStatus = (provider, keyStr) => {
  const timestamp = keyStatuses.value[provider]?.[keyStr]
  if (!timestamp || timestamp * 1000 < Date.now()) return "✅ Активен"
  const date = new Date(timestamp * 1000)
  return `⏳ Пауза до ${date.toLocaleTimeString()}`
}

const formatKeyString = (key) => {
  if (key.length <= 12) return "••••••••"
  return key.substring(0, 4) + "..." + key.substring(key.length - 4)
}

onMounted(() => {
  fetchSettings()
  fetchApiKeys()
  fetchKeyStatuses()
  fetchKeyBalances()
  statusInterval = setInterval(() => {
    fetchKeyStatuses()
    fetchKeyBalances()
  }, 10000)
})

onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
})
</script>

<style scoped>
.settings-page { height: 100%; padding: 24px 24px 100px; overflow-y: auto; }
.settings-wrapper { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
.settings-header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }
.settings-container { display: flex; flex-direction: column; gap: 24px; }
.settings-card { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 10px; padding: 24px; display: flex; flex-direction: column; gap: 18px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.card-title { margin: 0; font-size: 14px; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-row { display: flex; gap: 20px; }
.form-row .form-group { flex: 1; }
label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
.modern-input { background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 12px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; resize: vertical; }
.select-input { cursor: pointer; height: 47px; }
.modern-input:focus { outline: none; border-color: var(--accent-blue); }
.modern-input.mono { font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; }
.mt-2 { margin-top: 16px; }

.avatar-upload-wrapper { display: flex; align-items: center; gap: 16px; }
.user-avatar-preview { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border-color); }
.user-avatar-preview.placeholder { display: flex; align-items: center; justify-content: center; font-size: 28px; background: var(--bg-base); }
.file-input { flex: 1; cursor: pointer; padding: 8px 12px; }

/* Стили ключей */
.add-key-form { display: flex; gap: 12px; align-items: flex-end; background: var(--bg-base); padding: 16px; border-radius: 8px; border: 1px dashed var(--border-color); }
.keys-list { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
.key-item { display: flex; justify-content: space-between; align-items: center; background: var(--bg-base); border: 1px solid var(--border-color); padding: 12px 16px; border-radius: 8px; }
.key-info { display: flex; align-items: center; gap: 16px; }
.provider-badge { font-size: 11px; text-transform: uppercase; font-weight: bold; padding: 4px 8px; border-radius: 4px; letter-spacing: 0.5px; }
.provider-badge.groq { background: rgba(245, 80, 54, 0.15); color: #f55036; }
.provider-badge.gemini { background: rgba(66, 133, 244, 0.15); color: #4285f4; }
.provider-badge.openrouter { background: rgba(147, 51, 234, 0.15); color: #c084fc; }
.key-string { color: var(--text-main); font-size: 13px; }
.key-state.active { color: var(--success); font-weight: 600; font-size: 13px; }
.key-state.paused { color: var(--warning); font-size: 13px; }
.key-balance { color: var(--accent-blue); font-size: 11px; background: rgba(64, 104, 148, 0.1); padding: 2px 6px; border-radius: 4px; }
.empty-keys { text-align: center; padding: 24px; color: var(--text-muted); font-size: 14px; border: 1px dashed var(--border-color); border-radius: 8px; }
</style>
