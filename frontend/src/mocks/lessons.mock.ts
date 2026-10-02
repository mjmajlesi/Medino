import type { Lesson } from '../types/models';

// views و created_at نمایشی‌اند تا مرتب‌سازی قابل تست باشد — مقادیر واقعی از API می‌آید
export const lessonsMock: Lesson[] = [
  { id: 'les-anatomy', section_slug: 'basic', title: 'آناتومی', professor: 'دکتر رضایی', term: 1, code: 'BAS-101', views: 1240, created_at: '2026-06-10' },
  { id: 'les-biochem', section_slug: 'basic', title: 'بیوشیمی', professor: 'دکتر کریمی', term: 1, code: 'BAS-102', views: 860, created_at: '2026-05-20' },
  { id: 'les-physio', section_slug: 'basic', title: 'فیزیولوژی', professor: 'دکتر احمدی', term: 2, code: 'BAS-201', views: 975, created_at: '2026-04-11' },
  { id: 'les-cardio', section_slug: 'physio', title: 'فیزیوپاتولوژی قلب', professor: 'دکتر محمدی', term: 4, code: 'PHY-401', views: 1530, created_at: '2026-03-02' },
  { id: 'les-patho', section_slug: 'physio', title: 'پاتولوژی عمومی', professor: 'دکتر حسینی', term: 4, code: 'PHY-402', views: 640, created_at: '2026-02-18' },
  { id: 'les-semio', section_slug: 'karamozi', title: 'سمیولوژی', professor: 'دکتر نادری', term: 5, code: 'KAR-501', views: 720, created_at: '2026-02-14' },
  { id: 'les-internal', section_slug: 'karvarzi', title: 'داخلی ۱', professor: 'دکتر صادقی', term: 7, code: 'KAV-701', views: 1890, created_at: '2026-01-30' },
  { id: 'les-surgery', section_slug: 'karvarzi', title: 'جراحی عمومی', professor: 'دکتر موسوی', term: 7, code: 'KAV-702', views: 540, created_at: '2026-01-22' },
  { id: 'les-pedia', section_slug: 'stage', title: 'اطفال', professor: 'دکتر فرهادی', term: 9, code: 'STG-901', views: 480, created_at: '2026-01-15' },
  { id: 'les-obgyn', section_slug: 'stage', title: 'زنان و زایمان', professor: 'دکتر عزیزی', term: 9, code: 'STG-902', views: 510, created_at: '2026-01-10' },
  { id: 'les-lang', section_slug: 'general', title: 'زبان عمومی پزشکی', professor: 'دکتر اکبری', term: 1, code: 'GEN-101', views: 320, created_at: '2026-06-01' },
  { id: 'les-ethics', section_slug: 'general', title: 'اخلاق پزشکی', professor: 'دکتر یوسفی', term: 2, code: 'GEN-201', views: 290, created_at: '2026-05-05' },
];
