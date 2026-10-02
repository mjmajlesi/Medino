import { UploadCloud } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function CtaBand() {
  return (
    <section aria-label="دعوت به آپلود" className="mx-auto max-w-6xl px-4 pb-12">
      <div className="flex flex-col items-center gap-4 rounded-3xl border border-brand-100 bg-brand-50/70 px-6 py-10 text-center">
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-500 text-white shadow-lg shadow-brand-200">
          <UploadCloud size={28} strokeWidth={1.8} aria-hidden="true" />
        </span>
        <h2 className="text-xl md:text-2xl">جزوه خوبت خاک نخوره!</h2>
        <p className="max-w-md text-sm leading-7 text-slate-500">
          جزوه، فیلم یا خلاصه‌ات رو آپلود کن؛ بعد از تایید ادمین به اسم خودت منتشر
          می‌شه و بقیه بچه‌ها استفاده می‌کنن.
        </p>
        <Link
          to="/upload"
          className="mt-1 min-h-11 rounded-xl bg-brand-500 px-8 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-600"
        >
          شروع آپلود
        </Link>
      </div>
    </section>
  );
}
