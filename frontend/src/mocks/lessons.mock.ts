import type { Lesson } from '../types/models';

// لیست رسمی کارفرما — ۵ گروه، ۷۵ درس (آبان ۱۴۰۵)
// استاد/ترم اعلام نشده → professor «—» و term نامشخص (اختیاری در مدل)
const D = '2026-10-11';

const basicTitles = [
  'آناتومی', 'بافت‌شناسی', 'جنین‌شناسی', 'فیزیولوژی', 'بیوشیمی',
  'زیست‌شناسی سلولی و مولکولی', 'ژنتیک پزشکی', 'فیزیک پزشکی', 'بیوفیزیک',
  'میکروب‌شناسی', 'باکتری‌شناسی', 'ویروس‌شناسی', 'انگل‌شناسی', 'قارچ‌شناسی',
  'ایمنی‌شناسی', 'آسیب‌شناسی عمومی', 'آسیب‌شناسی اختصاصی', 'فارماکولوژی',
  'اپیدمیولوژی', 'آمار زیستی', 'بهداشت عمومی', 'تغذیه',
  'زبان تخصصی پزشکی', 'اصطلاحات پزشکی',
];

const physioTitles = [
  'فیزیوپاتولوژی قلب و عروق', 'فیزیوپاتولوژی تنفس', 'فیزیوپاتولوژی کلیه',
  'فیزیوپاتولوژی گوارش', 'فیزیوپاتولوژی غدد درون‌ریز', 'فیزیوپاتولوژی خون',
  'فیزیوپاتولوژی روماتولوژی', 'فیزیوپاتولوژی اعصاب', 'فیزیوپاتولوژی روان',
  'سمیولوژی', 'فارماکولوژی', 'آسیب‌شناسی بالینی', 'مهارت‌های بالینی',
];

const karamoziTitles = [
  'داخلی', 'جراحی عمومی', 'قلب و عروق', 'بیماری‌های عفونی', 'مغز و اعصاب',
  'ارتوپدی', 'اورولوژی', 'کودکان', 'زنان و زایمان', 'چشم‌پزشکی',
  'گوش، حلق و بینی', 'پوست', 'روان‌پزشکی', 'رادیولوژی', 'بیهوشی',
  'پزشکی قانونی', 'بهداشت', 'پزشکی اورژانس',
];

const karvarziTitles = [
  'داخلی', 'جراحی عمومی', 'کودکان', 'زنان و زایمان', 'اورژانس',
  'روان‌پزشکی', 'بیماری‌های عفونی', 'قلب و عروق', 'مغز و اعصاب', 'ارتوپدی',
  'اورولوژی', 'چشم‌پزشکی', 'گوش، حلق و بینی', 'پوست', 'رادیولوژی',
  'بیهوشی', 'پزشکی قانونی', 'پزشکی اجتماعی',
];

const generalTitles = ['معارف و اندیشه اسلامی', 'زبان و ادبیات'];

// مشخصات شناخته‌شده قبلی (حفظ می‌شود تا منابع Mock سر جایشان بمانند)
const known: Record<string, { professor: string; term?: number; code?: string; views?: number }> = {
  'basic:آناتومی': { professor: 'دکتر رضایی', term: 1, code: 'BAS-101', views: 1240 },
  'basic:بیوشیمی': { professor: 'دکتر کریمی', term: 1, code: 'BAS-102', views: 860 },
  'basic:فیزیولوژی': { professor: 'دکتر احمدی', term: 2, code: 'BAS-201', views: 975 },
  'physio:فیزیوپاتولوژی قلب و عروق': { professor: 'دکتر محمدی', term: 4, code: 'PHY-401', views: 1530 },
  'physio:سمیولوژی': { professor: 'دکتر نادری', term: 5, code: 'KAR-501', views: 720 },
  'karvarzi:داخلی': { professor: 'دکتر صادقی', term: 7, code: 'KAV-701', views: 1890 },
};

function build(slug: Lesson['section_slug'], titles: string[]): Lesson[] {
  return titles.map((title, i) => {
    const k = known[`${slug}:${title}`];
    const id = `${slug}-${String(i + 1).padStart(2, '0')}`;
    const lesson: Lesson = {
      id: `les-${id}`,
      section_slug: slug,
      title,
      professor: k?.professor ?? '—',
      created_at: D,
      views: k?.views ?? 0,
    };
    if (k?.term !== undefined) lesson.term = k.term;
    if (k?.code !== undefined) lesson.code = k.code;
    return lesson;
  });
}

export const lessonsMock: Lesson[] = [
  ...build('basic', basicTitles),
  ...build('physio', physioTitles),
  ...build('karamozi', karamoziTitles),
  ...build('karvarzi', karvarziTitles),
  ...build('general', generalTitles),
];
