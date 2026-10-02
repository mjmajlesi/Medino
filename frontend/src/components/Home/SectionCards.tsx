import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  BookOpen,
  HeartPulse,
  Hospital,
  Microscope,
  Stethoscope,
  Syringe,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { SectionSlug } from '../../types/models';
import { getLessons, getSections } from '../../services/lessons.service';

const sectionIcons: Record<SectionSlug, LucideIcon> = {
  basic: Microscope,
  physio: HeartPulse,
  karamozi: Stethoscope,
  karvarzi: Hospital,
  stage: Syringe,
  general: BookOpen,
};

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
        {sectionsQuery.data.map((s) => {
          const count = lessons.filter((l) => l.section_slug === s.slug).length;
          const Icon = sectionIcons[s.slug];
          return (
            <Link
              key={s.id}
              to={`/lessons?section=${s.slug}`}
              className="group relative rounded-2xl border border-brand-100 bg-white p-5 transition-all duration-200 hover:-translate-y-1 hover:border-brand-300 hover:shadow-lg hover:shadow-brand-100"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-100 text-brand-700 transition-colors group-hover:bg-brand-500 group-hover:text-white">
                  <Icon size={22} strokeWidth={1.8} />
                </span>
                <div>
                  <h3 className="text-base">{s.title}</h3>
                  <p className="text-xs text-slate-500">
                    {count > 0 ? `${count} درس` : 'به‌زودی'}
                  </p>
                </div>
              </div>
              {s.description && (
                <p className="mt-3 text-sm leading-6 text-slate-500">{s.description}</p>
              )}
              <ArrowLeft
                size={18}
                className="absolute bottom-4 end-4 text-brand-300 transition-all group-hover:-translate-x-1 group-hover:text-brand-600"
              />
            </Link>
          );
        })}
      </div>
    </section>
  );
}
