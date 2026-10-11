import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { z } from 'zod';
import { Pencil, Plus, Trash2, X } from 'lucide-react';
import type { Lesson, SectionSlug } from '../types/models';
import {
  createLesson,
  deleteLesson,
  getLessons,
  getSections,
  updateLesson,
} from '../services/lessons.service';

const schema = z.object({
  section_slug: z.string().min(1, 'بخش را انتخاب کن'),
  title: z.string().trim().min(2, 'عنوان درس لازم است'),
  professor: z.string().trim().min(2, 'نام استاد لازم است'),
  term: z.string().regex(/^\d{1,2}$/, 'ترم معتبر نیست'),
  code: z.string().trim().optional(),
});

type Form = z.infer<typeof schema>;

const inputCls =
  'w-full rounded-xl border border-brand-100 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100';

function LessonForm({
  initial,
  onDone,
}: {
  initial?: Lesson;
  onDone: () => void;
}) {
  const queryClient = useQueryClient();
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const [serverError, setServerError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: initial
      ? {
          section_slug: initial.section_slug,
          title: initial.title,
          professor: initial.professor,
          term: String(initial.term),
          code: initial.code ?? '',
        }
      : undefined,
  });

  const onSubmit = async (data: Form) => {
    setServerError('');
    try {
      const term = Number(data.term);
      if (!Number.isInteger(term) || term < 1 || term > 14) {
        setServerError('ترم باید بین ۱ تا ۱۴ باشد.');
        return;
      }
      const payload = {
        section_slug: data.section_slug as SectionSlug,
        title: data.title,
        professor: data.professor,
        term,
        code: data.code || undefined,
      };
      if (initial) await updateLesson(initial.id, payload);
      else await createLesson(payload);
      await queryClient.invalidateQueries({ queryKey: ['lessons'] });
      await queryClient.invalidateQueries({ queryKey: ['stats'] });
      onDone();
    } catch {
      setServerError('ذخیره ناموفق بود. دوباره تلاش کنید.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="rounded-2xl border border-brand-200 bg-brand-50/50 p-4" noValidate>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1.5 block text-xs font-medium text-slate-500">بخش</span>
          <select {...register('section_slug')} className={inputCls}>
            <option value="">انتخاب بخش</option>
            {(sectionsQuery.data ?? []).map((s) => (
              <option key={s.id} value={s.slug}>{s.title}</option>
            ))}
          </select>
          {errors.section_slug && <span className="mt-1 block text-xs text-red-500">{errors.section_slug.message}</span>}
        </label>
        <label className="block">
          <span className="mb-1.5 block text-xs font-medium text-slate-500">عنوان درس</span>
          <input {...register('title')} placeholder="مثلا: فارماکولوژی" className={inputCls} />
          {errors.title && <span className="mt-1 block text-xs text-red-500">{errors.title.message}</span>}
        </label>
        <label className="block">
          <span className="mb-1.5 block text-xs font-medium text-slate-500">نام استاد</span>
          <input {...register('professor')} placeholder="دکتر رضایی" className={inputCls} />
          {errors.professor && <span className="mt-1 block text-xs text-red-500">{errors.professor.message}</span>}
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-slate-500">ترم</span>
            <input {...register('term')} type="number" min={1} max={14} className={inputCls} />
            {errors.term && <span className="mt-1 block text-xs text-red-500">{errors.term.message}</span>}
          </label>
          <label className="block">
            <span className="mb-1.5 block text-xs font-medium text-slate-500">کد (اختیاری)</span>
            <input {...register('code')} dir="ltr" placeholder="BAS-101" className={inputCls} />
          </label>
        </div>
      </div>
      {serverError && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{serverError}</p>}
      <div className="mt-3 flex gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-xl bg-brand-500 px-6 py-2 text-sm text-white transition-colors hover:bg-brand-600 disabled:opacity-60"
        >
          {isSubmitting ? 'در حال ذخیره...' : initial ? 'ذخیره تغییرات' : 'افزودن درس'}
        </button>
        <button
          type="button"
          onClick={onDone}
          className="rounded-xl border border-brand-200 px-6 py-2 text-sm text-slate-500 hover:bg-white"
        >
          انصراف
        </button>
      </div>
    </form>
  );
}

export default function AdminLessonsPage() {
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState<{ mode: 'new' } | { mode: 'edit'; lesson: Lesson } | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const lessonsQuery = useQuery({ queryKey: ['lessons', 'all'], queryFn: () => getLessons({}) });
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const lessons = lessonsQuery.data ?? [];
  const sectionName = (slug: string) => sectionsQuery.data?.find((s) => s.slug === slug)?.title ?? slug;

  const doDelete = async () => {
    if (!deleteId) return;
    setBusy(true);
    try {
      await deleteLesson(deleteId);
      await queryClient.invalidateQueries({ queryKey: ['lessons'] });
      await queryClient.invalidateQueries({ queryKey: ['stats'] });
      setDeleteId(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <nav className="text-xs text-slate-400">
        <Link to="/admin" className="hover:text-brand-600">داشبورد ادمین</Link>
        {' / '}مدیریت دروس
      </nav>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl md:text-2xl">مدیریت دروس</h1>
          <p className="mt-1 text-sm text-slate-500">درس جدید بساز، ویرایش کن یا حذف کن — برای همه نمایش داده می‌شود</p>
        </div>
        {!formState && (
          <button
            type="button"
            onClick={() => setFormState({ mode: 'new' })}
            className="flex items-center gap-1.5 rounded-xl bg-brand-500 px-5 py-2.5 text-sm text-white transition-colors hover:bg-brand-600"
          >
            <Plus size={17} aria-hidden="true" />
            افزودن درس
          </button>
        )}
      </div>

      {formState && (
        <div className="mt-4">
          <LessonForm
            initial={formState.mode === 'edit' ? formState.lesson : undefined}
            onDone={() => setFormState(null)}
          />
        </div>
      )}

      <div className="mt-4 rounded-2xl border border-brand-100 bg-white">
        {lessonsQuery.isPending ? (
          <div className="space-y-3 p-4" aria-busy="true">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-xl bg-brand-50" />
            ))}
          </div>
        ) : lessonsQuery.isError ? (
          <p className="p-6 text-center text-sm text-red-600">خطا در بارگذاری دروس.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {lessons.map((l) => (
              <li key={l.id} className="flex flex-wrap items-center gap-2 px-4 py-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{l.title}</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {sectionName(l.section_slug)} · {l.professor} · ترم {l.term.toLocaleString('fa-IR')}
                  </p>
                </div>
                {deleteId === l.id ? (
                  <>
                    <span className="w-full text-xs text-red-600 sm:w-auto">
                      حذف شود؟ منابع این درس هم از دسترس خارج می‌شوند.
                    </span>
                    <button
                      type="button"
                      disabled={busy}
                      onClick={doDelete}
                      className="rounded-lg bg-red-600 px-4 py-1.5 text-xs text-white hover:bg-red-700 disabled:opacity-50"
                    >
                      {busy ? '...' : 'بله، حذف کن'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setDeleteId(null)}
                      className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs text-slate-500"
                    >
                      <X size={14} aria-hidden="true" />
                      انصراف
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => {
                        setDeleteId(null);
                        setFormState({ mode: 'edit', lesson: l });
                      }}
                      className="flex items-center gap-1 rounded-lg border border-brand-200 px-3 py-1.5 text-xs text-brand-700 hover:bg-brand-50"
                    >
                      <Pencil size={14} aria-hidden="true" />
                      ویرایش
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setFormState(null);
                        setDeleteId(l.id);
                      }}
                      className="flex items-center gap-1 rounded-lg border border-red-200 px-3 py-1.5 text-xs text-red-600 hover:bg-red-50"
                    >
                      <Trash2 size={14} aria-hidden="true" />
                      حذف
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
