import { useQuery } from '@tanstack/react-query';
import { ClipboardCheck, Inbox, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getLessons, getStats } from '../services/lessons.service';
import { getPendingUploads } from '../services/uploads.service';

const fa = (n: number) => n.toLocaleString('fa-IR');

export default function AdminDashboardPage() {
  const statsQuery = useQuery({ queryKey: ['stats'], queryFn: getStats });
  const lessonsQuery = useQuery({ queryKey: ['lessons', 'all'], queryFn: () => getLessons({}) });
  const pendingQuery = useQuery({ queryKey: ['admin-pending'], queryFn: getPendingUploads });

  const s = statsQuery.data;
  const totalResources = (s?.notes ?? 0) + (s?.videos ?? 0) + (s?.samples ?? 0) + (s?.summaries ?? 0);
  const pending = pendingQuery.data?.length ?? 0;

  const cards = [
    { label: 'درس', value: s?.lessons ?? lessonsQuery.data?.length ?? 0 },
    { label: 'منبع منتشرشده', value: totalResources },
    { label: 'در انتظار تایید', value: pending },
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-xl md:text-2xl">داشبورد ادمین</h1>
      <p className="mt-1 text-sm text-slate-500">نمای کلی مدیریت مدینو</p>

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {cards.map((c) => (
          <div key={c.label} className="rounded-2xl border border-brand-100 bg-white p-5 text-center">
            <p className="text-3xl font-extrabold text-brand-700">{fa(c.value)}</p>
            <p className="mt-1 text-sm text-slate-500">{c.label}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Link
          to="/admin/pending"
          className="flex items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5 transition-all hover:-translate-y-0.5 hover:shadow-md"
        >
          <Inbox size={26} className="shrink-0 text-amber-600" aria-hidden="true" />
          <span>
            <span className="block font-medium">بررسی آپلودها</span>
            <span className="text-xs text-slate-500">
              {pending > 0 ? `${fa(pending)} مورد در انتظار تایید است` : 'صف تایید خالی است'}
            </span>
          </span>
        </Link>
        <Link
          to="/upload?direct=1"
          className="flex items-center gap-3 rounded-2xl border border-brand-200 bg-brand-50 p-5 transition-all hover:-translate-y-0.5 hover:shadow-md"
        >
          <PlusCircle size={26} className="shrink-0 text-brand-600" aria-hidden="true" />
          <span>
            <span className="block font-medium">آپلود مستقیم</span>
            <span className="text-xs text-slate-500">بدون نیاز به تایید، مستقیم منتشر می‌شود</span>
          </span>
        </Link>
      </div>

      <p className="mt-6 flex items-center gap-1.5 text-xs text-slate-400">
        <ClipboardCheck size={14} aria-hidden="true" />
        تایید یا رد هر مورد از صفحه «بررسی آپلودها» انجام می‌شود.
      </p>
    </div>
  );
}
