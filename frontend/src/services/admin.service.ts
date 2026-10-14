import type { AdminRoleFilter, Paginated, StaffUser } from '../types/models';
import api, { USE_MOCK } from './api';

/* ------------------------------------------------------------------ */
/* مدیریت کاربرها (staff) — قرارداد بک‌اند:                              */
/*   GET   /api/admin/users/?search=&role=all|student|staff|superuser&page= */
/*     -> {count, next, previous, results: StaffUser[]} (۲۰ تایی)        */
/*   PATCH /api/admin/users/:id/access/ {is_staff: bool}                 */
/*   قوانین سمت سرور: سوپریوزر قابل تغییر نیست؛ هیچ‌کس نمی‌تواند دسترسی  */
/*   خودش را بگیرد؛ staff فقط staff غیرسوپر دیگر را می‌تواند عزل کند.    */
/* ------------------------------------------------------------------ */

export interface AdminUserFilters {
  search?: string;
  role?: AdminRoleFilter;
  page?: number;
}

export async function getAdminUsers(filters: AdminUserFilters = {}): Promise<Paginated<StaffUser>> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    return { count: 0, next: null, previous: null, results: [] };
  }
  const { data } = await api.get<Paginated<StaffUser>>('/admin/users/', {
    params: {
      search: filters.search || undefined,
      role: filters.role && filters.role !== 'all' ? filters.role : undefined,
      page: filters.page && filters.page > 1 ? filters.page : undefined,
    },
  });
  return data;
}

export async function setStaffAccess(id: string, isStaff: boolean): Promise<StaffUser> {
  const { data } = await api.patch<StaffUser>(`/admin/users/${id}/access/`, { is_staff: isStaff });
  return data;
}
