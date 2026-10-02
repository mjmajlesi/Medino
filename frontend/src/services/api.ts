import axios from 'axios';

/**
 * فلگ حالت Mock — تا وقتی API جنگو آماده نیست همه سرویس‌ها از mocks/ می‌خوانند.
 * با `VITE_USE_MOCK=false` در .env به API واقعی سوییچ می‌کنیم (TASK-17).
 */
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('medino_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
