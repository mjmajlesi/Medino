import { useQuery } from '@tanstack/react-query';
import { GraduationCap, LogOut, UploadCloud } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import type { ResourceStatus } from '../types/models';
import { RESOURCE_TYPE_LABELS } from '../types/models';
import { getMyUploads } from '../services/uploads.service';
import { useAuthStore } from '../store/auth.store';

const statusStyle: Record<ResourceStatus, string> = {
  pending: 'bg-amber-50 text-amber-700 ring-amber-200',
  approved: 'bg-green-50 text-green-700 ring-green-200',
  rejected: 'bg-red-50 text-red-600 ring-red-200',
};

const statusLabel: Record<ResourceStatus, string> = {
  pending: 'در انتظار تایید',
  approved: 'منتشر شده',
  rejected: 'رد شده',
};

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  const uploadsQuery = useQuery({
    queryKey: ['my-uploads', user?.student_no],
    queryFn: () => getMyUploads(`${user?.first_name} ${user?.last_name}`),
    enabled: !!user,
  });

  if (!user) return null; // گارد روت اجازه مهمان نمی‌دهد

  const fullName = `${user.first_name} ${user.last_name}`;
  const uploads = uploadsQuery.data ?? [];

  const info = [
    { label: 'نام و نام خانوادگی', value: fullName },
    { label: 'شماره دانشجویی', value: user.student_no },
    { label: 'سال ورودی', value: user.entry_year },
    { label: 'ترم فعلی', value: `ترم ${user.current_term}` },
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="flex flex-wrap items-center gap-4 rounded-2xl border border-brand-100 bg-gradient-to-l from-brand-50 to-white p-6">
        <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-500 text-2xl font-bold text-white">
          {user.first_name.charAt(0)}
        </span>
        <div className="flex-1">
          <h1 className="text-xl md:text-2xl">{fullName}</h1>
          <p className="mt-1 flex items-center gap-1 text-sm text-slate-500">
            <GraduationCap size={16} className="text-brand-400" aria-hidden="true" />
            دانشجوی پزشکی
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            logout();
            navigate('/');
          }}
          className="flex items-center gap-1.5 rounded-xl border border-red-200 px-4 py-2 text-sm text-red-600 transition-colors hover:bg-red-50"
        >
          <LogOut size={15} aria-hidden="true" />
          خروج از حساب
        </button>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {info.map((it) => (
          <div key={it.label} className="rounded-2xl border border-brand-100 bg-white p-4">
            <p className="text-xs text-slate-400">{it.label}</p>
            <p className="mt-1 font-medium">{it.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-between">
        <h2 className="text-lg">آپلودهای من</h2>
        <Link to="/upload" className="text-sm text-brand-600 hover:text-brand-700">
          آپلود جدید
        </Link>
      </div>

      <div className="mt-3 rounded-2xl border border-brand-100 bg-white p-4">
        {uploadsQuery.isPending ? (
          <div className="space-y-3" aria-busy="true">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-xl bg-brand-50" />
            ))}
          </div>
        ) : uploads.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <UploadCloud size={36} className="text-brand-200" aria-hidden="true" />
            <p className="text-sm text-slate-500">هنوز چیزی آپلود نکردی</p>
            <Link
              to="/upload"
              className="rounded-xl bg-brand-500 px-6 py-2 text-xs text-white transition-colors hover:bg-brand-600"
            >
              اولین آپلود
            </Link>
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {uploads.map((r) => (
              <li key={r.id} className="flex flex-wrap items-center gap-2 px-2 py-3">
                <span className="min-w-0 flex-1 text-sm">{r.title}</span>
                <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs text-brand-700">
                  {RESOURCE_TYPE_LABELS[r.type]}
                </span>
                <span className={`rounded-full px-2.5 py-1 text-xs ring-1 ${statusStyle[r.status]}`}>
                  {statusLabel[r.status]}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
