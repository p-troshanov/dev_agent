// frontend/src/components/plugins/DefaultApproval.vue
<template>
    <div class="plugin-default-approval">
        <p class="approval-text" v-html="formatLogContent(payload.message)"></p>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button @click="$emit('approve', toolCallId, true)" class="action-btn primary">✅ Разрешить</button>
            <button @click="$emit('approve', toolCallId, false)" class="action-btn danger">❌ Отклонить</button>
        </div>
    </div>
</template>

<script setup>
defineProps(['payload', 'toolCallId']);
defineEmits(['approve']);

const formatLogContent = (str) => {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};
</script>

<style scoped>
.approval-text { margin: 0; color: #e4e4e7; font-size: 14px; font-weight: 500; white-space: pre-wrap; line-height: 1.4; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.danger { background: rgba(255, 68, 68, 0.1); border-color: rgba(255, 68, 68, 0.3); color: #ff4444; }
</style>
