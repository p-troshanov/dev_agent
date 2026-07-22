// frontend/src/stores/appStore.js
import { reactive } from 'vue';
import { api, getToken } from '../services/api';

export const appStore = reactive({
  settings: {},
  isConnected: false,
  taskUpdateTrigger: 0,
  router: null,
  pendingTools: [],
  currentUser: null,
  
  // IDE (Облако) состояние
  isIdeOpen: false,
  ideConfig: { folder: '', path: '' },
  
  async init() {
    if (!getToken()) return;
    try {
      this.currentUser = await api.getMe();
      this.settings = await api.getSettings();
      this.connectWebSocket();
    } catch (e) {
      console.error("Failed to init appStore:", e);
    }
  },

  logout() {
    localStorage.removeItem('rita_token');
    this.currentUser = null;
    this.isConnected = false;
    if (this.router) this.router.push('/auth');
  },

  openIde(folder = '', path = '') {
    this.ideConfig = { folder, path };
    this.isIdeOpen = true;
  },

  closeIde() {
    this.isIdeOpen = false;
  },

  connectWebSocket() {
    const token = getToken();
    if (!token) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/frontend?token=${encodeURIComponent(token)}`;
    
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => { this.isConnected = true; };
    ws.onclose = () => {
      this.isConnected = false;
      setTimeout(() => {
        if (getToken()) this.connectWebSocket();
      }, 3000);
    };
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'TASK_UPDATED') this.taskUpdateTrigger++; 
      
      if (data.type === 'TOOL_CONFIRMATION') {
        this.pendingTools.push({
          call_id: data.call_id,
          agent_name: data.agent_name,
          function_name: data.function_name,
          arguments: data.arguments
        });
      }
      
      if (data.type === 'NAVIGATE') {
        if (data.route && this.router) this.router.push(data.route);
      } 
    };
  }
});
