import type { Resource } from '../types/models';

export const resourcesMock: Resource[] = [
  // آناتومی — هر ۴ نوع منبع
  { id: 'res-a1', lesson_id: 'les-anatomy', type: 'note', title: 'جزوه کامل آناتومی تنه', description: 'گردآوری ترم بهار', file_url: '#', status: 'approved', uploader_name: 'علی مرادی', created_at: '2026-06-10' },
  { id: 'res-a2', lesson_id: 'les-anatomy', type: 'video', title: 'آموزش تصویری آناتومی اندام', duration: '45:00', file_url: '#', status: 'approved', uploader_name: 'سارا احمدی', created_at: '2026-06-12' },
  { id: 'res-a3', lesson_id: 'les-anatomy', type: 'sample', title: 'نمونه سوالات پایان‌ترم ۱۴۰۴', file_url: '#', status: 'approved', uploader_name: 'علی مرادی', created_at: '2026-06-15' },
  { id: 'res-a4', lesson_id: 'les-anatomy', type: 'summary', title: 'خلاصه ۲۰ صفحه‌ای استخوان‌شناسی', file_url: '#', status: 'approved', uploader_name: 'نگار کریمی', created_at: '2026-06-18' },
  // بقیه دروس — یکی دو منبع
  { id: 'res-b1', lesson_id: 'les-biochem', type: 'note', title: 'جزوه بیوشیمی ساختاری', file_url: '#', status: 'approved', uploader_name: 'سارا احمدی', created_at: '2026-05-20' },
  { id: 'res-b2', lesson_id: 'les-biochem', type: 'sample', title: 'تست‌های میان‌ترم بیوشیمی', file_url: '#', status: 'approved', uploader_name: 'علی مرادی', created_at: '2026-05-25' },
  { id: 'res-p1', lesson_id: 'les-physio', type: 'video', title: 'فیزیولوژی قلب و عروق', duration: '60:00', file_url: '#', status: 'approved', uploader_name: 'نگار کریمی', created_at: '2026-04-11' },
  { id: 'res-c1', lesson_id: 'les-cardio', type: 'note', title: 'جزوه فیزیوپات قلب دکتر محمدی', file_url: '#', status: 'approved', uploader_name: 'علی مرادی', created_at: '2026-03-02' },
  // یک مورد pending برای تست پنل ادمین (TASK-15)
  { id: 'res-c2', lesson_id: 'les-cardio', type: 'summary', title: 'خلاصه نارسایی قلبی (در انتظار تایید)', file_url: '#', status: 'pending', uploader_name: 'رضا نادری', created_at: '2026-09-28' },
  { id: 'res-s1', lesson_id: 'les-semio', type: 'note', title: 'جزوه معاینه فیزیکی', file_url: '#', status: 'approved', uploader_name: 'سارا احمدی', created_at: '2026-02-14' },
  { id: 'res-i1', lesson_id: 'les-internal', type: 'sample', title: 'سوالات پرتکرار داخلی', file_url: '#', status: 'approved', uploader_name: 'نگار کریمی', created_at: '2026-01-30' },
  { id: 'res-l1', lesson_id: 'les-lang', type: 'note', title: 'لغات پرکاربرد پزشکی', file_url: '#', status: 'approved', uploader_name: 'علی مرادی', created_at: '2026-06-01' },
];
