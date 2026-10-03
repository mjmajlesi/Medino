import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import SectionCard from '../Sections/SectionCard';
import { getLessons, getSections } from '../../services/lessons.service';

export default function SectionCards() {
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const lessonsQuery = useQuery({ queryKey: ['lessons', 'all'], queryFn: () => getLessons({}) });

  if (sectionsQuery.isPending) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10" aria-busy="true">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-brand-50" />
          ))}
        </div>
      </div>
    );
  }

  if (sectionsQuery.isError) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-6 text-center text-red-600">
          خطا در بارگذاری بخش‌ها. لطفا صفحه را تازه‌سازی کنید.
        </p>
      </div>
    );
  }

  const lessons = lessonsQuery.data ?? [];
  const countsUnknown = lessonsQuery.isError;

  return (
    <section aria-label="بخش‌های آموزشی" className="mx-auto max-w-6xl px-4 py-10">
      <div className="mb-6 flex items-end justify-between">
        <div>
          <h2 className="text-xl md:text-2xl">بخش‌های آموزشی</h2>
          <p className="mt-1 text-sm text-slate-500">مقطع تحصیلی‌ات رو انتخاب کن</p>
        </div>
        <Link to="/sections" className="text-sm text-brand-600 hover:text-brand-700">
          مشاهده همه
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sectionsQuery.data.map((s) => (
          <SectionCard
            key={s.id}
            section={s}
            lessonCount={countsUnknown ? null : lessons.filter((l) => l.section_slug === s.slug).length}
          />
        ))}
      </div>
    </section>
  );
}
