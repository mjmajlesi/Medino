import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, FileText, ListChecks, NotebookPen, Video } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Lesson } from '../../types/models';
import { RESOURCE_TYPE_LABELS } from '../../types/models';
import { countByType, getLessonDetail, getSections } from '../../services/lessons.service';

const typeIcons = { note: FileText, video: Video, sample: ListChecks, summary: NotebookPen } as const;

export default function LessonCard({ lesson }: { lesson: Lesson }) {
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const detailQuery = useQuery({
    queryKey: ['lesson-detail', lesson.id],
    queryFn: () => getLessonDetail(lesson.id),
    staleTime: 5 * 60 * 1000,
  });

  const sectionTitle = sectionsQuery.data?.find((s) => s.slug === lesson.section_slug)?.title;
  const approved = (detailQuery.data?.resources ?? []).filter((r) => r.status === 'approved');
  const counts = countByType(approved);

  return (
    <Link
      to={`/lessons/${lesson.id}`}
      className="group flex flex-col rounded-2xl border border-brand-100 bg-white p-5 transition-all duration-200 hover:-translate-y-1 hover:border-brand-300 hover:shadow-lg hover:shadow-brand-100"
    >
      <div className="flex items-start justify-between gap-2">
        {sectionTitle && (
          <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
            {sectionTitle}
          </span>
        )}
        <span className="text-xs text-slate-400">ترم {lesson.term}</span>
      </div>

      <h3 className="mt-3 text-lg">{lesson.title}</h3>
      <p className="mt-1 text-sm text-slate-500">{lesson.professor}</p>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {(Object.keys(counts) as (keyof typeof counts)[]).map((t) => {
          const Icon = typeIcons[t];
          return (
            <span
              key={t}
              title={RESOURCE_TYPE_LABELS[t]}
              className={`flex items-center gap-1 rounded-lg px-2 py-1 text-xs ${
                counts[t] > 0 ? 'bg-brand-50 text-brand-700' : 'bg-slate-50 text-slate-300'
              }`}
            >
              <Icon size={14} aria-hidden="true" />
              {counts[t].toLocaleString('fa-IR')}
            </span>
          );
        })}
      </div>

      <span className="mt-4 flex items-center gap-1 pt-1 text-sm font-medium text-brand-600 group-hover:text-brand-700">
        مشاهده منابع
        <ArrowLeft size={16} className="transition-transform group-hover:-translate-x-1" />
      </span>
    </Link>
  );
}
