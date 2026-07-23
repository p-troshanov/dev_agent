// frontend/src/views/TasksView.vue
<template>
  <div class="tasks-container">
    <TasksSidebar 
      :tasks="tasks" 
      :activeTaskId="activeTaskId" 
      @select-task="selectTask" 
      @create-task="openCreateModal" 
    />
    
    <TaskLogsArea 
      ref="logsAreaRef"
      :activeTaskId="activeTaskId"
      :activeTask="activeTask"
      :activeLogs="activeLogs"
      @cancel="cancelTask"
      @duplicate="duplicateTask"
      @refresh="loadLogs(true)"
      @continue="handleContinueTask"
      @approve-tool="approveTool"
      @submit-tool="submitToolResponse"
      @next-phase="handleNextPhase"
      @rollback="handleRollback"
      @open-manual-tools="showManualModal = true"
    />
    
    <TaskCreateModal 
      :show="showModal"
      :agents="agents"
      :projects="projects"
      :initialData="initialModalData"
      @close="showModal = false"
      @submit="createTask"
    />

    <TaskManualToolsModal
      :show="showManualModal"
      :taskId="activeTaskId"
      @close="showManualModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../services/api'
import { appStore } from '../stores/appStore'

import TasksSidebar from '../components/tasks/TasksSidebar.vue'
import TaskLogsArea from '../components/tasks/TaskLogsArea.vue'
import TaskCreateModal from '../components/tasks/TaskCreateModal.vue'
import TaskManualToolsModal from '../components/tasks/TaskManualToolsModal.vue'

const tasks = ref([])
const agents = ref([])
const projects = ref([])
const activeTaskId = ref(null)
const activeLogs = ref([])

const showModal = ref(false)
const showManualModal = ref(false)
const initialModalData = ref({})
const logsAreaRef = ref(null)

const activeTask = computed(() => tasks.value.find(t => t.id === activeTaskId.value))

watch(() => activeTask.value?.title, (newTitle) => {
  document.title = newTitle ? `${newTitle} - RITA` : 'Задачи - RITA'
}, { immediate: true })

watch(() => appStore.taskUpdateTrigger, () => {
  fetchTasks()
  if (activeTaskId.value) loadLogs(false)
})

const fetchTasks = async () => {
  try {
    tasks.value = await api.getTasks()
  } catch (e) {
    console.error("Ошибка загрузки задач:", e)
  }
}

const fetchAgents = async () => {
  try {
    agents.value = await api.getAgents()
  } catch (e) {
    console.error("Ошибка загрузки агентов:", e)
  }
}

const fetchProjects = async () => {
  try {
    projects.value = await api.getProjects()
  } catch (e) {
    console.error("Ошибка загрузки проектов:", e)
  }
}

const openCreateModal = async () => {
  await fetchAgents()
  await fetchProjects()
  initialModalData.value = { 
    title: '', 
    initial_prompt: '', 
    agent_id: agents.value.length > 0 ? agents.value[0].id : null,
    project_id: projects.value.length > 0 ? projects.value[0].id : null,
    auto_approve_tools: false,
    type: 'standard',
    target_action: 'full_execution'
  }
  showModal.value = true
}

const duplicateTask = async () => {
  if (!activeTask.value) return;
  await fetchAgents();
  await fetchProjects();
  
  const t = activeTask.value;
  const firstUserLog = activeLogs.value.find(l => l.role === 'user');
  const prompt = firstUserLog ? firstUserLog.content : '';
  const proj = projects.value.find(p => p.name === t.project_name);
  const projId = proj ? proj.id : (projects.value.length > 0 ? projects.value[0].id : null);
  
  initialModalData.value = {
    title: t.title + ' (Копия)',
    initial_prompt: prompt,
    agent_id: t.agent_id,
    project_id: projId,
    auto_approve_tools: !!t.auto_approve_tools,
    type: t.type || 'standard',
    target_action: t.target_action || 'full_execution'
  };
  showModal.value = true;
}

const createTask = async (formData) => {
  if (!formData.title.trim() || !formData.initial_prompt.trim()) {
    return alert("Название и ТЗ обязательны!")
  }
  if (!formData.agent_id) {
    return alert("Необходимо выбрать агента для выполнения задачи!")
  }
  if (!formData.project_id) {
    return alert("Необходимо выбрать проект для задачи!")
  }
  
  try {
    const res = await api.createTask(formData)
    showModal.value = false
    await fetchTasks()
    selectTask(res.id)
  } catch (e) {
    console.error("Ошибка создания задачи:", e)
  }
}

const handleContinueTask = async (promptText) => {
  if (!activeTaskId.value) return;
  try {
    await api.continueTask(activeTaskId.value, promptText);
    await fetchTasks();
    await loadLogs(true);
  } catch (e) {
    console.error("Ошибка при продолжении задачи:", e);
    alert("Не удалось продолжить задачу");
  }
}

const handleNextPhase = async (phase) => {
  if (!activeTaskId.value) return;
  try {
    await api.nextTaskPhase(activeTaskId.value, phase);
    await api.continueTask(activeTaskId.value, `Одобрено. Переходим в фазу: ${phase.toUpperCase()}. Действуй согласно инструкциям текущей фазы.`);
    await fetchTasks();
    await loadLogs(true);
  } catch (e) {
    console.error("Ошибка переключения фазы:", e);
  }
}

const handleRollback = async () => {
  if (!activeTaskId.value) return;
  if (!confirm("Вы уверены, что хотите откатить все изменения, сделанные агентом в этой задаче? Текущие файлы будут заменены версиями из бекапа задачи.")) return;
  
  try {
    const res = await api.rollbackTask(activeTaskId.value);
    alert(res.message || "Откат инициирован");
    await loadLogs(true);
  } catch (e) {
    console.error("Ошибка отката:", e);
    alert("Произошла ошибка при откате");
  }
}

const cancelTask = async () => {
  if (!activeTaskId.value) return;
  const currentTask = tasks.value.find(t => t.id === activeTaskId.value);
  if (currentTask) currentTask.status = 'failed';
  try {
    await api.cancelTask(activeTaskId.value);
    await fetchTasks();
    await loadLogs(true);
  } catch (e) { console.error("Ошибка при остановке:", e) }
}

const approveTool = async (tool_call_id, approved) => {
  if (!activeTaskId.value) return;
  const currentTask = tasks.value.find(t => t.id === activeTaskId.value);
  if (currentTask) currentTask.status = 'running';
  try {
    await api.approveTaskTool(activeTaskId.value, tool_call_id, approved);
    await loadLogs(true);
  } catch (e) { console.error("Ошибка подтверждения тулзы:", e) }
}

const submitToolResponse = async (tool_call_id, text) => {
  if (!activeTaskId.value) return;
  const currentTask = tasks.value.find(t => t.id === activeTaskId.value);
  if (currentTask) currentTask.status = 'running';
  try {
    await api.submitTaskToolResponse(activeTaskId.value, tool_call_id, text);
    await loadLogs(true);
  } catch (e) { 
    console.error("Ошибка отправки ответа:", e) 
  }
}

const selectTask = async (id) => {
  activeTaskId.value = id
  await loadLogs(true)
}

const loadLogs = async (forceScroll = false) => {
  if (!activeTaskId.value) return
  try {
    activeLogs.value = await api.getTaskLogs(activeTaskId.value)
    if (forceScroll && logsAreaRef.value) {
      logsAreaRef.value.scrollToBottom(true);
    }
  } catch (e) {
    console.error("Ошибка загрузки логов:", e)
  }
}

onMounted(() => {
  fetchTasks()
  setInterval(() => {
    if (activeTaskId.value) loadLogs(false)
    fetchTasks()
  }, 5000)
})
</script>

<style scoped>
.tasks-container { display: flex; height: 100%; overflow: hidden; background: var(--bg-base); }
</style>
