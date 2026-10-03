import type { Resource, ResourceType } from '../types/models';
import api, { USE_MOCK } from './api';

export interface UploadInput {
  lessonId: string;
  professor: string;
  type: ResourceType;
  title: string;
  description?: string;
  file: File;
  /** نام نمایشی آپلودکننده — در حالت واقعی بک‌اند از توکن می‌فهمد */
  uploaderName?: string;
  /**
   * آپلود مستقیم ادمین (بدون تایید) — قرارداد بک‌اند: فیلد `direct=true`
   * در multipart؛ بک‌اند فقط برای is_staff قبولش می‌کند
   */
  direct?: boolean;
}

/* لیست نمایشی آپلودهای همین نشست (فقط Mock، در حافظه — با API حذف می‌شود) */
const mockMyUploads: Resource[] = [];

export async function submitUpload(input: UploadInput): Promise<{ id: string; status: 'pending' | 'approved' }> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 500));
    const created: Resource = {
      id: `mock-${Date.now()}`,
      lesson_id: input.lessonId,
      type: input.type,
      title: input.title,
      description: input.description,
      file_url: '#',
      status: input.direct ? 'approved' : 'pending',
      uploader_name: input.uploaderName ?? 'من',
      created_at: new Date().toISOString().slice(0, 10),
    };
    mockMyUploads.unshift(created);
    return { id: created.id, status: input.direct ? 'approved' : 'pending' };
  }
  const form = new FormData();
  form.append('lesson', input.lessonId);
  form.append('professor', input.professor);
  form.append('type', input.type);
  form.append('title', input.title);
  if (input.description) form.append('description', input.description);
  form.append('file', input.file);
  if (input.direct) form.append('direct', 'true');
  const { data } = await api.post<{ id: string; status: 'pending' | 'approved' }>('/uploads/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getPendingUploads(): Promise<Resource[]> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const { resourcesMock } = await import('../mocks/resources.mock');
    return [...mockMyUploads.filter((r) => r.status === 'pending'), ...resourcesMock.filter((r) => r.status === 'pending')];
  }
  const { data } = await api.get<Resource[]>('/admin/pending/');
  return data;
}

/**
 * آپلودهای کاربر جاری — قرارداد بک‌اند: GET /api/uploads/mine/‏ -> Resource[]
 */
export async function getMyUploads(uploaderName: string): Promise<Resource[]> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const { resourcesMock } = await import('../mocks/resources.mock');
    return [
      ...mockMyUploads,
      ...resourcesMock.filter((r) => r.uploader_name === uploaderName),
    ];
  }
  const { data } = await api.get<Resource[]>('/uploads/mine/');
  return data;
}

export async function reviewUpload(id: string, action: 'approve' | 'reject'): Promise<{ id: string; status: 'approved' | 'rejected' }> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    const next = action === 'approve' ? 'approved' : 'rejected';
    const local = mockMyUploads.find((r) => r.id === id);
    if (local) local.status = next;
    const { resourcesMock } = await import('../mocks/resources.mock');
    const seeded = resourcesMock.find((r) => r.id === id);
    if (seeded) seeded.status = next;
    return { id, status: next };
  }
  const { data } = await api.post<{ id: string; status: 'approved' | 'rejected' }>(`/admin/approve/${id}/`, { action });
  return data;
}

/**
 * دانلود فایل‌های تاییدنشده با احراز هویت — تگ <a> و <video> نمی‌توانند
 * هدر Bearer بفرستند، پس فایل با کلاینت مجهز به توکن گرفته و به‌صورت
 * object URL مصرف می‌شود. فایل‌های approved عمومی‌اند و مستقیم لینک می‌شوند.
 */
export async function fetchPrivateFile(url: string): Promise<string> {
  const { data } = await api.get<Blob>(url, { responseType: 'blob' });
  return URL.createObjectURL(data);
}
