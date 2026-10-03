import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, ChevronLeft, UploadCloud, User } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import type { ResourceType } from '../types/models';
import FileRow from '../components/Lessons/FileRow';
import ResourceTabs from '../components/Lessons/ResourceTabs';
import { countByType, getLessonDetail, getSections } from '../services/lessons.service';

export default function LessonDetailPage() {
  const { id = '' } = useParams();
  const [tab, setTab] = useState<ResourceType>('note');

  const detailQuery = useQuery({
    queryKey: ['lesson-detail', id],
    queryFn: () => getLessonDetail(id),
    retry: false,
  });
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });

  if (detailQuery.isPending) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-8" aria-busy="true">
        <div className="h-8 w-48 animate-pulse rounded bg-brand-50" />
        <div className="mt-4 h-40 animate-pulse rounded-2xl bg-brand-50" />
      </div>
    );
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 text-center">
        <p className="text-6xl font-bold text-brand-200">؟</p>
        <h1 className="mt-4 text-2xl">درس پیدا نشد</h1>
        <Link to="/lessons" className="mt-6 inline-block rounded-md bg-brand-500 px-6 py-2 text-white hover:bg-brand-600">
          بازگشت به لیست دروس
        </Link>
      </div>
    );
  }

  const { lesson, resources } = detailQuery.data;
  const approved = resources.filter((r) => r.status === 'approved');
  const counts = countByType(approved);
  const sectionTitle = sectionsQuery.data?.find((s) => s.slug === lesson.section_slug)?.title;
  const tabItems = approved.filter((r) => r.type === tab);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <nav aria-label="مسیر" className="flex items-center gap-1 text-xs text-slate-400">
        <Link to="/" className="hover:text-brand-600">خانه</Link>
        <ChevronLeft size={14} aria-hidden="true" />
        <Link to="/lessons" className="hover:text-brand-600">دروس</Link>
        <ChevronLeft size={14} aria-hidden="true" />
        <span className="text-slate-600">{lesson.title}</span>
      </nav>

      <header className="mt-4 rounded-2xl border border-brand-100 bg-gradient-to-l from-brand-50 to-white p-6">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {sectionTitle && (
            <span className="rounded-full bg-brand-500 px-3 py-1 font-medium text-white">{sectionTitle}</span>
          )}
          <span className="rounded-full bg-white px-3 py-1 text-slate-500 ring-1 ring-brand-100">
            ترم {lesson.term.toLocaleString('fa-IR')}
          </span>
        </div>
        <h1 className="mt-3 text-2xl md:text-3xl">{lesson.title}</h1>
        <p className="mt-2 flex items-center gap-1.5 text-sm text-slate-500">
          <User size={15} className="text-brand-400" aria-hidden="true" />
          {lesson.professor}
          {lesson.code && <span className="text-slate-300">· {lesson.code}</span>}
        </p>
      </header>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <ResourceTabs counts={counts} active={tab} onChange={setTab} />
        <Link
          to={`/upload?lesson=${lesson.id}`}
          className="flex shrink-0 items-center gap-1.5 rounded-xl border border-brand-200 bg-brand-50 px-4 py-2 text-xs font-medium text-brand-700 transition-colors hover:bg-brand-100"
        >
          <UploadCloud size={15} aria-hidden="true" />
          آپلود برای این درس
        </Link>
      </div>

      <div role="tabpanel" className="mt-4 rounded-2xl border border-brand-100 bg-white p-4">
        {tabItems.length === 0 ? (
          <div className="flex flex-col items-center gap-3 px-2 py-10 text-center">
            <BookOpen size={32} className="text-brand-200" aria-hidden="true" />
            <p className="text-sm text-slate-500">
              برای این بخش هنوز منبعی ثبت نشده — اولین نفری باش که آپلود می‌کنه!
            </p>
            <Link
              to={`/upload?lesson=${lesson.id}`}
              className="rounded-xl bg-brand-500 px-6 py-2 text-xs text-white transition-colors hover:bg-brand-600"
            >
              آپلود منبع
            </Link>
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {tabItems.map((r) => (
              <FileRow key={r.id} resource={r} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
