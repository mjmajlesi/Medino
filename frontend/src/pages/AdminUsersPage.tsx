import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Search, ShieldCheck, ShieldOff } from 'lucide-react';
import type { AdminRoleFilter, StaffUser } from '../types/models';
import { getAdminUsers, setStaffAccess } from '../services/admin.service';
import { useDebounce } from '../hooks/useDebounce';
import { useAuthStore } from '../store/auth.store';

const ROLES: { value: AdminRoleFilter; label: string }[] = [
  { value: 'all', label: 'همه' },
  { value: 'student', label: 'دانشجوها' },
  { value: 'staff', label: 'ادمین‌ها' },
  { value: 'superuser', label: 'سوپریوزرها' },
];

function Row({ user, isSelf, onChanged }: { user: StaffUser; isSelf: boolean; onChanged: () => void }) {
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState('');

  const locked = user.is_superuser || isSelf;
  const lockReason = user.is_superuser
    ? 'سوپریوزر از اینجا قابل تغییر نیست'
    : 'نمی‌توانی دسترسی خودت را بگیری';

  const act = async () => {
    setBusy(true);
    setFailed('');
    try {
      await setStaffAccess(user.id, !user.is_staff);
      onChanged();
    } catch {
      setFailed('عملیات ناموفق بود. دوباره تلاش کنید.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <li className="px-4 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">
            {user.first_name} {user.last_name}
            {isSelf && <span className="text-xs text-slate-400"> (خودت)</span>}
          </p>
          <p className="mt-0.5 text-xs text-slate-500">شماره دانشجویی: {user.student_no}</p>
        </div>
        {user.is_superuser && (
          <span className="rounded-full bg-violet-100 px-2.5 py-1 text-xs text-violet-700">سوپریوزر</span>
        )}
        {user.is_staff && !user.is_superuser && (
          <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs text-amber-700">ادمین</span>
        )}
        {locked ? (
          <span title={lockReason} className="cursor-not-allowed rounded-lg bg-slate-100 px-4 py-1.5 text-xs text-slate-400">
            {user.is_staff ? 'عزل ادمین' : 'ارتقا به ادمین'}
          </span>
        ) : (
          <button
            type="button"
            disabled={busy}
            onClick={act}
            title={user.is_staff ? 'گرفتن دسترسی ادمین' : 'دادن دسترسی ادمین'}
            className={`flex items-center gap-1 rounded-lg px-4 py-1.5 text-xs transition-colors disabled:opacity-50 ${
              user.is_staff
                ? 'border border-red-200 text-red-600 hover:bg-red-50'
                : 'bg-brand-500 text-white hover:bg-brand-600'
            }`}
          >
            {user.is_staff ? <ShieldOff size={14} aria-hidden="true" /> : <ShieldCheck size={14} aria-hidden="true" />}
            {busy ? '...' : user.is_staff ? 'عزل ادمین' : 'ارتقا به ادمین'}
          </button>
        )}
      </div>
      {failed && <p className="mt-2 rounded-lg bg-red-50 px-3 py-1.5 text-xs text-red-600">{failed}</p>}
    </li>
  );
}

export default function AdminUsersPage() {
  const current = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [input, setInput] = useState('');
  const [role, setRole] = useState<AdminRoleFilter>('all');
  const [page, setPage] = useState(1);
  const search = useDebounce(input.trim(), 400);

  useEffect(() => {
    setPage(1);
  }, [search, role]);

  const usersQuery = useQuery({
    queryKey: ['admin-users', { search, role, page }],
    queryFn: () => getAdminUsers({ search, role, page }),
  });

  const totalPages = usersQuery.data ? Math.max(1, Math.ceil(usersQuery.data.count / 20)) : 1;
  const items = usersQuery.data?.results ?? [];

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['admin-users'] });
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <nav className="text-xs text-slate-400">
        <Link to="/admin" className="hover:text-brand-600">داشبورد ادمین</Link>
        {' / '}مدیریت ادمین‌ها
      </nav>
      <h1 className="mt-2 text-xl md:text-2xl">مدیریت ادمین‌ها</h1>
      <p className="mt-1 text-sm text-slate-500">ارتقا و عزل دسترسی ادمین — سوپریوزرها فقط از پنل جنگو تغییر می‌کنند</p>

      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="flex flex-1 items-center gap-2 rounded-2xl border border-brand-100 bg-white p-2">
          <Search size={18} className="ms-2 shrink-0 text-brand-400" aria-hidden="true" />
          <label htmlFor="admin-user-search" className="sr-only">جستجوی کاربر</label>
          <input
            id="admin-user-search"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="شماره دانشجویی یا نام..."
            autoComplete="off"
            className="w-full bg-transparent py-1.5 text-sm outline-none placeholder:text-slate-400"
          />
        </div>
        <div className="flex gap-1.5" role="tablist" aria-label="فیلتر نقش">
          {ROLES.map((r) => (
            <button
              key={r.value}
              role="tab"
              aria-selected={role === r.value}
              onClick={() => setRole(r.value)}
              className={`rounded-xl px-3 py-2 text-xs font-medium transition-colors ${
                role === r.value ? 'bg-brand-500 text-white' : 'border border-brand-100 bg-white text-slate-500 hover:text-brand-700'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-brand-100 bg-white">
        {usersQuery.isPending ? (
          <div className="space-y-3 p-4" aria-busy="true">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-xl bg-brand-50" />
            ))}
          </div>
        ) : usersQuery.isError ? (
          <p className="p-6 text-center text-sm text-red-600">خطا در بارگذاری کاربرها.</p>
        ) : items.length === 0 ? (
          <p className="p-10 text-center text-sm text-slate-400">کاربری با این مشخصات پیدا نشد.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {items.map((u) => (
              <Row key={u.id} user={u} isSelf={!!current && u.student_no === current.student_no} onChanged={refresh} />
            ))}
          </ul>
        )}
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-3 text-sm">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-lg border border-brand-100 bg-white p-2 text-slate-500 disabled:opacity-40"
            aria-label="صفحه قبلی"
          >
            <ChevronRight size={16} aria-hidden="true" />
          </button>
          <span className="text-slate-500">
            صفحه {page.toLocaleString('fa-IR')} از {totalPages.toLocaleString('fa-IR')}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-lg border border-brand-100 bg-white p-2 text-slate-500 disabled:opacity-40"
            aria-label="صفحه بعدی"
          >
            <ChevronLeft size={16} aria-hidden="true" />
          </button>
        </div>
      )}
    </div>
  );
}
