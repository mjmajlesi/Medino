import type {
  LessonDetail,
  LessonFilters,
  Resource,
  Section,
} from '../types/models';
import type { Lesson } from '../types/models';
import { lessonsMock } from '../mocks/lessons.mock';
import { resourcesMock } from '../mocks/resources.mock';
import { sectionsMock } from '../mocks/sections.mock';
import api, { USE_MOCK } from './api';

const delay = (ms = 250) => new Promise((r) => setTimeout(r, ms));

function applyFilters(lessons: Lesson[], f: LessonFilters): Lesson[] {
  const q = (f.search ?? '').trim();
  const prof = (f.professor ?? '').trim();
  const filtered = lessons.filter((l) => {
    if (f.section && l.section_slug !== f.section) return false;
    if (q && !`${l.title} ${l.professor}`.includes(q)) return false;
    if (prof && !l.professor.includes(prof)) return false;
    if (f.term !== undefined && f.term !== '' && l.term !== Number(f.term))
      return false;
    if (f.type) {
      const hasType = resourcesMock.some(
        (r: Resource) =>
          r.lesson_id === l.id && r.type === f.type && r.status === 'approved',
      );
      if (!hasType) return false;
    }
    return true;
  });
  if (f.sort === 'newest') {
    return [...filtered].sort((a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? ''));
  }
  if (f.sort === 'popular') {
    return [...filtered].sort((a, b) => (b.views ?? 0) - (a.views ?? 0));
  }
  return filtered;
}

export async function getSections(): Promise<Section[]> {
  if (USE_MOCK) {
    await delay();
    return sectionsMock;
  }
  const { data } = await api.get<Section[]>('/sections/');
  return data;
}

export async function getLessons(filters: LessonFilters = {}): Promise<Lesson[]> {
  if (USE_MOCK) {
    await delay();
    return applyFilters(lessonsMock, filters);
  }
  const { data } = await api.get<Lesson[]>('/lessons/', {
    params: {
      section: filters.section || undefined,
      search: filters.search || undefined,
      professor: filters.professor || undefined,
      type: filters.type || undefined,
      term: filters.term === '' ? undefined : filters.term,
      ordering:
        filters.sort === 'newest'
          ? '-created_at'
          : filters.sort === 'popular'
            ? '-views'
            : undefined,
    },
  });
  return data;
}

export async function getLessonDetail(id: string): Promise<LessonDetail> {
  if (USE_MOCK) {
    await delay();
    const lesson = lessonsMock.find((l) => l.id === id);
    if (!lesson) throw new Error('درس پیدا نشد');
    const resources = resourcesMock.filter((r) => r.lesson_id === id);
    return { lesson, resources };
  }
  const { data } = await api.get<LessonDetail>(`/lessons/${id}/`);
  return data;
}

export function countByType(resources: Resource[]) {
  return {
    note: resources.filter((r) => r.type === 'note').length,
    video: resources.filter((r) => r.type === 'video').length,
    sample: resources.filter((r) => r.type === 'sample').length,
    summary: resources.filter((r) => r.type === 'summary').length,
  };
}

export interface SiteStats {
  lessons: number;
  notes: number;
  videos: number;
  samples: number;
  summaries: number;
}

/* ------------------------------------------------------------------ */
/* مدیریت دروس (staff) — قرارداد بک‌اند (هنوز پیاده نشده، TASK-21):     */
/*   POST   /api/lessons/      {section_slug, title, professor, term, code?} -> 201 Lesson */
/*   PUT    /api/lessons/:id/  {...} -> 200 Lesson                               */
/*   DELETE /api/lessons/:id/  -> 204 (رفتار با منابع درس با بک‌اند است)        */
/* هر سه فقط برای is_staff. با آماده شدن بک‌اند، شاخه واقعی همین‌جا وصل می‌شود. */
/* ------------------------------------------------------------------ */

export interface LessonInput {
  section_slug: Lesson['section_slug'];
  title: string;
  professor: string;
  term: number;
  code?: string;
}

export async function createLesson(input: LessonInput): Promise<Lesson> {
  if (USE_MOCK) {
    await delay();
    const created: Lesson = { ...input, id: `les-mock-${Date.now()}` };
    lessonsMock.unshift(created);
    return created;
  }
  const { data } = await api.post<Lesson>('/lessons/', input);
  return data;
}

export async function updateLesson(id: string, input: LessonInput): Promise<Lesson> {
  if (USE_MOCK) {
    await delay();
    const idx = lessonsMock.findIndex((l) => l.id === id);
    if (idx === -1) throw new Error('درس پیدا نشد');
    lessonsMock[idx] = { ...lessonsMock[idx], ...input };
    return lessonsMock[idx];
  }
  const { data } = await api.put<Lesson>(`/lessons/${id}/`, input);
  return data;
}

export async function deleteLesson(id: string): Promise<void> {
  if (USE_MOCK) {
    await delay();
    const idx = lessonsMock.findIndex((l) => l.id === id);
    if (idx === -1) throw new Error('درس پیدا نشد');
    lessonsMock.splice(idx, 1);
    return;
  }
  await api.delete(`/lessons/${id}/`);
}

/**
 * آمار کلی سایت — فقط منابع «تاییدشده» شمرده می‌شوند،
 * پس با هر تایید ادمین خودکار بزرگ می‌شود (از صفر شروع می‌شود).
 */
export async function getStats(): Promise<SiteStats> {
  if (USE_MOCK) {
    await delay();
    const approved = resourcesMock.filter((r) => r.status === 'approved');
    const byType = countByType(approved);
    return {
      lessons: lessonsMock.length,
      notes: byType.note,
      videos: byType.video,
      samples: byType.sample,
      summaries: byType.summary,
    };
  }
  const { data } = await api.get<SiteStats>('/stats/');
  return data;
}
