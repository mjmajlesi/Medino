import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-16 text-center">
      <p className="text-6xl font-bold text-brand-200">۴۰۴</p>
      <h1 className="mt-4 text-2xl">صفحه پیدا نشد</h1>
      <p className="mt-2 text-slate-500">آدرسی که دنبالش می‌گردی وجود نداره.</p>
      <Link
        to="/"
        className="mt-6 inline-block rounded-md bg-brand-500 px-6 py-2 text-white transition-colors hover:bg-brand-600"
      >
        بازگشت به خانه
      </Link>
    </div>
  );
}
