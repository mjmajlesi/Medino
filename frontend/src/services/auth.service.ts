import type { StudentUser } from '../types/models';
import api, { clearTokens, setTokens, USE_MOCK } from './api';

export interface RegisterInput extends StudentUser {
  password: string;
}

export interface AuthResult {
  user: StudentUser;
  access: string;
  refresh: string;
}

const mockUser: StudentUser = {
  first_name: 'دانشجوی',
  last_name: 'تستی',
  student_no: '400123456',
  entry_year: '1403',
  current_term: '3',
};

/** ورود نمایشی ادمین (فقط Mock — با API واقعی حذف می‌شود) */
const mockAdmin: StudentUser = {
  first_name: 'ادمین',
  last_name: 'مدینو',
  student_no: '400000000',
  entry_year: '1400',
  current_term: '12',
  is_staff: true,
};

/* ------------------------------------------------------------------ */
/* قرارداد API احراز هویت برای تیم بک‌اند (Django REST):               */
/*   POST {VITE_API_URL}/auth/login/                                   */
/*     body: { student_no: string, password: string }                   */
/*   POST {VITE_API_URL}/auth/register/                                */
/*     body: { first_name, last_name, student_no, entry_year,          */
/*             current_term, password }                                */
/*   هر دو در حالت موفق (200) برمی‌گردانند:                            */
/*     { user: { first_name, last_name, student_no, entry_year,         */
/*               current_term, is_staff }, access: string, refresh: string } */
/*   فرانت توکن access را در هدر Authorization: Bearer <access> می‌فرستد */
/*   با VITE_USE_MOCK=false همین کد بدون هیچ تغییری به API واقعی وصل   */
/*   می‌شود و کل بخش Mock زیر حذف‌شدنی است.                            */
/* ------------------------------------------------------------------ */

/**
 * رجیستری نمایشی فقط در حافظه (نه localStorage) — تا رفرش صفحه زنده است.
 * با وصل شدن API واقعی، کل این بخش Mock دور انداخته می‌شود.
 */
const mockRegistry = new Map<string, StoredMockUser>();

interface StoredMockUser {
  user: StudentUser;
  password: string;
}

export async function login(studentNo: string, _password: string): Promise<AuthResult> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const found = mockRegistry.get(studentNo);
    if (found) {
      if (found.password !== _password) throw new Error('رمز عبور اشتباه است');
      const result = { user: found.user, access: 'mock-access', refresh: 'mock-refresh' };
      setTokens(result.access, result.refresh);
      return result;
    }
    // حالت دمو: شماره ناشناس با همان یوزر تستی وارد می‌شود
    const result = { user: mockUser, access: 'mock-access', refresh: 'mock-refresh' };
    setTokens(result.access, result.refresh);
    return result;
  }
  const { data } = await api.post('/auth/login/', {
    student_no: studentNo,
    password: _password,
  });
  setTokens(data.access, data.refresh);
  return data;
}

export async function register(input: RegisterInput): Promise<AuthResult> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const { password, ...user } = input;
    mockRegistry.set(user.student_no, { user, password });
    const result = { user, access: 'mock-access', refresh: 'mock-refresh' };
    setTokens(result.access, result.refresh);
    return result;
  }
  const { data } = await api.post('/auth/register/', input);
  setTokens(data.access, data.refresh);
  return data;
}

export function logout() {
  clearTokens();
}

/** پروفایل جاری از سرور — برای اعتبارسنجی مجدد نشست بعد از رفرش */
export async function getMe(): Promise<StudentUser> {
  const { data } = await api.get<StudentUser>('/auth/me/');
  return data;
}

/** ورود نمایشی ادمین — فقط Mock؛ دکمه‌اش در LoginPage است */
export async function mockAdminLogin(): Promise<AuthResult> {
  await new Promise((r) => setTimeout(r, 300));
  const result = { user: mockAdmin, access: 'mock-admin-access', refresh: 'mock-admin-refresh' };
  setTokens(result.access, result.refresh);
  return result;
}
