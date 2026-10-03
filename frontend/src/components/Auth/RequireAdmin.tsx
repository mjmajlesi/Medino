import { Link } from 'react-router-dom';
import type { ReactNode } from 'react';
import { useAuthStore } from '../../store/auth.store';

/** فقط ادمین (is_staff) — بقیه صفحه ۴۰۳ می‌بینند */
export default function RequireAdmin({ children }: { children: ReactNode }) {
  const user = useAuthStore((s) => s.user);

  if (!user?.is_staff) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center">
        <p className="text-6xl font-bold text-brand-200">۴۰۳</p>
        <h1 className="mt-4 text-2xl">دسترسی محدود</h1>
        <p className="mt-2 text-sm text-slate-500">این بخش فقط برای ادمین‌هاست.</p>
        <Link to="/" className="mt-6 inline-block rounded-md bg-brand-500 px-6 py-2 text-white hover:bg-brand-600">
          بازگشت به خانه
        </Link>
      </div>
    );
  }
  return <>{children}</>;
}
