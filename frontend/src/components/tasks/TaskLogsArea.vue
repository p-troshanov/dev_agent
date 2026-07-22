// frontend/src/components/tasks/TaskLogsArea.vue
<template>
  <div class="task-content">
    <div v-if="!activeTaskId" class="empty-state">
      <div class="empty-icon">🛠️</div>
      <p>Выберите задачу слева или создайте новую, чтобы посмотреть процесс выполнения.</p>
    </div>

    <div v-else class="logs-area custom-scrollbar" ref="logsContainer" @click="handleLogClick">
      <div class="logs-header">
        <div style="display: flex; flex-direction: column; gap: 4px;">
           <h4>Протокол (ID: {{ activeTaskId }})</h4>
           <span class="context-volume" title="Размер контекста">🧠 ~{{ contextTokens }} t</span>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">
          <button v-if="activeTask && ['running', 'pending', 'waiting_user'].includes(activeTask.status)" @click="handleCancel" class="action-btn danger">⏹ Остановить</button>
          <button @click="openTaskIde" class="action-btn outline" title="Открыть рабочую директорию задачи в IDE">☁️ Папка задачи</button>
          <button @click="$emit('duplicate')" class="action-btn outline" title="Создать новую задачу на основе этой">📋 Дублировать</button>
          <button @click="downloadTaskContext" class="action-btn outline" title="Скачать контекст">📥 Контекст</button>
          <button @click="downloadTaskDebug" class="action-btn outline" title="JSON Отладка">🐞 JSON</button>
          <button @click="$emit('refresh')" class="action-btn outline" title="Обновить логи">🔄 Обновить</button>
        </div>
      </div>

      <div v-for="log in activeLogs" :key="log.id" class="log-entry" :class="log.role">
        <div class="log-meta">
          <span class="log-agent">{{ log.agent_name || log.role }}</span>
          <span class="log-time">{{ new Date(log.created_at).toLocaleTimeString() }}</span>
        </div>
        
        <div v-if="log.role === 'tool'" class="log-content tool-output" :class="{'approval-mode': log.pending_approval}" @mouseleave="activeLogMenuId = null">
          <div class="msg-menu-container">
            <button class="msg-menu-btn" @click.stop="activeLogMenuId = activeLogMenuId === log.id ? null : log.id">⋮</button>
            <div class="msg-menu-dropdown" v-if="activeLogMenuId === log.id">
              <button @click.stop="copyText(log.content, log.id); activeLogMenuId = null" class="msg-menu-item">
                <span v-if="copiedLogId === log.id">✅ Скопировано</span>
                <span v-else>📋 Копировать ответ</span>
              </button>
            </div>
          </div>

          <div class="tool-label">
            {{ log.agent_name || 'Вызов инструмента' }} 
            <span v-if="log.tool_call_id" style="opacity: 0.6; font-size: 10px; margin-left: 8px; font-weight: normal;">(ID: {{ log.tool_call_id }})</span>
          </div>
          
          <template v-if="!log.pending_approval">
              <template v-if="getPluginResultData(log.content)">
                  <component 
                      :is="resolveResultPlugin(getPluginResultData(log.content).plugin_name)"
                      :payload="getPluginResultData(log.content)"
                      :toolCallId="log.tool_call_id"
                      :taskId="activeTaskId"
                      @submit="handleSubmitTool"
                  />
              </template>
              <template v-else>
                  <div class="markdown-body" v-html="formatLogContent(log.content)"></div>
              </template>
          </template>
          <div v-else class="approval-panel">
             <template v-if="getPluginData(log.content)">
               <component 
                   :is="resolveApprovalPlugin(getPluginData(log.content).tool_name)" 
                   :payload="getPluginData(log.content)"
                   :toolCallId="log.tool_call_id"
                   @submit="handleSubmitTool"
                   @approve="(id, approved) => $emit('approve-tool', id, approved)"
                   @focus="(id) => activeToolInputId = id"
                   @blur="() => activeToolInputId = null"
               />
             </template>
          </div>
        </div>
        
        <div v-else class="log-content standard-text" @mouseleave="activeLogMenuId = null">
          <div class="msg-menu-container">
            <button class="msg-menu-btn" @click.stop="activeLogMenuId = activeLogMenuId === log.id ? null : log.id">⋮</button>
            <div class="msg-menu-dropdown" v-if="activeLogMenuId === log.id">
              <button @click.stop="copyText(log.content, log.id); activeLogMenuId = null" class="msg-menu-item">
                <span v-if="copiedLogId === log.id">✅ Скопировано</span>
                <span v-else>📋 Копировать текст</span>
              </button>
            </div>
          </div>

          <div class="markdown-body" v-html="formatLogContent(log.content)"></div>
        </div>
      </div>
      
      <div v-if="activeLogs.length === 0" class="empty-state-mini">
        Логи пусты. Задача только инициализирована.
      </div>
    </div>
    
    <div v-if="activeTask && ['completed', 'failed'].includes(activeTask.status)" class="continue-task-panel">
      <textarea 
        ref="continueInputRef"
        v-model="continuePrompt" 
        @keydown.enter.exact.prevent="handleContinueTask"
        @focus="isContinuePromptFocused = true"
        @blur="isContinuePromptFocused = false"
        @input="autoResize"
        class="modern-input custom-scrollbar" 
        placeholder="Задача остановлена. Напишите сюда, чтобы выдать новые указания и продолжить..."
        rows="1" 
      ></textarea>
      <button @click="handleContinueTask" class="action-btn primary" :disabled="!continuePrompt.trim()">Продолжить</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, defineAsyncComponent } from 'vue'
import { api } from '../../services/api'
import { appStore } from '../../stores/appStore'

const DefaultApproval = defineAsyncComponent(() => import('../plugins/DefaultApproval.vue'))
const AskUserApproval = defineAsyncComponent(() => import('../plugins/AskUserApproval.vue'))
const CodeApproval = defineAsyncComponent(() => import('../plugins/CodeApproval.vue'))

const props = defineProps({
  activeTaskId: Number,
  activeTask: Object,
  activeLogs: Array
});

const emit = defineEmits(['cancel', 'duplicate', 'refresh', 'continue', 'approve-tool', 'submit-tool']);

const logsContainer = ref(null)
const continuePrompt = ref('')
const continueInputRef = ref(null)
const toolInputs = ref({}) 
const copiedLogId = ref(null)
const activeLogMenuId = ref(null)
const isContinuePromptFocused = ref(false)
const activeToolInputId = ref(null)

const contextTokens = computed(() => {
  const textLength = props.activeLogs.reduce((acc, log) => acc + (log.content ? log.content.length : 0), 0);
  return Math.ceil(textLength / 4);
})

const copyText = async (text, id) => {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    copiedLogId.value = id;
    setTimeout(() => { if (copiedLogId.value === id) copiedLogId.value = null; }, 2000);
  } catch (err) {
    console.error('Ошибка копирования:', err);
  }
}

watch(continuePrompt, (newVal) => {
  if (!newVal && continueInputRef.value) {
    continueInputRef.value.style.height = 'auto'
  }
})

const autoResize = (event) => {
  const el = event.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

const resolveApprovalPlugin = (toolName) => {
    if (toolName === 'ask_user' || toolName === 'message_user') return AskUserApproval
    if (toolName === 'edit_file' || toolName === 'write_file') return CodeApproval
    return DefaultApproval
}

const resolveResultPlugin = (pluginName) => {
    return null
}

const getPluginData = (logContent) => {
    if (typeof logContent !== 'string' || !logContent.startsWith('{')) return null;
    try {
        const parsed = JSON.parse(logContent);
        if (parsed && parsed.is_plugin_request) return parsed;
    } catch (e) {}
    return null;
}

const getPluginResultData = (logContent) => {
    if (typeof logContent !== 'string' || !logContent.startsWith('{')) return null;
    try {
        const parsed = JSON.parse(logContent);
        if (parsed && parsed.is_plugin_result) return parsed;
    } catch (e) {}
    return null;
}

const openTaskIde = () => {
  if (!props.activeTask) return;
  appStore.openIde(props.activeTask.work_dir || '', '');
}

const handleContinueTask = () => {
  if (!continuePrompt.value.trim() || !props.activeTaskId) return;
  emit('continue', continuePrompt.value.trim());
  continuePrompt.value = '';
}

const handleCancel = () => {
  if (confirm("Принудительно остановить задачу? Процесс будет прерван.")) {
    emit('cancel');
  }
}

const handleSubmitTool = (tool_call_id, customPayload = null) => {
  let text = '';
  if (customPayload) {
      text = typeof customPayload === 'string' ? customPayload : JSON.stringify(customPayload);
  } else {
      text = toolInputs.value[tool_call_id] || '';
  }
  if (!text.trim()) return;
  
  emit('submit-tool', tool_call_id, text.trim());
  
  if (toolInputs.value[tool_call_id]) {
      delete toolInputs.value[tool_call_id];
  }
}

const downloadTaskContext = async () => {
  if (!props.activeTaskId) return;
  try {
    await api.downloadTaskContext(props.activeTaskId);
  } catch (e) {
    alert("Ошибка скачивания контекста");
  }
}

const downloadTaskDebug = async () => {
  if (!props.activeTaskId) return;
  try {
    await api.downloadTaskDebug(props.activeTaskId);
  } catch (e) {
    alert("Ошибка скачивания отладочных логов (возможно, их еще нет)");
  }
}

const processAuthImages = async () => {
  if (!logsContainer.value) return;
  const images = logsContainer.value.querySelectorAll('img.auth-image[data-auth-src]');
  for (let img of images) {
    const src = img.getAttribute('data-auth-src');
    if (src && !img.src.startsWith('blob:')) {
       try {
          const blobUrl = await api.getImageBlob(src);
          img.src = blobUrl;
          img.removeAttribute('data-auth-src');
       } catch (e) {
          console.error("Failed to load image", e);
       }
    }
  }
}

const sanitizeHtml = (str) => {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const formatLogContent = (text) => {
  if (!text) return '';
  let html = text.trim();
  
  if (html.startsWith('{') && html.endsWith('}')) {
    try {
      const parsed = JSON.parse(html);
      if (parsed.thoughts || parsed.plan) {
         let formatted = '';
         if (parsed.thoughts) {
             formatted += `<strong style="color: var(--accent-purple); font-size: 13px;">💭 Мысли:</strong> <span style="font-size: 14px;">${sanitizeHtml(parsed.thoughts)}</span><br>`;
         }
         if (parsed.plan) {
             formatted += `<strong style="color: var(--accent-blue); display: inline-block; margin-top: 8px; font-size: 13px;">📋 План выполнения:</strong><br><pre style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; font-size: 12px; font-family: 'Consolas', monospace; color: #a3b8cc; margin-top: 6px;">${sanitizeHtml(JSON.stringify(parsed.plan, null, 2))}</pre>`;
         }
         return formatted;
      }
    } catch(e) {}
  }

  // 1. Извлекаем блоки кода
  const codeBlocks = [];
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    codeBlocks.push(code);
    return `___CODEBLOCK_${codeBlocks.length - 1}___`;
  });
  html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
    codeBlocks.push(code);
    return `___CODEBLOCK_${codeBlocks.length - 1}___`;
  });

  html = sanitizeHtml(html);

  // 2. Жирный, Курсив, Инлайн-Код
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #e4e4e7;">$1</code>');

  // 3. Заголовки (Markdown)
  html = html.replace(/^### (.*$)/gim, '<h3 style="margin: 16px 0 8px; color: var(--accent-blue);">$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2 style="margin: 18px 0 10px; color: var(--accent-purple);">$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1 style="margin: 20px 0 12px; color: var(--text-main); font-size: 1.4em;">$1</h1>');

  // 4. Специфичные правила RITA (Кнопки)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img data-auth-src="$2" alt="$1" class="auth-image" style="max-width:100%; max-height:400px; border-radius:8px; display:block; margin:8px 0;" />');
  html = html.replace(/\[ФАЙЛ СОХРАНЕН\]:\s*(.+)/g, '<br><button class="action-btn outline editor-trigger mt-2" data-path="$1">📄 Открыть $1 в IDE</button>');
  html = html.replace(/\[ATTACHMENT\]\((.+?)\)/g, '<br><a href="$1" target="_blank" class="action-btn primary mt-2" style="display: inline-block; text-decoration: none;">⬇️ Скачать результат</a>');

  // 5. Списки
  html = html.replace(/^\s*[-*]\s+(.*)$/gim, '<li style="margin-left: 20px; list-style-type: disc; margin-bottom: 4px;">$1</li>');
  html = html.replace(/^\s*\d+\.\s+(.*)$/gim, '<li style="margin-left: 20px; list-style-type: decimal; margin-bottom: 4px;">$1</li>');

  // 6. Переносы строк (избегаем разрывов внутри списков и заголовков)
  html = html.split('\n').join('<br>');
  html = html.replace(/<\/h[1-3]><br>/g, (m) => m.replace('<br>', ''));
  html = html.replace(/<\/li><br>/g, '</li>');
  html = html.replace(/<br><li/g, '<li');

  // 7. Возвращаем блоки кода
  html = html.replace(/___CODEBLOCK_(\d+)___/g, (match, index) => {
    const code = sanitizeHtml(codeBlocks[index].trim());
    return `<div class="md-code-block" style="margin: 12px 0;"><div style="background: rgba(0,0,0,0.4); padding: 6px 12px; font-size: 11px; color: #8b8b9e; border-top-left-radius: 8px; border-top-right-radius: 8px; border: 1px solid var(--border-color); border-bottom: none; display: flex; justify-content: space-between; align-items: center;"><span>Код / Логи</span></div><pre style="margin: 0; background: #0d0d12; padding: 12px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; border: 1px solid var(--border-color); overflow-x: auto; font-family: 'Consolas', monospace; font-size: 13px; color: #a3b8cc; line-height: 1.4;">${code}</pre></div>`;
  });
  
  return html;
}

const handleLogClick = async (e) => {
  activeLogMenuId.value = null; // Закрытие меню при клике по области
  
  if (e.target.classList.contains('editor-trigger')) {
    const path = e.target.getAttribute('data-path')
    appStore.openIde('', path);
  } else if (e.target.tagName === 'A' && e.target.getAttribute('href')?.includes('/api/tools/fs/download')) {
    e.preventDefault();
    try {
      const urlStr = e.target.getAttribute('href');
      const url = new URL(urlStr, window.location.origin);
      const path = url.searchParams.get('path');
      if (path) await api.downloadAttachment(path);
    } catch(err) {
      console.error(err);
      alert("Ошибка скачивания файла");
    }
  }
}

let lastLogsLength = 0;
let forceNextScroll = false;

watch(() => props.activeTaskId, () => { 
  forceNextScroll = true; 
  lastLogsLength = 0; 
});

watch(() => props.activeLogs, (newLogs) => {
  const currentLength = newLogs ? newLogs.length : 0;
  const isNewMessage = currentLength > lastLogsLength;
  lastLogsLength = currentLength;

  scrollToBottom(forceNextScroll || isNewMessage);
  forceNextScroll = false;
  nextTick(processAuthImages);
}, { deep: true, flush: 'post' });

const scrollToBottom = (force = false) => {
  nextTick(() => {
    if (logsContainer.value) {
      const el = logsContainer.value;
      const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 150;
      if (force || isAtBottom) {
        el.scrollTo({
          top: el.scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  })
}

defineExpose({ scrollToBottom });
</script>

<style scoped>
.task-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
.empty-state { margin: auto; text-align: center; color: var(--text-muted); font-size: 14px; }
.empty-icon { font-size: 32px; margin-bottom: 12px; opacity: 0.6; }
.empty-state-mini { text-align: center; color: var(--text-muted); font-size: 13px; font-style: italic; padding: 20px; }

.logs-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }

.logs-header { 
  display: flex; justify-content: space-between; align-items: center; 
  border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 8px; 
  position: sticky; top: -24px; background: var(--bg-base); z-index: 10; padding-top: 24px; margin-top: -24px;
}
.logs-header h4 { margin: 0; color: var(--text-main); font-size: 14px; font-weight: 600; }
.context-volume { font-size: 11px; color: var(--accent-blue); background: rgba(64, 104, 148, 0.1); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(64, 104, 148, 0.3); align-self: flex-start; cursor: help;}

.log-entry { display: flex; flex-direction: column; gap: 6px; max-width: 90%; }
.log-entry.user { align-self: flex-end; }
.log-entry.assistant, .log-entry.system { align-self: flex-start; }
.log-entry.tool { align-self: flex-start; width: 100%; max-width: 100%; }

.log-meta { display: flex; gap: 8px; align-items: center; font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: bold; margin-left: 4px; margin-right: 4px; }
.user .log-meta { justify-content: flex-end; }
.log-agent { color: var(--accent-purple); }
.user .log-agent { color: var(--accent-blue); }

.log-content { position: relative; background: var(--bg-surface); padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border-color); font-size: 14px; color: var(--text-main); line-height: 1.5; white-space: pre-wrap; }
.user .log-content { background: var(--msg-user); border-color: rgba(64, 104, 148, 0.4); }
.assistant .log-content { background: var(--msg-rita); border-color: rgba(107, 76, 154, 0.4); }

.markdown-body { display: block; width: 100%; }

/* Всплывающее меню */
.msg-menu-container { position: absolute; top: 6px; right: 8px; z-index: 5; }
.msg-menu-btn { cursor: pointer; color: var(--text-muted); opacity: 0; transition: opacity 0.2s; font-size: 18px; line-height: 1; padding: 2px 8px; border-radius: 4px; background: transparent; border: none; font-weight: bold;}
.log-content:hover .msg-menu-btn { opacity: 1; }
.msg-menu-btn:hover { background: rgba(255,255,255,0.1); color: var(--text-main); }
.msg-menu-dropdown { position: absolute; top: 100%; right: 0; background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 6px; padding: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); min-width: 140px; margin-top: 4px; }
.msg-menu-item { display: flex; align-items: center; gap: 8px; width: 100%; padding: 8px 12px; background: transparent; border: none; color: var(--text-main); font-size: 13px; text-align: left; cursor: pointer; border-radius: 4px; transition: 0.2s; white-space: nowrap; }
.msg-menu-item:hover { background: var(--bg-surface-hover); color: var(--accent-blue); }

.tool-output { background: #0d0d12; border-color: rgba(163, 114, 50, 0.4); padding: 0; border-radius: 8px; }
.tool-output.approval-mode { border-color: var(--warning); border-width: 2px; }
.tool-label { background: rgba(163, 114, 50, 0.15); color: var(--warning); padding: 6px 12px; font-size: 12px; font-family: monospace; border-bottom: 1px solid rgba(163, 114, 50, 0.4); border-top-left-radius: 8px; border-top-right-radius: 8px; }

.approval-panel { padding: 16px; background: rgba(163, 114, 50, 0.05); }

.continue-task-panel { display: flex; align-items: flex-end; gap: 12px; padding: 16px 24px; border-top: 1px solid var(--border-color); background: var(--bg-panel); z-index: 10; }
.continue-task-panel .modern-input { flex: 1; resize: none; max-height: 150px; overflow-y: auto; font-family: inherit; line-height: 1.5; background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; outline: none; transition: 0.2s; }
.continue-task-panel .modern-input:focus { border-color: var(--accent-blue); }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
.action-btn.outline { border-color: var(--accent-blue); color: var(--accent-blue); }
.action-btn.outline:hover { background: rgba(64, 104, 148, 0.1); }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; height: 42px; }
.action-btn.primary:hover:not(:disabled) { background: var(--accent-blue-hover); }
.action-btn.primary:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.danger { background: rgba(255, 68, 68, 0.1); border-color: rgba(255, 68, 68, 0.3); color: #ff4444; }
.action-btn.danger:hover { background: rgba(255, 68, 68, 0.2); }
</style>
