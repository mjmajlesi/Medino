import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import SectionCard from '../components/Sections/SectionCard';
import { getLessons, getSections } from '../services/lessons.service';

export default function SectionsPage() {
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const lessonsQuery = useQuery({ queryKey: ['lessons', 'all'], queryFn: () => getLessons({}) });

  const lessons = lessonsQuery.data ?? [];
  const countsUnknown = lessonsQuery.isError;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <nav aria-label="مسیر" className="text-xs text-slate-400">
        <Link to="/" className="hover:text-brand-600">خانه</Link>
        {' / '}بخش‌ها
      </nav>
      <h1 className="mt-2 text-xl md:text-2xl">بخش‌های آموزشی</h1>
      <p className="mt-1 text-sm text-slate-500">مقطع تحصیلی‌ات رو انتخاب کن تا درس‌هاش رو ببینی</p>

      <div className="mt-6">
        {sectionsQuery.isPending ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2" aria-busy="true">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-36 animate-pulse rounded-2xl bg-brand-50" />
            ))}
          </div>
        ) : sectionsQuery.isError ? (
          <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-6 text-center text-red-600">
            خطا در بارگذاری بخش‌ها. لطفا صفحه را تازه‌سازی کنید.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {sectionsQuery.data.map((s) => (
              <SectionCard
                key={s.id}
                section={s}
                lessonCount={countsUnknown ? null : lessons.filter((l) => l.section_slug === s.slug).length}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
