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
  /** ترم اعلام‌نشده برای درس‌های جدید (نامشخص) */
  term?: number;
  code?: string;
  /** از API می‌آید — در Mock مقدار نمایشی دارد */
  views?: number;
  /** از API می‌آید — در Mock مقدار نمایشی دارد */
  created_at?: string;
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
  sort?: 'newest' | 'popular' | '';
}

export interface StudentUser {
  first_name: string;
  last_name: string;
  student_no: string;
  // بک‌اند گاهی عدد و گاهی رشته می‌فرستد (me در برابر لیست ادمین) — هر دو پشتیبانی می‌شود
  entry_year: string | number;
  current_term: string | number;
  /** از API می‌آید (is_staff جنگو) — در Mock فقط ادمین نمایشی true است */
  is_staff?: boolean;
  /** از API می‌آید — فقط نمایشی؛ از طریق فرانت قابل تغییر نیست */
  is_superuser?: boolean;
}

/** ردیف کاربر در لیست مدیریت ادمین‌ها */
export interface StaffUser extends StudentUser {
  id: string;
}

/** پاسخ صفحه‌بندی‌شده DRF */
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type AdminRoleFilter = 'all' | 'student' | 'staff' | 'superuser';

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  note: 'جزوه',
  video: 'فیلم آموزشی',
  sample: 'نمونه سوال',
  summary: 'خلاصه‌نویسی',
};
