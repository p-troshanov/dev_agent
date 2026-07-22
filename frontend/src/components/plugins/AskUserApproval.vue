// frontend/src/components/plugins/AskUserApproval.vue
<template>
    <div class="plugin-ask-user">
        <p class="approval-text" v-html="formatLogContent(payload.message)"></p>
        <div style="display: flex; gap: 10px; margin-top: 10px; align-items: flex-end;">
            <textarea 
                v-model="text"
                class="modern-input custom-scrollbar"
                style="flex: 1; resize: none; max-height: 150px; overflow-y: auto; font-family: inherit; line-height: 1.5;"
                placeholder="Напишите ваш ответ агенту..."
                rows="1"
                @input="autoResize"
                @focus="$emit('focus', toolCallId)"
                @blur="$emit('blur')"
                @keydown.enter.exact.prevent="handleSubmit"
            ></textarea>
            <button @click="handleSubmit" class="action-btn primary" style="height: 42px;" :disabled="!text.trim()">Ответить</button>
            <button @click="$emit('approve', toolCallId, false)" class="action-btn danger" style="height: 42px;">Прервать</button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
const props = defineProps(['payload', 'toolCallId']);
const emit = defineEmits(['submit', 'approve', 'focus', 'blur']);

const text = ref('');

const formatLogContent = (str) => {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};

const autoResize = (event) => {
    const el = event.target;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
};

const handleSubmit = () => {
    if (text.value.trim()) emit('submit', props.toolCallId, text.value);
};
</script>

<style scoped>
.approval-text { margin: 0; color: #e4e4e7; font-size: 14px; font-weight: 500; white-space: pre-wrap; line-height: 1.4; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.danger { background: rgba(255, 68, 68, 0.1); border-color: rgba(255, 68, 68, 0.3); color: #ff4444; }
.modern-input { background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; outline: none; }
</style>
