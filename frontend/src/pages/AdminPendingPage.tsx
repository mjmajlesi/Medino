import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Check, Download, Inbox, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Resource } from '../types/models';
import { RESOURCE_TYPE_LABELS } from '../types/models';
import { getLessonDetail } from '../services/lessons.service';
import { fetchPrivateFile, getPendingUploads, reviewUpload } from '../services/uploads.service';

function Row({ item }: { item: Resource }) {
  const queryClient = useQueryClient();
  const [busy, setBusy] = useState<'approve' | 'reject' | null>(null);
  const [done, setDone] = useState<'approved' | 'rejected' | null>(null);
  const [failed, setFailed] = useState(false);
  const [lessonTitle, setLessonTitle] = useState<string>('');
  // آدرس امن دانلود: فایل pending با توکن گرفته می‌شود، نه لینک مستقیم
  const [href, setHref] = useState(item.file_url);

  useEffect(() => {
    getLessonDetail(item.lesson_id)
      .then((d) => setLessonTitle(d.lesson.title))
      .catch(() => {});
  }, [item.lesson_id]);

  useEffect(() => {
    let alive = true;
    let objUrl: string | null = null;
    if (item.file_url !== '#' && item.status !== 'approved') {
      fetchPrivateFile(item.file_url)
        .then((u) => {
          if (alive) {
            objUrl = u;
            setHref(u);
          } else {
            URL.revokeObjectURL(u);
          }
        })
        .catch(() => {});
    } else {
      setHref(item.file_url);
    }
    return () => {
      alive = false;
      if (objUrl) URL.revokeObjectURL(objUrl);
    };
  }, [item.file_url, item.status]);

  const act = async (action: 'approve' | 'reject') => {
    setBusy(action);
    setFailed(false);
    try {
      await reviewUpload(item.id, action);
      setDone(action === 'approve' ? 'approved' : 'rejected');
      await queryClient.invalidateQueries({ queryKey: ['admin-pending'] });
      await queryClient.invalidateQueries({ queryKey: ['my-uploads'] });
      await queryClient.invalidateQueries({ queryKey: ['lessons'] });
    } catch {
      setFailed(true);
    } finally {
      setBusy(null);
    }
  };

  return (
    <li className={`px-4 py-4 ${done === 'approved' ? 'bg-green-50/60' : done === 'rejected' ? 'bg-red-50/60' : ''}`}>
      <div className="flex flex-wrap items-center gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">{item.title}</p>
          <p className="mt-0.5 text-xs text-slate-500">
            {lessonTitle || item.lesson_id} · {RESOURCE_TYPE_LABELS[item.type]} · آپلودکننده: {item.uploader_name}
          </p>
        </div>
        {failed && (
          <span className="w-full rounded-lg bg-red-50 px-3 py-1.5 text-xs text-red-600">
            عملیات ناموفق بود (مثلا دسترسی قطع است). دوباره تلاش کنید.
          </span>
        )}
        {item.file_url !== '#' ? (
          <a href={href} download className="flex items-center gap-1 rounded-lg border border-brand-200 px-3 py-1.5 text-xs text-brand-700 hover:bg-brand-50">
            <Download size={14} aria-hidden="true" />
            دانلود
          </a>
        ) : (
          <span className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs text-slate-400">فایل نمایشی</span>
        )}
        {done ? (
          <span className={`rounded-lg px-3 py-1.5 text-xs font-medium ${done === 'approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
            {done === 'approved' ? 'تایید شد' : 'رد شد'}
          </span>
        ) : (
          <>
            <button
              type="button"
              disabled={busy !== null}
              onClick={() => act('approve')}
              className="flex items-center gap-1 rounded-lg bg-green-600 px-4 py-1.5 text-xs text-white transition-colors hover:bg-green-700 disabled:opacity-50"
            >
              <Check size={14} aria-hidden="true" />
              {busy === 'approve' ? '...' : 'تایید'}
            </button>
            <button
              type="button"
              disabled={busy !== null}
              onClick={() => act('reject')}
              className="flex items-center gap-1 rounded-lg border border-red-200 px-4 py-1.5 text-xs text-red-600 transition-colors hover:bg-red-50 disabled:opacity-50"
            >
              <X size={14} aria-hidden="true" />
              {busy === 'reject' ? '...' : 'رد'}
            </button>
          </>
        )}
      </div>
    </li>
  );
}

export default function AdminPendingPage() {
  const { data, isPending, isError } = useQuery({ queryKey: ['admin-pending'], queryFn: getPendingUploads });
  const items = data ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <nav className="text-xs text-slate-400">
        <Link to="/admin" className="hover:text-brand-600">داشبورد ادمین</Link>
        {' / '}بررسی آپلودها
      </nav>
      <h1 className="mt-2 flex items-center gap-2 text-xl md:text-2xl">
        <Inbox size={22} className="text-amber-500" aria-hidden="true" />
        بررسی آپلودها
        {items.length > 0 && (
          <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs text-amber-700">
            {items.length.toLocaleString('fa-IR')}
          </span>
        )}
      </h1>

      <div className="mt-4 rounded-2xl border border-brand-100 bg-white">
        {isPending ? (
          <div className="space-y-3 p-4" aria-busy="true">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-14 animate-pulse rounded-xl bg-brand-50" />
            ))}
          </div>
        ) : isError ? (
          <p className="p-6 text-center text-sm text-red-600">خطا در بارگذاری صف تایید.</p>
        ) : items.length === 0 ? (
          <p className="p-10 text-center text-sm text-slate-400">صف تایید خالی است — همه‌چیز بررسی شده.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {items.map((r) => (
              <Row key={r.id} item={r} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
