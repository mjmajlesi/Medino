import { create } from 'zustand';
import type { StudentUser } from '../types/models';
import { getAccessToken, USE_MOCK } from '../services/api';
import { getMe, login as svcLogin, logout as svcLogout, mockAdminLogin, register as svcRegister } from '../services/auth.service';
import type { RegisterInput } from '../services/auth.service';

const USER_KEY = 'medino_user';

function loadUser(): StudentUser | null {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as StudentUser) : null;
  } catch {
    return null;
  }
}

interface AuthState {
  user: StudentUser | null;
  login: (studentNo: string, password: string) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  loginAsAdmin: () => Promise<void>;
  logout: () => void;
  /**
   * اعتبارسنجی مجدد نشست در شروع اپ — در حالت واقعی با /auth/me/ نقش
   * و مشخصات تازه را می‌گیرد؛ توکن نامعتبر = خروج خودکار
   */
  restore: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: loadUser(),

  login: async (studentNo, password) => {
    const { user } = await svcLogin(studentNo, password);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ user });
  },

  register: async (input) => {
    const { user } = await svcRegister(input);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ user });
  },

  loginAsAdmin: async () => {
    if (!USE_MOCK) throw new Error('ورود نمایشی فقط در حالت Mock فعال است');
    const { user } = await mockAdminLogin();
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ user });
  },

  logout: () => {
    svcLogout();
    localStorage.removeItem(USER_KEY);
    set({ user: null });
  },

  restore: async () => {
    if (USE_MOCK || !getAccessToken()) return;
    try {
      const user = await getMe();
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      set({ user });
    } catch {
      svcLogout();
      localStorage.removeItem(USER_KEY);
      set({ user: null });
    }
  },
}));
