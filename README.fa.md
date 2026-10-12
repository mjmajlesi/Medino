# مدینو — پلتفرم آموزشی دانشجویان پزشکی

![frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite%20%2B%20Tailwind-0ea5e9)
![backend](https://img.shields.io/badge/backend-Django%20REST%20%2B%20PostgreSQL-092e20)
![lang](https://img.shields.io/badge/lang-fa%20RTL-blue)
![license](https://img.shields.io/badge/license-MIT-green)

> 🇬🇧 **English version:** [README.md](README.md)

مدینو پلتفرم فارسی و راست‌چین برای دانشجویان پزشکی است: جزوات، فیلم‌های آموزشی،
نمونه سوالات و خلاصه‌نویسی‌ها — از علوم پایه تا کارورزی — به‌علاوه دروس عمومی.

> `Education • For • Better Tomorrow`

## ✨ امکانات

- 🏠 صفحه اصلی با اسلایدر، جستجوی سریع، آمار زنده و ۶ کارت بخش
- 🔍 جستجو (نام درس/استاد) + ۵ فیلتر (بخش، نوع منبع، استاد، ترم، مرتب‌سازی) با لینک اشتراکی
- 📚 صفحه هر درس با ۴ تب: جزوه / فیلم آموزشی / نمونه سوال / خلاصه‌نویسی
- ⬆️ آپلود منبع توسط دانشجو + صف **تایید ادمین** + انتشار مستقیم ادمین
- 👤 ورود با شماره دانشجویی (JWT با رفرش خودکار) و پروفایل با لیست آپلودها
- 🛠️ مدیریت دروس توسط ادمین (ساخت / ویرایش / حذف)
- 🌙 دارک مود ملایم با ذخیره انتخاب کاربر

## 🗂️ ساختار ریپو

```
Medino/
├── frontend/          # React + Vite + TS + Tailwind v4
├── backend/           # Django REST + SimpleJWT ([راهنمای بک‌اند](backend/README.md))
├── docs/              # مستندات (آدیت قرارداد API + خروجی سید دروس)
├── plan.md            # پلن و قرارداد API (مرجع حقیقت)
├── task.md            # تسک‌بندی و لاگ پیشرفت
└── LICENSE            # MIT
```

## 🚀 شروع سریع (داکر — پیشنهادی)

پیش‌نیاز: Docker Engine و Docker Compose. از روت پروژه:

```bash
cp .env.docker.example .env.docker
chmod 600 .env.docker
# داخل .env.docker مقدار SECRET_KEY و POSTGRES_PASSWORD را عوض کنید
docker compose --env-file .env.docker config --quiet
docker compose --env-file .env.docker build
docker compose --env-file .env.docker up -d --wait
docker compose --env-file .env.docker ps
```

ساختار کانتینرها: مرورگر ← Nginx روی `:8080` ← فرانت (SPA) و `/api/` ← جنگو ← PostgreSQL.
فقط Nginx پورت هاست دارد. بعد از بالا آمدن:

- سایت: `http://localhost:8080/`
- API: `http://localhost:8080/api/` — سلامت: `/healthz` و `/api/health/`
- ادمین جنگو: `http://localhost:8080/django-admin/` (صفحه مدیریت ری‌اکت: `/admin`)

سید دروس و superuser خودکار ساخته **نمی‌شوند**:

```bash
docker compose --env-file .env.docker run --rm backend python manage.py seed_academics
docker compose --env-file .env.docker run --rm backend python manage.py createsuperuser
```

کاتالوگ معتبر ۷۵ درس در [`docs/lessons-seed.json`](docs/lessons-seed.json) است.

## 💻 توسعه لوکال (بدون داکر)

### فرانت‌اند — `http://localhost:5173`

```bash
cd frontend
npm install
cp .env.example .env    # بعد مقادیر واقعی را بگذارید
npm run dev             # بیلد: npm run build | پیش‌نمایش: npm run preview
```

| متغیر | حالت Mock | اتصال واقعی |
|---|---|---|
| `VITE_USE_MOCK` | `true` | `false` |
| `VITE_API_URL` | — | `http://127.0.0.1:8000/api` |

با `VITE_USE_MOCK=true` فرانت کاملا آفلاین با دیتای نمایشی کار می‌کند.

### بک‌اند — `http://127.0.0.1:8000`

راهنمای کامل: [`backend/README.md`](backend/README.md). خلاصه: venv ← نصب requirements ←
ساخت `backend/.env` شخصی ← `migrate` ← `seed_academics` ← `runserver`.
`CORS_ALLOWED_ORIGINS` باید origin دقیق فرانت (با scheme و پورت) باشد.

> ⚠️ **هماهنگی سقف آپلود:** سقف فرانت (۵۰MB) و `MAX_UPLOAD_SIZE` بک‌اند باید یکی باشند.

## 👥 نقش‌ها

| نقش | دسترسی |
|---|---|
| مهمان | خانه، دروس، جزئیات، سرچ/فیلتر |
| دانشجو (لاگین) | آپلود منبع، پروفایل و لیست آپلودها |
| ادمین (`is_staff`) | داشبورد `/admin`، تایید/رد صف، انتشار مستقیم، مدیریت دروس |

## 📡 قرارداد API

قرارداد کامل در [`plan.md`](plan.md) بند ۷؛ آدیت سازگاری در [`docs/`](docs/).
نکات کلیدی: احراز هویت JWT با رفرش، `is_staff` در جواب auth، `ordering` در سرچ،
آپلود `direct` ادمین، تحویل فایل بر اساس تایید.

## 📄 لایسنس

MIT — فایل [`LICENSE`](LICENSE).
