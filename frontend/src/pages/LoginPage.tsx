import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { USE_MOCK } from '../services/api';
import { useAuthStore } from '../store/auth.store';

const schema = z.object({
  studentNo: z
    .string()
    .regex(/^\d{7,12}$/, 'شماره دانشجویی باید ۷ تا ۱۲ رقم باشد'),
  password: z.string().min(6, 'رمز عبور حداقل ۶ کاراکتر است'),
});

type Form = z.infer<typeof schema>;

const inputCls =
  'w-full rounded-xl border border-brand-100 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((s) => s.login);
  const loginAsAdmin = useAuthStore((s) => s.loginAsAdmin);
  const alreadyIn = useAuthStore((s) => s.user);
  const [serverError, setServerError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Form>({ resolver: zodResolver(schema) });

  if (alreadyIn) {
    return <Navigate to={(location.state as { from?: string } | null)?.from ?? '/'} replace />;
  }

  const onSubmit = async (data: Form) => {
    setServerError('');
    try {
      await login(data.studentNo, data.password);
      navigate((location.state as { from?: string } | null)?.from ?? '/', { replace: true });
    } catch {
      setServerError('ورود ناموفق بود. مشخصات را بررسی کنید.');
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-12">
      <h1 className="text-center text-2xl">ورود به مدینو</h1>
      <p className="mt-1 text-center text-sm text-slate-500">با شماره دانشجویی وارد شو</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 rounded-2xl border border-brand-100 bg-white p-6 shadow-lg shadow-brand-100/50" noValidate>
        <label className="block">
          <span className="mb-1.5 block text-xs font-medium text-slate-500">شماره دانشجویی</span>
          <input {...register('studentNo')} inputMode="numeric" dir="ltr" placeholder="400123456" className={inputCls} />
          {errors.studentNo && <span className="mt-1 block text-xs text-red-500">{errors.studentNo.message}</span>}
        </label>

        <label className="mt-4 block">
          <span className="mb-1.5 block text-xs font-medium text-slate-500">رمز عبور</span>
          <input {...register('password')} type="password" dir="ltr" placeholder="••••••" className={inputCls} />
          {errors.password && <span className="mt-1 block text-xs text-red-500">{errors.password.message}</span>}
        </label>

        {serverError && (
          <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{serverError}</p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 min-h-11 w-full rounded-xl bg-brand-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-600 disabled:opacity-60"
        >
          {isSubmitting ? 'در حال ورود...' : 'ورود'}
        </button>

        <p className="mt-4 text-center text-xs text-slate-500">
          حساب نداری؟{' '}
          <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
            ثبت‌نام کن
          </Link>
        </p>

        {USE_MOCK && (
          <button
            type="button"
            onClick={async () => {
              setServerError('');
              try {
                await loginAsAdmin();
                navigate('/admin', { replace: true });
              } catch {
                setServerError('ورود نمایشی ناموفق بود.');
              }
            }}
            className="mt-3 w-full rounded-xl border border-dashed border-brand-300 py-2.5 text-xs text-brand-600 transition-colors hover:bg-brand-50"
          >
            ورود نمایشی به‌عنوان ادمین (فقط دوره Mock)
          </button>
        )}
      </form>
    </div>
  );
}
