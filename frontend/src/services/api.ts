import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

/**
 * فلگ حالت Mock — تا وقتی API جنگو آماده نیست همه سرویس‌ها از mocks/ می‌خوانند.
 * با `VITE_USE_MOCK=false` در .env به API واقعی سوییچ می‌کنیم (TASK-17).
 */
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

const TOKEN_KEY = 'medino_token';
const REFRESH_KEY = 'medino_refresh';

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access: string, refresh?: string) {
  localStorage.setItem(TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/**
 * رفرش خودکار توکن: روی 401 (به‌جز خود اندپوینت‌های auth) یک‌بار با
 * refresh تلاش می‌کند و درخواست اول را تکرار می‌کند؛ اگر رفرش هم fail شد
 * نشست پاک می‌شود و گاردها کاربر را به لاگین می‌فرستند.
 */
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const status = error.response?.status;
    const isAuthCall = original?.url?.includes('/auth/');
    const refresh = !USE_MOCK ? localStorage.getItem(REFRESH_KEY) : null;

    if (status === 401 && original && !original._retry && !isAuthCall && refresh) {
      original._retry = true;
      try {
        const { data } = await api.post<{ access: string; refresh?: string }>('/auth/token/refresh/', { refresh });
        setTokens(data.access, data.refresh);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        clearTokens();
        const { useAuthStore } = await import('../store/auth.store');
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(error);
  },
);

export default api;
