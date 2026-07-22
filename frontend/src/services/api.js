// frontend/src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export function getToken() {
  return localStorage.getItem('rita_token');
}

async function request(endpoint, method = 'GET', body = null) {
  const options = { method, headers: {} };
  const token = getToken();
  
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  
  if (body) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  
  if (res.status === 401) {
    localStorage.removeItem('rita_token');
    window.location.href = '/auth';
  }
  
  if (!res.ok) {
    let errText = await res.text();
    if (res.status === 413 || errText.includes('413 Request Entity Too Large')) {
        errText = "Файл слишком большой для сервера (Nginx 413 Request Entity Too Large). Увеличьте client_max_body_size в настройках Nginx.";
    }
    throw new Error(`API Error: ${res.status} - ${errText}`);
  }
  
  const text = await res.text();
  return text ? JSON.parse(text) : {};
}

async function downloadFile(endpoint, filename) {
  const token = getToken();
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!res.ok) throw new Error('Download failed');
  
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'download';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export const api = {
  login: (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    }).then(async r => {
      if (!r.ok) throw new Error(await r.text());
      return r.json();
    });
  },
  register: (username, password) => request('/auth/register', 'POST', { username, password }),
  getMe: () => request('/auth/me'),

  getSettings: () => request('/settings'),
  updateSettings: (data) => request('/settings', 'POST', data),
  
  getAgents: () => request('/agents'),
  createAgent: (data) => request('/agents', 'POST', data),
  updateAgent: (id, data) => request(`/agents/${id}`, 'PUT', data),
  deleteAgent: (id) => request(`/agents/${id}`, 'DELETE'),
  
  getTools: () => request('/tools'),
  updateTool: (id, data) => request(`/tools/${id}`, 'PUT', data),
  directGenerateImage: (prompt) => request('/tools/direct/generate_image', 'POST', { prompt }),
  directGenerateVideo: (prompt, imagePath, durationSeconds) => request('/tools/direct/generate_video', 'POST', { prompt, image_path: imagePath, duration_seconds: durationSeconds }),
  checkVideoStatus: (jobId) => request(`/tools/direct/generate_video/status/${jobId}`),
  
  getProjects: () => request('/projects'),
  createProject: (data) => request('/projects', 'POST', data),
  updateProject: (id, data) => request(`/projects/${id}`, 'PUT', data),
  deleteProject: (id) => request(`/projects/${id}`, 'DELETE'),
  resetProjectWebhook: (id) => request(`/projects/${id}/reset_webhook`, 'POST'),

  getTasks: () => request('/tasks'),
  createTask: (data) => request('/tasks', 'POST', data),
  getTaskLogs: (id) => request(`/tasks/${id}/logs`),
  cancelTask: (id) => request(`/tasks/${id}/cancel`, 'POST'),
  approveTaskTool: (id, tool_call_id, approved) => request(`/tasks/${id}/approve_tool`, 'POST', { tool_call_id, approved }),
  submitTaskToolResponse: (id, tool_call_id, response_text) => request(`/tasks/${id}/submit_tool_response`, 'POST', { tool_call_id, response_text }),
  continueTask: (id, prompt) => request(`/tasks/${id}/continue`, 'POST', { prompt }),

  getKeys: () => request('/keys'),
  addKey: (data) => request('/keys', 'POST', data),
  deleteKey: (id) => request(`/keys/${id}`, 'DELETE'),
  getKeysStatus: () => request('/keys/status'),
  getKeyBalances: () => request('/keys/balances'),
  
  getStatistics: () => request('/statistics'),
  getAggregatedStatistics: (period, groupBy) => request(`/statistics/aggregated?period=${period}&group_by=${groupBy}`),

  readFile: (path) => request(`/tools/fs/read?path=${encodeURIComponent(path)}`),
  writeFile: (path, content) => request('/tools/fs/write', 'POST', { path, content }),
  listFs: (path) => request(`/tools/fs/list?path=${encodeURIComponent(path || '')}`),
  deleteFs: (path) => request(`/tools/fs/delete?path=${encodeURIComponent(path)}`, 'DELETE'),
  renameFs: (oldPath, newPath) => request('/tools/fs/rename', 'POST', { old_path: oldPath, new_path: newPath }),
  mkdirFs: (path) => request('/tools/fs/mkdir', 'POST', { path, content: '' }),
  sendDirectToTelegram: (data) => request('/tools/telegram_direct', 'POST', data),
  
  uploadFs: async (path, file) => {
    const token = getToken();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', path || '');
    
    const res = await fetch(`${API_BASE}/tools/fs/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    if (!res.ok) {
      let errText = await res.text();
      if (res.status === 413 || errText.includes('413 Request Entity Too Large')) {
          errText = "Файл превышает лимит вашего сервера. Увеличьте client_max_body_size в настройках Nginx.";
      }
      throw new Error(`${res.status} - ${errText}`);
    }
    return res.json();
  },

  getImageBlob: async (url) => {
    const token = getToken();
    const fetchUrl = url.startsWith('/api') ? `${API_BASE}${url.replace(/^\/api/, '')}` : url;
    const res = await fetch(fetchUrl, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Blob fetch failed'); 
    const blob = await res.blob();
    return window.URL.createObjectURL(blob);
  },

  downloadTaskContext: (id) => downloadFile(`/tasks/${id}/context_export`, `task_context_${id}.json`),
  downloadTaskDebug: (id) => downloadFile(`/tasks/${id}/debug_export`, `task_debug_${id}.zip`),
  downloadAttachment: (path) => downloadFile(`/tools/fs/download?path=${encodeURIComponent(path)}`, path.split('/').pop())
};
