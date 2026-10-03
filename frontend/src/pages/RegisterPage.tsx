import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { useAuthStore } from '../store/auth.store';

const schema = z
  .object({
    firstName: z.string().trim().min(2, 'نام را کامل بنویس'),
    lastName: z.string().trim().min(2, 'نام خانوادگی را کامل بنویس'),
    studentNo: z.string().regex(/^\d{7,12}$/, 'شماره دانشجویی باید ۷ تا ۱۲ رقم باشد'),
    entryYear: z.string().regex(/^\d{4}$/, 'سال ورودی ۴ رقم است (مثلا ۱۴۰۳)'),
    currentTerm: z.string().min(1, 'ترم فعلی را انتخاب کن'),
    password: z.string().min(6, 'رمز عبور حداقل ۶ کاراکتر است'),
    confirmPassword: z.string(),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: 'تکرار رمز با رمز یکی نیست',
    path: ['confirmPassword'],
  });

type Form = z.infer<typeof schema>;

const inputCls =
  'w-full rounded-xl border border-brand-100 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100';

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-medium text-slate-500">{label}</span>
      {children}
      {error && <span className="mt-1 block text-xs text-red-500">{error}</span>}
    </label>
  );
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const registerUser = useAuthStore((s) => s.register);
  const alreadyIn = useAuthStore((s) => s.user);
  const [serverError, setServerError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Form>({ resolver: zodResolver(schema) });

  if (alreadyIn) {
    return <Navigate to="/" replace />;
  }

  const onSubmit = async (data: Form) => {
    setServerError('');
    try {
      await registerUser({
        first_name: data.firstName,
        last_name: data.lastName,
        student_no: data.studentNo,
        entry_year: data.entryYear,
        current_term: data.currentTerm,
        password: data.password,
      });
      navigate('/', { replace: true });
    } catch {
      setServerError('ثبت‌نام ناموفق بود. دوباره تلاش کنید.');
    }
  };

  return (
    <div className="mx-auto max-w-lg px-4 py-12">
      <h1 className="text-center text-2xl">ثبت‌نام در مدینو</h1>
      <p className="mt-1 text-center text-sm text-slate-500">مشخصات دانشجویی‌ات را وارد کن</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 rounded-2xl border border-brand-100 bg-white p-6 shadow-lg shadow-brand-100/50" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="نام" error={errors.firstName?.message}>
            <input {...register('firstName')} placeholder="محمد" className={inputCls} />
          </Field>
          <Field label="نام خانوادگی" error={errors.lastName?.message}>
            <input {...register('lastName')} placeholder="رضایی" className={inputCls} />
          </Field>
          <Field label="شماره دانشجویی" error={errors.studentNo?.message}>
            <input {...register('studentNo')} inputMode="numeric" dir="ltr" placeholder="400123456" className={inputCls} />
          </Field>
          <Field label="سال ورودی" error={errors.entryYear?.message}>
            <input {...register('entryYear')} inputMode="numeric" placeholder="۱۴۰۳" className={inputCls} />
          </Field>
          <Field label="ترم فعلی" error={errors.currentTerm?.message}>
            <select {...register('currentTerm')} defaultValue="" className={inputCls}>
              <option value="" disabled>انتخاب ترم</option>
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={String(i + 1)}>
                  ترم {(i + 1).toLocaleString('fa-IR')}
                </option>
              ))}
            </select>
          </Field>
          <div />
          <Field label="رمز عبور" error={errors.password?.message}>
            <input {...register('password')} type="password" dir="ltr" placeholder="حداقل ۶ کاراکتر" className={inputCls} />
          </Field>
          <Field label="تکرار رمز عبور" error={errors.confirmPassword?.message}>
            <input {...register('confirmPassword')} type="password" dir="ltr" placeholder="تکرار رمز" className={inputCls} />
          </Field>
        </div>

        {serverError && (
          <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{serverError}</p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 min-h-11 w-full rounded-xl bg-brand-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-600 disabled:opacity-60"
        >
          {isSubmitting ? 'در حال ثبت‌نام...' : 'ثبت‌نام'}
        </button>

        <p className="mt-4 text-center text-xs text-slate-500">
          قبلا ثبت‌نام کردی؟{' '}
          <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
            وارد شو
          </Link>
        </p>
      </form>
    </div>
  );
}
