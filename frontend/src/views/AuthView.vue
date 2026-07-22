// frontend/src/views/AuthView.vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="brand-title">RITA <span>Core</span></h1>
      <div class="auth-tabs">
        <button :class="{ active: isLogin }" @click="isLogin = true">Вход</button>
        <button :class="{ active: !isLogin }" @click="isLogin = false">Регистрация</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label>Логин</label>
          <input type="text" v-model="username" class="modern-input" required />
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input type="password" v-model="password" class="modern-input" required />
        </div>
        
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        
        <button type="submit" class="action-btn primary w-100" :disabled="loading">
          {{ loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../services/api';
import { appStore } from '../stores/appStore';

const router = useRouter();
const isLogin = ref(true);
const username = ref('');
const password = ref('');
const errorMsg = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  errorMsg.value = '';
  loading.value = true;
  try {
    let res;
    if (isLogin.value) {
      res = await api.login(username.value, password.value);
    } else {
      res = await api.register(username.value, password.value);
    }
    localStorage.setItem('rita_token', res.access_token);
    await appStore.init();
    router.push('/');
  } catch (e) {
    errorMsg.value = "Ошибка: " + e.message;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-base);
}
.auth-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.brand-title {
  font-size: 24px;
  margin: 0 0 24px 0;
  text-align: center;
  color: var(--text-main);
  font-weight: 600;
}
.brand-title span { color: var(--accent-purple); }
.auth-tabs {
  display: flex;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}
.auth-tabs button {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: 0.2s;
}
.auth-tabs button.active {
  color: var(--accent-blue);
  border-bottom: 2px solid var(--accent-blue);
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
}
.modern-input {
  background: var(--bg-base);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.modern-input:focus {
  border-color: var(--accent-blue);
}
.w-100 {
  width: 100%;
  height: 48px;
  font-size: 15px;
}
.error-msg {
  color: #ff4444;
  font-size: 13px;
  text-align: center;
  background: rgba(255, 68, 68, 0.1);
  padding: 8px;
  border-radius: 4px;
}
.action-btn.primary {
  background: var(--accent-blue);
  border: 1px solid var(--accent-blue);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: 0.2s;
}
.action-btn.primary:hover {
  background: var(--accent-blue-hover);
}
.action-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
