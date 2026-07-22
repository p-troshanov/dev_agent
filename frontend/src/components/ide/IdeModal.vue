// frontend/src/components/ide/IdeModal.vue
<template>
  <div class="modal-overlay ide-overlay" @click.self="closeIde">
    <div class="ide-container" :class="{'drag-active': isDragging}"
         @dragover.prevent="isDragging = true"
         @dragenter.prevent="isDragging = true"
         @dragleave.prevent="isDragging = false"
         @drop.prevent="onDropFiles">
         
      <div v-if="isDragging" class="ide-drag-overlay">
        <span>Отпустите файлы для загрузки в текущую папку</span>
      </div>

      <div class="ide-sidebar">
          <div class="ide-toolbar">
            <button @click="ideGoUp" :disabled="!ideCurrentFolder" title="На уровень вверх">⬆️</button>
            <button @click="ideRefresh" title="Обновить дерево">🔄</button>
            <button @click="ideNewFile" title="Создать файл">📄</button>
            <button @click="ideNewFolder" title="Создать папку">📁</button>
            <button @click="triggerUpload" title="Загрузить файл">📤</button>
            <input type="file" ref="fileUploadInput" multiple @change="ideUploadFiles" style="display: none;" />
          </div>
          <div class="ide-path" :title="displayIdePath(ideCurrentFolder)">{{ displayIdePath(ideCurrentFolder) }}</div>
          <div class="ide-file-list custom-scrollbar">
            <div v-if="ideIsLoading" class="ide-empty-state" style="padding-top:20px;">Загрузка...</div>
            <div v-for="item in ideFiles" :key="item.path" class="ide-file-item" @click="ideItemClick(item)">
                <span v-if="item.is_dir">📁</span>
                <span v-else>📄</span>
                <span class="file-name" :title="item.name">{{ item.name }}</span>
                <div class="file-actions">
                  <button class="icon-btn copy-btn" @click.stop="ideCopyPath(item)" title="Копировать путь">📋</button>
                  <button class="icon-btn rename-btn" @click.stop="ideRename(item)" title="Переименовать">✏️</button>
                  <button v-if="!item.is_dir" class="icon-btn download-btn" @click.stop="ideDownload(item)" title="Скачать файл">📥</button>
                  <button class="icon-btn delete-btn" @click.stop="ideDelete(item)" title="Удалить">✖</button>
                </div>
            </div>
            <div v-if="!ideIsLoading && ideFiles.length === 0" class="ide-empty-state" style="padding-top:20px;">Пустая папка</div>
          </div>
      </div>
      <div class="ide-editor-area">
          <div class="ide-editor-header">
            <span class="ide-active-file">{{ ideSelectedFilePath ? displayIdePath(ideSelectedFilePath) : 'Выберите файл в меню слева' }}</span>
            <div style="display: flex; gap: 12px;">
                <button v-if="ideSelectedFilePath" @click="ideSaveFile" class="action-btn primary">💾 Сохранить изменения</button>
                <button class="icon-btn close-ide-btn" @click="closeIde">✖</button>
            </div>
          </div>
          <textarea v-if="ideSelectedFilePath" v-model="ideEditorContent" class="code-editor custom-scrollbar" spellcheck="false"></textarea>
          <div v-else class="ide-empty-state">Для начала работы выберите или создайте файл.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { appStore } from '../../stores/appStore'
import { api } from '../../services/api'

const ideFiles = ref([])
const ideCurrentFolder = ref('')
const ideSelectedFilePath = ref('')
const ideEditorContent = ref('')
const ideIsLoading = ref(false)
const isDragging = ref(false)
const fileUploadInput = ref(null)

const displayIdePath = (path) => {
  const uid = appStore.currentUser?.id || 1;
  const prefix = `/workspace/user_${uid}`;
  let p = path || '';
  if (p.startsWith(prefix)) return p;
  if (p.startsWith('/')) p = p.substring(1);
  return `${prefix}/${p}`;
}

const closeIde = () => {
  appStore.closeIde()
}

const ideRefresh = async () => {
  try {
    ideIsLoading.value = true;
    const res = await api.listFs(ideCurrentFolder.value);
    ideFiles.value = Array.isArray(res) ? res : (res.items || []);
  } catch (e) {
    console.error("FS List error:", e);
    alert("Ошибка чтения директории");
  } finally {
    ideIsLoading.value = false;
  }
}

const ideGoUp = () => {
  if (!ideCurrentFolder.value) return;
  const parts = ideCurrentFolder.value.split(/[/\\]/);
  parts.pop();
  ideCurrentFolder.value = parts.join('/');
  ideRefresh();
}

const ideItemClick = async (item) => {
  if (item.is_dir) {
    ideCurrentFolder.value = item.path;
    ideRefresh();
  } else {
    try {
      const res = await api.readFile(item.path);
      ideEditorContent.value = res.content || '';
      ideSelectedFilePath.value = item.path;
    } catch (e) {
      alert("Ошибка чтения файла");
    }
  }
}

const ideSaveFile = async () => {
  if (!ideSelectedFilePath.value) return;
  try {
    await api.writeFile(ideSelectedFilePath.value, ideEditorContent.value);
    alert("Файл сохранен!");
  } catch(e) {
    alert("Ошибка сохранения");
  }
}

const ideNewFile = () => {
  const name = prompt("Имя нового файла (можно с путем):");
  if (!name) return;
  const newPath = ideCurrentFolder.value ? `${ideCurrentFolder.value}/${name}` : name;
  ideSelectedFilePath.value = newPath;
  ideEditorContent.value = '';
}

const ideNewFolder = async () => {
  const name = prompt("Имя новой папки:");
  if (!name) return;
  const newPath = ideCurrentFolder.value ? `${ideCurrentFolder.value}/${name}` : name;
  try {
    await api.mkdirFs(newPath);
    ideRefresh();
  } catch(e) {
    alert("Ошибка создания папки");
  }
}

const ideDelete = async (item) => {
  if (!confirm(`Удалить ${item.name}?`)) return;
  try {
    await api.deleteFs(item.path);
    if (ideSelectedFilePath.value === item.path) {
      ideSelectedFilePath.value = '';
      ideEditorContent.value = '';
    }
    ideRefresh();
  } catch(e) {
    alert("Ошибка удаления");
  }
}

const ideRename = async (item) => {
  const newName = prompt(`Переименовать ${item.name} в:`, item.name);
  if (!newName || newName === item.name) return;
  
  const oldPath = item.path;
  const parts = oldPath.split(/[/\\]/);
  parts.pop(); // Удаляем старое имя файла
  const parentDir = parts.join('/');
  
  const newPath = parentDir ? `${parentDir}/${newName}` : newName;
  
  try {
    await api.renameFs(oldPath, newPath);
    // Если переименован открытый в данный момент файл, обновляем его путь
    if (ideSelectedFilePath.value === oldPath) {
      ideSelectedFilePath.value = newPath;
    }
    ideRefresh();
  } catch(e) {
    console.error("Rename error:", e);
    alert("Ошибка переименования: " + (e.message || e));
  }
}

const triggerUpload = () => {
  if (fileUploadInput.value) fileUploadInput.value.click();
}

const processUploadFiles = async (files) => {
  if (!files || files.length === 0) return;
  
  ideIsLoading.value = true;
  let uploadedPaths = [];
  try {
    for (let i = 0; i < files.length; i++) {
      await api.uploadFs(ideCurrentFolder.value, files[i]);
      const newPath = ideCurrentFolder.value ? `${ideCurrentFolder.value}/${files[i].name}` : files[i].name;
      uploadedPaths.push(displayIdePath(newPath));
    }
    
    const pathsText = uploadedPaths.join('\n');
    try {
      await navigator.clipboard.writeText(pathsText);
      alert("Файлы успешно загружены!\nПуть скопирован в буфер обмена:\n" + pathsText);
    } catch(clipErr) {
      alert("Файлы успешно загружены!\n(К сожалению, браузер не позволил автоматически скопировать путь в буфер обмена)");
    }
    
    await ideRefresh();
  } catch(err) {
    console.error("Upload error:", err);
    alert("Ошибка загрузки файла: " + (err.message || err) + "\n(Если файл большой, сервер мог закрыть соединение по таймауту, но файл всё равно был сохранён на диск)");
  } finally {
    if (fileUploadInput.value) fileUploadInput.value.value = '';
    ideIsLoading.value = false;
    isDragging.value = false;
  }
}

const ideUploadFiles = (e) => {
  processUploadFiles(e.target.files);
}

const onDropFiles = (e) => {
  isDragging.value = false;
  if (e.dataTransfer && e.dataTransfer.files) {
    processUploadFiles(e.dataTransfer.files);
  }
}

const ideCopyPath = async (item) => {
  try {
    const fullPath = displayIdePath(item.path);
    await navigator.clipboard.writeText(fullPath);
    alert("Путь скопирован:\n" + fullPath);
  } catch(e) {
    console.error(e);
  }
}

const ideDownload = async (item) => {
  try {
    await api.downloadAttachment(item.path);
  } catch(e) {
    console.error(e);
    alert("Ошибка скачивания файла");
  }
}

watch(() => appStore.isIdeOpen, async (isOpen) => {
  if (isOpen) {
    ideCurrentFolder.value = appStore.ideConfig.folder || '';
    ideSelectedFilePath.value = appStore.ideConfig.path || '';
    ideEditorContent.value = '';

    if (ideSelectedFilePath.value) {
      try {
        const res = await api.readFile(ideSelectedFilePath.value);
        ideEditorContent.value = res.content || '';
        const parts = ideSelectedFilePath.value.split('/');
        parts.pop();
        ideCurrentFolder.value = parts.join('/');
      } catch (e) {
        alert("Не удалось прочитать файл. Возможно его нет на диске бэкенда.");
      }
    }
    await ideRefresh();
  }
}, { immediate: true });
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(2px); }
.ide-overlay { display: flex; padding: 24px; align-items: stretch; justify-content: stretch; }
.ide-container { flex: 1; display: flex; background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.5); position: relative; }

.ide-container.drag-active > *:not(.ide-drag-overlay) {
  pointer-events: none;
}

.ide-drag-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(64, 104, 148, 0.85);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: bold;
  backdrop-filter: blur(4px);
  pointer-events: none;
  border: 4px dashed rgba(255,255,255,0.5);
  border-radius: 12px;
}

.ide-sidebar { width: 280px; background: var(--bg-surface); display: flex; flex-direction: column; border-right: 1px solid var(--border-color); }
.ide-toolbar { padding: 12px; display: flex; gap: 8px; border-bottom: 1px solid var(--border-color); }
.ide-toolbar button { background: var(--bg-panel); border: 1px solid var(--border-color); color: var(--text-main); border-radius: 6px; padding: 6px 10px; cursor: pointer; transition: 0.2s; flex: 1;}
.ide-toolbar button:hover:not(:disabled) { background: var(--accent-blue); color: white; border-color: var(--accent-blue); }
.ide-toolbar button:disabled { opacity: 0.5; cursor: not-allowed; }
.ide-path { padding: 8px 12px; font-size: 11px; font-family: monospace; color: var(--accent-blue); border-bottom: 1px solid var(--border-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ide-file-list { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 2px;}
.ide-file-item { display: flex; align-items: center; gap: 8px; padding: 8px; cursor: pointer; border-radius: 6px; font-size: 13px; color: var(--text-main); }
.ide-file-item:hover { background: rgba(255,255,255,0.05); }
.ide-file-item .file-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.ide-file-item .file-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
.ide-file-item:hover .file-actions { opacity: 1; }
.ide-file-item .icon-btn { background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; transition: 0.2s; }
.ide-file-item .icon-btn:hover { color: var(--text-main); background: rgba(255,255,255,0.1); }
.ide-file-item .delete-btn:hover { color: #ff4444; background: rgba(255, 68, 68, 0.1); }
.ide-file-item .copy-btn:hover { color: var(--accent-blue); background: rgba(64, 104, 148, 0.15); }
.ide-file-item .rename-btn:hover { color: var(--accent-blue); background: rgba(64, 104, 148, 0.15); }
.ide-file-item .download-btn:hover { color: var(--success); background: rgba(58, 122, 80, 0.15); }

.ide-editor-area { flex: 1; display: flex; flex-direction: column; background: #0d0d12; }
.ide-editor-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid var(--border-color); background: var(--bg-panel); }
.ide-active-file { font-family: monospace; color: var(--text-main); font-size: 13px; font-weight: bold; }
.ide-empty-state { flex: 1; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 14px; text-align: center; }
.close-ide-btn { font-size: 16px; color: var(--text-muted); cursor: pointer; background: transparent; border: none; }
.close-ide-btn:hover { color: #ff4444; }
.code-editor { flex: 1; background: transparent; color: #a3b8cc; font-family: 'Consolas', 'Monaco', monospace; font-size: 14px; border: none; padding: 16px; outline: none; resize: none; line-height: 1.5; white-space: pre; }
</style>
