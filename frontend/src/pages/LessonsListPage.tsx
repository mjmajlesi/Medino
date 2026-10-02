import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import type { ResourceType, SectionSlug } from '../types/models';
import EmptyState from '../components/Lessons/EmptyState';
import FilterPanel from '../components/Lessons/FilterPanel';
import type { FilterState } from '../components/Lessons/FilterPanel';
import LessonCard from '../components/Lessons/LessonCard';
import SearchBar from '../components/Lessons/SearchBar';
import { useDebounce } from '../hooks/useDebounce';
import { getLessons, getSections } from '../services/lessons.service';

const EMPTY_FILTERS: FilterState = { section: '', type: '', professor: '', term: '', sort: '' };

const SECTIONS: SectionSlug[] = ['basic', 'physio', 'karamozi', 'karvarzi', 'stage', 'general'];
const TYPES: ResourceType[] = ['note', 'video', 'sample', 'summary'];
const SORTS: NonNullable<FilterState['sort']>[] = ['newest', 'popular'];

function readState(params: URLSearchParams): { search: string; filters: FilterState } {
  const section = params.get('section') ?? '';
  const type = params.get('type') ?? '';
  const sort = params.get('sort') ?? '';
  const termRaw = params.get('term') ?? '';
  return {
    search: params.get('search') ?? '',
    filters: {
      section: (SECTIONS.includes(section as SectionSlug) ? section : '') as SectionSlug | '',
      type: (TYPES.includes(type as ResourceType) ? type : '') as ResourceType | '',
      professor: params.get('professor') ?? '',
      term: termRaw === '' || Number.isNaN(Number(termRaw)) ? '' : Number(termRaw),
      sort: (SORTS.includes(sort as never) ? sort : '') as FilterState['sort'],
    },
  };
}

function writeState(params: URLSearchParams, search: string, f: FilterState): URLSearchParams {
  const next = new URLSearchParams(params);
  const set = (k: string, v: string) => (v ? next.set(k, v) : next.delete(k));
  set('search', search.trim());
  set('section', f.section);
  set('type', f.type);
  set('professor', f.professor);
  set('term', f.term === '' ? '' : String(f.term));
  set('sort', f.sort);
  return next;
}

export default function LessonsListPage() {
  // URL منبع حقیقته — هر تغییری (تایپ، فیلتر، بک‌باتن) از همین‌جا می‌گذرد
  const [params, setParams] = useSearchParams();
  const { search, filters } = useMemo(() => readState(params), [params]);

  // اینپوت سرچ آنی تایپ می‌شود، ولی با debounce وارد URL (و کوئری) می‌شود
  const [input, setInput] = useState(search);
  const debouncedInput = useDebounce(input.trim(), 400);

  useEffect(() => {
    setParams((prev) => writeState(prev, debouncedInput, readState(prev).filters), {
      replace: true,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedInput]);

  // سینک از بیرون (بک‌باتن، لینک مستقیم) — وقتی کاربر در حال تایپ است دست نمی‌زنیم
  // تا debounce عقب‌مانده متن در حال تایپ را پاک نکند
  useEffect(() => {
    if (document.activeElement?.id !== 'lesson-search') setInput(search);
  }, [search]);

  const lessonsQuery = useQuery({
    queryKey: ['lessons', { search, ...filters }],
    queryFn: () => getLessons({ search, ...filters }),
  });
  const sectionsQuery = useQuery({ queryKey: ['sections'], queryFn: getSections });
  const allLessonsQuery = useQuery({ queryKey: ['lessons', 'all'], queryFn: () => getLessons({}) });

  const professors = useMemo(
    () => [...new Set((allLessonsQuery.data ?? []).map((l) => l.professor))],
    [allLessonsQuery.data],
  );
  const terms = useMemo(
    () => [...new Set((allLessonsQuery.data ?? []).map((l) => l.term))].sort((a, b) => a - b),
    [allLessonsQuery.data],
  );
  const activeCount = [filters.section, filters.type, filters.professor, filters.term, filters.sort].filter(
    (v) => v !== '',
  ).length;

  const lessons = lessonsQuery.data ?? [];

  const patchFilters = (patch: Partial<FilterState>) => {
    setParams((prev) => {
      const cur = readState(prev);
      return writeState(prev, cur.search, { ...cur.filters, ...patch });
    });
  };

  const resetAll = () => {
    setInput('');
    setParams({});
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-xl md:text-2xl">دروس</h1>
      <p className="mt-1 text-sm text-slate-500">
        {lessonsQuery.isPending
          ? 'در حال جستجو...'
          : `${lessons.length.toLocaleString('fa-IR')} درس پیدا شد`}
      </p>

      <div className="mt-4">
        <SearchBar value={input} onChange={setInput} />
      </div>

      <div className="mt-4">
        <FilterPanel
          filters={filters}
          onChange={patchFilters}
          onReset={() => setParams((prev) => writeState(prev, readState(prev).search, EMPTY_FILTERS))}
          sections={sectionsQuery.data ?? []}
          professors={professors}
          terms={terms}
          activeCount={activeCount}
        />
      </div>

      <div className="mt-6">
        {lessonsQuery.isPending ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-48 animate-pulse rounded-2xl bg-brand-50" />
            ))}
          </div>
        ) : lessonsQuery.isError ? (
          <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-6 text-center text-red-600">
            خطا در بارگذاری دروس. لطفا دوباره تلاش کنید.
          </p>
        ) : lessons.length === 0 ? (
          <EmptyState onReset={resetAll} />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {lessons.map((l) => (
              <LessonCard key={l.id} lesson={l} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
