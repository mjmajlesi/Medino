// مدل‌های مشترک فرانت‌اند — مطابق قرارداد API با بک‌اند Django (بند ۶ plan.md)

export type SectionSlug =
  | 'basic'
  | 'physio'
  | 'karamozi'
  | 'karvarzi'
  | 'stage'
  | 'general';

export interface Section {
  id: string;
  slug: SectionSlug;
  title: string;
  description?: string;
}

export type ResourceType = 'note' | 'video' | 'sample' | 'summary';

export type ResourceStatus = 'pending' | 'approved' | 'rejected';

export interface Lesson {
  id: string;
  section_slug: SectionSlug;
  title: string;
  professor: string;
  term: number;
  code?: string;
}

export interface Resource {
  id: string;
  lesson_id: string;
  type: ResourceType;
  title: string;
  description?: string;
  file_url: string;
  duration?: string;
  status: ResourceStatus;
  uploader_name: string;
  created_at: string;
}

export interface LessonDetail {
  lesson: Lesson;
  resources: Resource[];
}

/** پارامترهای فیلتر/سرچ لیست دروس — mirror کوئری‌پارام‌های GET /api/lessons/ */
export interface LessonFilters {
  section?: SectionSlug | '';
  search?: string;
  professor?: string;
  type?: ResourceType | '';
  term?: number | '';
}

export interface StudentUser {
  first_name: string;
  last_name: string;
  student_no: string;
  entry_year: string;
  current_term: string;
}

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  note: 'جزوه',
  video: 'فیلم آموزشی',
  sample: 'نمونه سوال',
  summary: 'خلاصه‌نویسی',
};
