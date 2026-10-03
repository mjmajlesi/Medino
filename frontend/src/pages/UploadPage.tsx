import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { Link, useSearchParams } from 'react-router-dom';
import { z } from 'zod';
import { CheckCircle2, UploadCloud } from 'lucide-react';
import type { ResourceType, SectionSlug } from '../types/models';
import { RESOURCE_TYPE_LABELS } from '../types/models';
import { getLessons, getSections } from '../services/lessons.service';
import { submitUpload } from '../services/uploads.service';
import { useAuthStore } from '../store/auth.store';

/**
 * سقف و فرمت‌ها دقیقاً مطابق بک‌اند (validators.py):
 * اسناد (جزوه/سوال/خلاصه): PDF و DOCX — ویدیو: MP4 و WebM.
 * بک‌اند محتوا را هم بررسی می‌کند؛ این چک فرانت فقط برای UX زودهنگام است.
 */
const MAX_MB = 50;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const DOC_EXTS = ['pdf', 'docx'];
const VIDEO_EXTS = ['mp4', 'webm'];

const schema = z
  .object({
    section: z.string().min(1, 'بخش را انتخاب کن'),
    lessonId: z.string().min(1, 'درس را انتخاب کن'),
    professor: z.string().trim().min(2, 'نام استاد لازم است'),
    type: z.enum(['note', 'video', 'sample', 'summary'], { message: 'نوع منبع را انتخاب کن' }),
    title: z.string().trim().min(3, 'عنوان حداقل ۳ کاراکتر است'),
    description: z.string().trim().max(500, 'توضیح حداکثر ۵۰۰ کاراکتر است').optional(),
    file: z.instanceof(FileList).refine((fl) => fl.length > 0, 'فایل را انتخاب کن'),
  })
  .superRefine((data, ctx) => {
    const f = data.file[0];
    if (!f) return;
    if (f.size > MAX_BYTES) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['file'], message: `حجم فایل حداکثر ${MAX_MB} مگابایت است` });
    }
    const ext = (f.name.split('.').pop() ?? '').toLowerCase();
    const allowed = data.type === 'video' ? VIDEO_EXTS : DOC_EXTS;
    if (!allowed.includes(ext)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['file'],
        message: `برای «${RESOURCE_TYPE_LABELS[data.type]}» فقط ${allowed.join('، ')} مجاز است`,
      });
    }
  });

type Form = z.infer<typeof schema>;

const inputCls =
  'w-full rounded-xl border border-brand-100 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100';

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-medium text-slate-500">{label}</span>
      {children}
      {error && <span className="mt-1 block text-xs text-red-500">{error}</span>}
    </label>
  );
}

export default function UploadPage() {
  const [params] = useSearchParams();
  const presetLesson = params.get('lesson') ?? '';
  // آپلود مستقیم ادمین: ?direct=1 — بدون صف تایید، مستقیم منتشر می‌شود
  const directMode = params.get('direct') === '1';
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [done, setDone] = useState(false);
  const [serverError, setServerError] = useState('');

  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const lessonsQuery = useQuery({ queryKey: ['lessons', 'all'], queryFn: () => getLessons({}) });
  const allLessons = lessonsQuery.data ?? [];

  const preset = allLessons.find((l) => l.id === presetLesson);

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: {
      section: preset?.section_slug ?? '',
      lessonId: preset?.id ?? '',
      professor: preset?.professor ?? '',
      type: undefined,
      title: '',
      description: '',
    },
  });

  const watchedSection = useWatch({ control, name: 'section' });
  const watchedFile = useWatch({ control, name: 'file' });
  const watchedType = useWatch({ control, name: 'type' });
  const sectionLessons = allLessons.filter((l) => l.section_slug === (watchedSection as SectionSlug));

  const onSectionChange = (slug: string) => {
    setValue('section', slug);
    setValue('lessonId', '');
    setValue('professor', '');
  };

  const onLessonChange = (id: string) => {
    setValue('lessonId', id);
    const found = allLessons.find((l) => l.id === id);
    if (found) setValue('professor', found.professor);
  };

  const onSubmit = async (data: Form) => {
    setServerError('');
    try {
      await submitUpload({
        lessonId: data.lessonId,
        professor: data.professor,
        type: data.type as ResourceType,
        title: data.title,
        description: data.description || undefined,
        file: data.file[0],
        uploaderName: user ? `${user.first_name} ${user.last_name}` : undefined,
        direct: directMode && !!user?.is_staff,
      });
      await queryClient.invalidateQueries({ queryKey: ['my-uploads'] });
      setDone(true);
    } catch {
      setServerError('آپلود ناموفق بود. دوباره تلاش کنید.');
    }
  };

  if (done) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center">
        <CheckCircle2 size={56} className="mx-auto text-green-500" aria-hidden="true" />
        <h1 className="mt-4 text-2xl">ارسال شد!</h1>
        <p className="mt-2 text-sm leading-7 text-slate-500">
          {directMode && user?.is_staff ? (
            <>فایلت مستقیم <strong>منتشر شد</strong>.</>
          ) : (
            <>فایلت ثبت شد و الان <strong>در انتظار تایید ادمین</strong> است.
            بعد از تایید، به اسم خودت منتشر می‌شود.</>
          )}
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link to="/profile" className="rounded-xl bg-brand-500 px-6 py-2.5 text-sm text-white hover:bg-brand-600">
            مشاهده آپلودهای من
          </Link>
          <Link to="/lessons" className="rounded-xl border border-brand-200 px-6 py-2.5 text-sm text-brand-700 hover:bg-brand-50">
            بازگشت به دروس
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="flex items-center gap-2 text-xl md:text-2xl">
        <UploadCloud size={24} className="text-brand-500" aria-hidden="true" />
        آپلود منبع جدید
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        {directMode && user?.is_staff ? 'آپلود مستقیم ادمین — بدون نیاز به تایید منتشر می‌شود' : 'بعد از تایید ادمین منتشر می‌شود'}
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4 rounded-2xl border border-brand-100 bg-white p-6 shadow-lg shadow-brand-100/50" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="بخش" error={errors.section?.message}>
            <select {...register('section')} onChange={(e) => onSectionChange(e.target.value)} className={inputCls}>
              <option value="">انتخاب بخش</option>
              {(sectionsQuery.data ?? []).map((s) => (
                <option key={s.id} value={s.slug}>{s.title}</option>
              ))}
            </select>
          </Field>
          <Field label="درس" error={errors.lessonId?.message}>
            <select {...register('lessonId')} onChange={(e) => onLessonChange(e.target.value)} disabled={!watchedSection} className={inputCls}>
              <option value="">اول بخش را انتخاب کن</option>
              {sectionLessons.map((l) => (
                <option key={l.id} value={l.id}>{l.title}</option>
              ))}
            </select>
          </Field>
          <Field label="نام استاد" error={errors.professor?.message}>
            <input {...register('professor')} placeholder="دکتر رضایی" className={inputCls} />
          </Field>
          <Field label="نوع منبع" error={errors.type?.message}>
            <select {...register('type')} className={inputCls} defaultValue="">
              <option value="" disabled>انتخاب نوع</option>
              {(Object.keys(RESOURCE_TYPE_LABELS) as ResourceType[]).map((t) => (
                <option key={t} value={t}>{RESOURCE_TYPE_LABELS[t]}</option>
              ))}
            </select>
          </Field>
        </div>

        <Field label="عنوان" error={errors.title?.message}>
          <input {...register('title')} placeholder="مثلا: جزوه کامل آناتومی تنه" className={inputCls} />
        </Field>

        <Field label="توضیح (اختیاری)" error={errors.description?.message}>
          <textarea {...register('description')} rows={3} placeholder="توضیح کوتاه درباره این منبع..." className={inputCls} />
        </Field>

        <Field label={`فایل (حداکثر ${MAX_MB} مگابایت)`} error={errors.file?.message as string | undefined}>
          <input
            type="file"
            {...register('file')}
            accept={watchedType === 'video' ? '.mp4,.webm' : '.pdf,.docx'}
            className="w-full rounded-xl border border-dashed border-brand-200 bg-brand-50/50 px-4 py-3 text-sm text-slate-600 file:me-3 file:rounded-lg file:border-0 file:bg-brand-500 file:px-4 file:py-1.5 file:text-xs file:text-white"
          />
          {watchedFile && watchedFile.length > 0 && (
            <span className="mt-1 block text-xs text-slate-400">
              {watchedFile[0].name} · {(watchedFile[0].size / 1024 / 1024).toFixed(1)} مگابایت
            </span>
          )}
        </Field>

        {serverError && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{serverError}</p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="min-h-11 w-full rounded-xl bg-brand-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-600 disabled:opacity-60"
        >
          {isSubmitting ? 'در حال آپلود...' : 'ارسال برای تایید'}
        </button>
      </form>
    </div>
  );
}
