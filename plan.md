# پلن نهایی پروژه Medino — بخش فرانت‌اند

> تاریخ: 2026-10-01 | وضعیت: نهایی | تکنولوژی قطعی شده با کارفرما/تیم

## ۱. معرفی پروژه
وب‌سایت آموزشی **مدینو (Medino)** برای دانشجویان پزشکی.
فرانت‌اند در پوشه `frontend/` با **React + Vite** ساخته می‌شود.
بک‌اند و داوپس با رفیق تیم (Django REST Framework) است. فایل‌ها روی همان سرور بک‌اند ذخیره می‌شوند.

## ۲. ساختار آموزشی سایت (قطعی)
۶ بخش:
1. علوم پایه
2. فیزیوپاتولوژی
3. کارآموزی
4. کارورزی (اینترنی)
5. استاژری
6. دروس عمومی (بخش فرعی)

سلسله‌مراتب:
```
بخش (Section) -> درس (Lesson) -> منابع:
  - جزوات (PDF / فایل)
  - فیلم آموزشی (ویدیو / لینک)
  - نمونه سوال
  - خلاصه‌نویسی‌ها
```

## ۳. نیازمندی‌های کارفرما (۹ مورد + تفسیر فنی)
1. اسم سایت: مدینو، مخاطب دانشجویان پزشکی.
2. ۵ بخش اصلی + ۱ بخش فرعی عمومی (مجموع ۶ کارت در صفحه اصلی/بخش‌ها).
3. **فیلترینگ + سرچ دروس — پراهمیت.** سرچ روی نام درس + نام استاد + تگ. فیلتر روی بخش، نوع منبع، استاد، ترم.
4. هر درس ۴ تب منبعی دارد (جزوه / فیلم / نمونه‌سوال / خلاصه).
5. آپلود توسط یوزر + تایید ادمین + آپلود مستقیم ادمین.
   فلو: `upload (pending) -> admin review -> approve/reject -> publish`
6. فیلدهای ثبت‌نام/لاگین (تفسیر ما — چون «نام درس و استاد» برای لاگین معنی ندارد):
   - لاگین: شماره دانشجویی + رمز عبور (JWT)
   - ثبت‌نام/پروفایل: نام، نام خانوادگی، شماره دانشجویی، سال ورودی، ترم فعلی
   - نام درس + نام استاد فقط در **فرم آپلود** اجباری‌اند، نه در لاگین.
7. دیزاین: تم سفید + آبی کم‌رنگ. راست‌چین (RTL)، فونت وزیرمتن.
8. لوگو طراحی شده، فعلا `placeholder` تا فایل اصلی برسد. مسیر: `frontend/src/assets/logo.svg`
9. صفحه اصلی: هدر + اسلایدر ۳ اسلایدی (Swiper، autoplay + دکمه + دات).

## ۴. استک فنی قطعی
```
frontend/
  Vite + React + TypeScript
  react-router-dom (روتینگ)
  TailwindCSS (استایل) + clsx
  Axios + @tanstack/react-query (ارتباط با API)
  zustand (auth/store سبک)
  react-hook-form + zod (فرم + ولیدیشن)
  swiper (اسلایدر)
```
فونت: Vazirmatn از CDN یا `public/fonts`.
زبان: فارسی، `dir="rtl"`, `lang="fa"`.

## ۵. ساختار پوشه frontend (هدف نهایی)
```
frontend/
  public/ (logo placeholder, favicon)
  src/
    assets/
    components/
      Layout/ (Header, Footer, MainLayout)
      Home/ (HeroSlider, SectionCards, QuickSearch)
      Lessons/ (SearchBar, FilterPanel, LessonCard, ResourceTabs, FileRow)
      Upload/ (UploadForm)
      Admin/ (PendingTable)
      Ui/ (Button, Input, Badge, Modal, Spinner, EmptyState)
    pages/
      HomePage, SectionsPage, LessonsListPage, LessonDetailPage,
      UploadPage, LoginPage, RegisterPage, ProfilePage,
      AdminDashboardPage, AdminPendingPage, NotFoundPage
    services/ (api.ts, auth.service.ts, lessons.service.ts, uploads.service.ts)
    hooks/ (useDebounce, useAuth)
    store/ (auth.store.ts)
    types/ (models.ts مطابق مدل‌های Django)
    mocks/ (sections.mock.ts, lessons.mock.ts — تا آماده شدن API)
    styles/ (index.css با تم آبی کم‌رنگ)
  .env.example (VITE_API_URL=http://localhost:8000/api)
```

## ۶. مدل داده (برای هماهنگی با Django)
```ts
Section { id, slug, title } // slug: basic | physio | karamozi | karvarzi | stage | general
Lesson { id, section_slug, title, professor, term, code }
Resource { id, lesson_id, type: 'note'|'video'|'sample'|'summary',
  title, description, file_url, duration?, status: 'pending'|'approved'|'rejected',
  uploader_name, created_at }
User { first_name, last_name, student_no, entry_year, current_term, token }
```

## ۷. قرارداد API با بک‌اند (Django REST) — نسخه نهایی TASK-16
```
GET  /api/sections/
GET  /api/lessons/?section=<slug>&search=<q>&professor=<q>&type=<note|video|sample|summary>&term=<n>&ordering=<-created_at|-views>
     // type فقط درس‌هایی با منبع approved آن نوع؛ ordering برای سورت
GET  /api/lessons/:id/          // {lesson, resources} — فقط منابع approved
GET  /api/stats/                // {lessons, notes, videos, samples, summaries}
POST /api/uploads/              // multipart: lesson, professor, type, title, description?, file, direct?
     // جواب: {id, status: 'pending'|'approved'} — direct=true فقط برای is_staff
GET  /api/uploads/mine/        // Resource[] کاربر جاری (همه وضعیت‌ها)
GET  /api/admin/pending/       // Resource[] — فقط is_staff (هدر Bearer)
POST /api/admin/approve/:id/   // {action: 'approve'|'reject'} -> {id, status}
POST /api/auth/register/       // first_name, last_name, student_no, entry_year, current_term, password
POST /api/auth/login/          // {student_no, password}
     // جواب هر دو: {user: {first_name, last_name, student_no, entry_year, current_term, is_staff}, access, refresh}
```
⚠️ **الزامی برای بک‌اند:** فیلد `is_staff` باید در جواب login/register (و ترجیحا `/auth/me/`) باشد؛
بدون آن گارد `/admin` فرانت هیچ ادمینی را راه نمی‌دهد. آیدی‌ها رشته‌ای (numeric-string) و
تاریخ‌ها ISO کامل‌اند. فایل‌های pending/rejected فقط با توکن معتبر سرو شوند (فرانت با blob می‌گیرد).
تا آماده شدن بک‌اند: همه سرویس‌ها اول به `mocks/` وصل‌اند، با یک فلگ `USE_MOCK=true` قابل سوییچ به API واقعی.

## ۸. دیزاین سیستم
- رنگ: `bg-white` زمینه، `sky-100 / sky-200 / sky-500` تم آبی، متن `slate-800`.
- **دارک مود (EXTRA):** تاگل ماه/خورشید در هدر + `medino-theme` در localStorage + اسکریپت ضدفلش در
  `index.html`. تم تیره ملایم (slate-900/800) فقط سطوح سفید/متن/بوردر را عوض می‌کند؛ آبی برند
  دست‌نخورده. اورلی روشن اسلایدر عمدا روشن می‌ماند (خوانایی متن).
- کارت‌های ۶ بخش با آیکون + تعداد دروس.
- اسلایدر هدر: ۳ اسلاید (معرفی مدینو / جدیدترین جزوات / راهنمای آپلود).
- موبایل‌فرست، بعد دسکتاپ.
- لوگو: فعلا placeholder مربعی آبی با حرف «م».

## ۹. فازبندی (خلاصه — جزئیات در task.md)
- فاز ۰: اسکافولد پروژه
- فاز ۱: زیرساخت (روتینگ، لایه‌آوت، تم، Mock)
- فاز ۲: خانه + اسلایدر + کارت بخش‌ها
- فاز ۳: لیست دروس + سرچ و فیلتر (پرریسک‌ترین)
- فاز ۴: صفحه جزئیات درس + ۴ تب
- فاز ۵: احراز هویت
- فاز ۶: آپلود یوزر
- فاز ۷: پنل ادمین (تایید + آپلود)
- فاز ۸: اتصال نهایی به API + دیپلوی

## ۱۰. قوانین کاری (توافق با کاربر)
1. هر بار **فقط یک تسک** از `task.md` انجام می‌شود.
2. بعد از هر تسک، منتظر **تایید صریح کاربر** می‌مانیم، بعد سراغ بعدی.
3. بعد از هر تسک، گراف دانش (`graphify update`) + `plan.md`/`task.md` (ستون وضعیت) آپدیت می‌شود.
4. هیچ فایل بک‌اندی دست زده نمی‌شود. فقط `frontend/` + `plan.md` + `task.md`.

## ۱۱. graphify (نقشه دانش پروژه)
- ابزار: `@nodesify/graphify` (نصب global).
- دستورها:
  ```
  nodesify-graphify run .        // ساخت اولیه گراف
  nodesify-graphify update .      // آپدیت بعد از هر تسک
  nodesify-graphify stats         // آمار نود/اج
  ```
- خروجی در `.graphify/` (db.sqlite, graph.json, graph_report.md). این پوشه کامیت نمی‌شود (به `.gitignore` اضافه می‌شود).

## ۱۲. ریسک‌ها و تصمیم‌های باز
- [x] تکنولوژی: React+Vite — بسته شد.
- [x] ذخیره فایل: سرور Django — بسته شد.
- [ ] پخش ویدیو: فعلا `<video>` مستقیم از `file_url`. اگر فایل سنگین شد، بعدا لینک آپارات اضافه می‌شود.
- [ ] حجم آپلود: سقف نهایی بک‌اند ۵۰MB پیش‌فرض (قابل تنظیم با `MAX_UPLOAD_SIZE`) — فرانت هم ۵۰MB چک می‌کند.
- [ ] لوگوی اصلی: در انتظار فایل کارفرما.

---
*این فایل مرجع حقیقت پروژه است. هر تغییری در اسکوپ باید اول اینجا ثبت شود.*
