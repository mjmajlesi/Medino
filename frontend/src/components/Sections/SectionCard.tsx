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
import type { Section, SectionSlug } from '../../types/models';

export const sectionIcons: Record<SectionSlug, LucideIcon> = {
  basic: Microscope,
  physio: HeartPulse,
  karamozi: Stethoscope,
  karvarzi: Hospital,
  stage: Syringe,
  general: BookOpen,
};

interface SectionCardProps {
  section: Section;
  /** تعداد دروس — null یعنی نامشخص (خطای بارگذاری) و نمایش داده نمی‌شود */
  lessonCount: number | null;
}

export default function SectionCard({ section, lessonCount }: SectionCardProps) {
  const Icon = sectionIcons[section.slug];
  return (
    <Link
      to={`/lessons?section=${section.slug}`}
      className="group relative rounded-2xl border border-brand-100 bg-white p-5 transition-all duration-200 hover:-translate-y-1 hover:border-brand-300 hover:shadow-lg hover:shadow-brand-100"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-100 text-brand-700 transition-colors group-hover:bg-brand-500 group-hover:text-white">
          <Icon size={22} strokeWidth={1.8} aria-hidden="true" />
        </span>
        <div>
          <h3 className="text-base">{section.title}</h3>
          {lessonCount !== null && (
            <p className="text-xs text-slate-500">
              {lessonCount > 0 ? `${lessonCount} درس` : 'به‌زودی'}
            </p>
          )}
        </div>
      </div>
      {section.description && (
        <p className="mt-3 text-sm leading-6 text-slate-500">{section.description}</p>
      )}
      <ArrowLeft
        size={18}
        className="absolute bottom-4 end-4 text-brand-300 transition-all group-hover:-translate-x-1 group-hover:text-brand-600"
        aria-hidden="true"
      />
    </Link>
  );
}
