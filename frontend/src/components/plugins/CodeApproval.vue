// frontend/src/components/plugins/CodeApproval.vue
<template>
    <div class="plugin-code-approval">
        <p class="approval-text">
            Агент хочет 
            <strong v-if="payload.tool_name === 'edit_file'">изменить кусок кода в файле:</strong>
            <strong v-else>перезаписать/создать файл:</strong>
            <span style="color: var(--accent-blue);"> {{ payload.args.path }}</span>
        </p>
        
        <div v-if="loading" class="loading-state">Загрузка текущего файла с сервера...</div>
        <div v-else class="diff-view">
            <div class="code-pane">
                <div class="pane-title">Было (оригинал)</div>
                <pre class="custom-scrollbar">{{ oldCode }}</pre>
            </div>
            <div class="code-pane">
                <div class="pane-title">Станет (после применения)</div>
                <pre class="custom-scrollbar">{{ newCode }}</pre>
            </div>
        </div>

        <div class="actions" style="margin-top: 12px; display: flex; gap: 8px;">
            <button @click="$emit('approve', toolCallId, true)" class="action-btn primary" :disabled="loading">💾 Применить изменения</button>
            <button @click="$emit('approve', toolCallId, false)" class="action-btn danger" :disabled="loading">❌ Отклонить</button>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../../services/api';

const props = defineProps(['payload', 'toolCallId']);
const emit = defineEmits(['approve']);

const loading = ref(true);
const oldCode = ref('');
const newCode = ref('');

onMounted(async () => {
    try {
        const res = await api.readFile(props.payload.args.path);
        oldCode.value = res.content || '';
    } catch (e) {
        oldCode.value = '// Файл не существует на диске (будет создан) или недоступен для чтения.';
    }

    if (props.payload.tool_name === 'write_file') {
        newCode.value = props.payload.args.content || '';
    } else if (props.payload.tool_name === 'edit_file') {
        const search = props.payload.args.search_string || '';
        const replace = props.payload.args.replace_string || '';
        
        if (search && oldCode.value.includes(search)) {
            newCode.value = oldCode.value.replace(search, replace);
        } else {
            newCode.value = '// ОШИБКА: Искомая строка для замены (search_string) не найдена в оригинальном файле. Агент ошибся с отступами или текстом.';
        }
    }
    
    loading.value = false;
});
</script>

<style scoped>
.approval-text { margin: 0 0 10px 0; color: #e4e4e7; font-size: 14px; }
.diff-view { display: flex; gap: 10px; margin-top: 10px; height: 350px; }
.code-pane { flex: 1; display: flex; flex-direction: column; border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden; }
.pane-title { background: var(--bg-surface); padding: 6px 10px; font-size: 12px; font-weight: bold; color: var(--text-muted); border-bottom: 1px solid var(--border-color); }
.code-pane pre { flex: 1; margin: 0; padding: 12px; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; color: #a3b8cc; overflow: auto; white-space: pre; background: #0d0d12; line-height: 1.4; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: 0.2s; }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.danger { background: rgba(255, 68, 68, 0.1); border-color: rgba(255, 68, 68, 0.3); color: #ff4444; }
.action-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
