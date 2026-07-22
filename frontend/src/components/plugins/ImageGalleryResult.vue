// frontend/src/components/plugins/ImageGalleryResult.vue
<template>
    <div class="plugin-image-gallery">
        <div class="gallery-grid">
            <div 
                v-for="(img, idx) in payload.data" :key="idx" 
                class="gallery-item"
                :class="{'selected': selectedUrls.includes(img.url)}"
                @click="toggleSelection(img.url)"
            >
                <img :src="img.url" :alt="img.title" />
                <div v-if="selectedUrls.includes(img.url)" class="check-icon">✓</div>
            </div>
        </div>
        <div class="gallery-actions">
            <button @click="downloadSelected" :disabled="!selectedUrls.length" class="action-btn outline">💾 Сохранить</button>
            <button @click="loadMore" class="action-btn outline">🔄 Найти еще 10</button>
            <button @click="continueWithSelected" :disabled="!selectedUrls.length" class="action-btn primary">➡️ Продолжить с выбранными</button>
            <button @click="sendToTelegram" :disabled="!selectedUrls.length" class="action-btn outline telegram-btn">✈️ В Telegram</button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { api } from '../../services/api';

const props = defineProps(['payload', 'toolCallId', 'taskId']);
const emit = defineEmits(['submit']);

const selectedUrls = ref([]);

const toggleSelection = (url) => {
    const idx = selectedUrls.value.indexOf(url);
    if (idx === -1) selectedUrls.value.push(url);
    else selectedUrls.value.splice(idx, 1);
};

const downloadSelected = async () => {
    for (const url of selectedUrls.value) {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const objUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = objUrl;
            a.download = url.split('/').pop() || 'image.jpg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(objUrl);
        } catch (e) {
            console.error("Ошибка скачивания", e);
        }
    }
};

const loadMore = () => {
    emit('submit', props.toolCallId, "Пользователь запрашивает еще 10 изображений по этому же запросу.");
};

const continueWithSelected = () => {
    emit('submit', props.toolCallId, `Пользователь выбрал следующие изображения:\n${selectedUrls.value.join('\n')}`);
};

const sendToTelegram = async () => {
    try {
        await api.sendDirectToTelegram({ task_id: props.taskId, urls: selectedUrls.value });
        alert("Изображения успешно отправлены в Telegram!");
    } catch (e) {
        alert("Ошибка отправки в Telegram. Проверьте настройки бота у агента.");
    }
};
</script>

<style scoped>
.plugin-image-gallery { padding: 12px; }
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px; }
.gallery-item { position: relative; border-radius: 8px; overflow: hidden; cursor: pointer; border: 2px solid transparent; transition: 0.2s; aspect-ratio: 1; background: rgba(0,0,0,0.2); }
.gallery-item img { width: 100%; height: 100%; object-fit: cover; }
.gallery-item:hover { border-color: rgba(107, 76, 154, 0.5); }
.gallery-item.selected { border-color: var(--accent-purple); box-shadow: 0 0 10px rgba(107,76,154,0.5); }
.check-icon { position: absolute; top: 8px; right: 8px; background: var(--accent-purple); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }
.gallery-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.action-btn { background: var(--bg-surface); color: var(--text-main); border: 1px solid var(--border-color); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn:hover:not(:disabled) { background: var(--bg-surface-hover); }
.action-btn.primary { background: var(--accent-blue); border-color: var(--accent-blue); color: #fff; }
.action-btn.primary:hover:not(:disabled) { background: var(--accent-blue-hover); }
.telegram-btn { color: #38bdf8; border-color: rgba(56, 189, 248, 0.4); }
.telegram-btn:hover:not(:disabled) { background: rgba(56, 189, 248, 0.1); border-color: #38bdf8; }
</style>
