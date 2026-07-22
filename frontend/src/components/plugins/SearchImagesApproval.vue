// frontend/src/components/plugins/SearchImagesApproval.vue
<template>
    <div class="plugin-search-approval">
        <p class="approval-text">{{ payload.message }}</p>
        <div style="margin: 10px 0;">
            <label style="font-size: 11px; color: var(--accent-purple); font-weight: bold; text-transform: uppercase;">Запрос поиска:</label>
            <textarea 
                v-model="editableQuery"
                class="modern-input custom-scrollbar"
                style="width: 100%; min-height: 60px; margin-top: 6px; resize: vertical;"
                @focus="$emit('focus', toolCallId)"
                @blur="$emit('blur')"
            ></textarea>
        </div>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button @click="handleApprove" class="action-btn primary">✅ Разрешить</button>
            <button @click="$emit('approve', toolCallId, false)" class="action-btn danger">❌ Отклонить</button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps(['payload', 'toolCallId']);
const emit = defineEmits(['approve', 'focus', 'blur']);

const editableQuery = ref(props.payload.args.query || '');

const handleApprove = () => {
    const result = {
        action: "modify_args",
        new_args: { query: editableQuery.value }
    };
    emit('approve', props.toolCallId, JSON.stringify(result));
}
</script>

<style scoped>
.approval-text { margin: 0; color: #e4e4e7; font-size: 14px; font-weight: 500; white-space: pre-wrap; line-height: 1.4; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.danger { background: rgba(255, 68, 68, 0.1); border-color: rgba(255, 68, 68, 0.3); color: #ff4444; }
.modern-input { background: var(--bg-base); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 14px; border-radius: 8px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; outline: none; box-sizing: border-box; }
</style>
