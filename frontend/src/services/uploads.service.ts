import type { ResourceType } from '../types/models';
import api, { USE_MOCK } from './api';

export interface UploadInput {
  lessonId: string;
  professor: string;
  type: ResourceType;
  title: string;
  description?: string;
  file: File;
}

export async function submitUpload(input: UploadInput): Promise<{ id: string; status: 'pending' }> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 500));
    void input;
    return { id: `mock-${Date.now()}`, status: 'pending' };
  }
  const form = new FormData();
  form.append('lesson', input.lessonId);
  form.append('professor', input.professor);
  form.append('type', input.type);
  form.append('title', input.title);
  if (input.description) form.append('description', input.description);
  form.append('file', input.file);
  const { data } = await api.post('/uploads/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getPendingUploads() {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const { resourcesMock } = await import('../mocks/resources.mock');
    return resourcesMock.filter((r) => r.status === 'pending');
  }
  const { data } = await api.get('/admin/pending/');
  return data;
}

export async function reviewUpload(id: string, action: 'approve' | 'reject') {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    return { id, status: action === 'approve' ? 'approved' : 'rejected' };
  }
  const { data } = await api.post(`/admin/approve/${id}/`, { action });
  return data;
}
