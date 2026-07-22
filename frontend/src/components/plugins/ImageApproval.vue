// frontend/src/components/plugins/ImageApproval.vue
<template>
    <div class="plugin-image-approval">
        <p class="approval-text">{{ payload.message }}</p>
        <div style="background: rgba(0,0,0,0.2); padding: 12px; margin: 12px 0; border-radius: 8px; border: 1px solid var(--border-color);">
            <strong style="color: var(--accent-purple); font-size: 12px; text-transform: uppercase;">Промпт для изображения:</strong>
            <div style="margin-top: 6px; font-size: 14px; color: #fff;">{{ payload.args.prompt }}</div>
        </div>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button @click="$emit('approve', toolCallId, true)" class="action-btn primary">✅ Сгенерировать</button>
            <button @click="$emit('approve', toolCallId, false)" class="action-btn danger">❌ Отменить</button>
        </div>
    </div>
</template>

<script setup>
defineProps(['payload', 'toolCallId']);
defineEmits(['approve']);
</script>

<style scoped>
.approval-text { margin: 0; color: #e4e4e7; font-size: 14px; font-weight: 500; white-space: pre-wrap; line-height: 1.4; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.danger { background: rgba(255, 68, 68, 0.1); border-color: rgba(255, 68, 68, 0.3); color: #ff4444; }
</style>
