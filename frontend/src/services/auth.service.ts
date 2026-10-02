import type { StudentUser } from '../types/models';
import api, { USE_MOCK } from './api';

const TOKEN_KEY = 'medino_token';

export interface RegisterInput extends StudentUser {
  password: string;
}

interface MockAuthResult {
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

export async function login(studentNo: string, _password: string): Promise<MockAuthResult> {
  void _password;
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const result = { user: mockUser, access: 'mock-access', refresh: 'mock-refresh' };
    localStorage.setItem(TOKEN_KEY, result.access);
    return result;
  }
  const { data } = await api.post('/auth/login/', {
    student_no: studentNo,
    password: _password,
  });
  localStorage.setItem(TOKEN_KEY, data.access);
  return data;
}

export async function register(input: RegisterInput): Promise<MockAuthResult> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const { password: _pw, ...user } = input;
    void _pw;
    const result = { user, access: 'mock-access', refresh: 'mock-refresh' };
    localStorage.setItem(TOKEN_KEY, result.access);
    return result;
  }
  const { data } = await api.post('/auth/register/', input);
  localStorage.setItem(TOKEN_KEY, data.access);
  return data;
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}
