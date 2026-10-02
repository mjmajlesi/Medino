import type { Lesson } from '../types/models';

export const lessonsMock: Lesson[] = [
  { id: 'les-anatomy', section_slug: 'basic', title: 'آناتومی', professor: 'دکتر رضایی', term: 1, code: 'BAS-101' },
  { id: 'les-biochem', section_slug: 'basic', title: 'بیوشیمی', professor: 'دکتر کریمی', term: 1, code: 'BAS-102' },
  { id: 'les-physio', section_slug: 'basic', title: 'فیزیولوژی', professor: 'دکتر احمدی', term: 2, code: 'BAS-201' },
  { id: 'les-cardio', section_slug: 'physio', title: 'فیزیوپاتولوژی قلب', professor: 'دکتر محمدی', term: 4, code: 'PHY-401' },
  { id: 'les-patho', section_slug: 'physio', title: 'پاتولوژی عمومی', professor: 'دکتر حسینی', term: 4, code: 'PHY-402' },
  { id: 'les-semio', section_slug: 'karamozi', title: 'سمیولوژی', professor: 'دکتر نادری', term: 5, code: 'KAR-501' },
  { id: 'les-internal', section_slug: 'karvarzi', title: 'داخلی ۱', professor: 'دکتر صادقی', term: 7, code: 'KAV-701' },
  { id: 'les-surgery', section_slug: 'karvarzi', title: 'جراحی عمومی', professor: 'دکتر موسوی', term: 7, code: 'KAV-702' },
  { id: 'les-pedia', section_slug: 'stage', title: 'اطفال', professor: 'دکتر فرهادی', term: 9, code: 'STG-901' },
  { id: 'les-obgyn', section_slug: 'stage', title: 'زنان و زایمان', professor: 'دکتر عزیزی', term: 9, code: 'STG-902' },
  { id: 'les-lang', section_slug: 'general', title: 'زبان عمومی پزشکی', professor: 'دکتر اکبری', term: 1, code: 'GEN-101' },
  { id: 'les-ethics', section_slug: 'general', title: 'اخلاق پزشکی', professor: 'دکتر یوسفی', term: 2, code: 'GEN-201' },
];
