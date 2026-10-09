# مدینو (Medino) — مرجع آموزشی دانشجویان پزشکی

![frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite%20%2B%20Tailwind-0ea5e9)
![backend](https://img.shields.io/badge/backend-Django%20REST-092e20)
![lang](https://img.shields.io/badge/lang-fa%20RTL-blue)
![license](https://img.shields.io/badge/license-MIT-green)

پلتفرم فارسی و راست‌چین برای دانشجویان پزشکی: جزوات، فیلم‌های آموزشی، نمونه سوالات و
خلاصه‌نویسی‌ها — از علوم پایه تا استاژری، به‌علاوه دروس عمومی.

> `Education • For • Better Tomorrow`

## ✨ امکانات

- 🏠 صفحه اصلی با اسلایدر، جستجوی سریع، نوار آمار زنده و ۶ کارت بخش
- 🔍 جستجو (نام درس/استاد) + ۵ فیلتر (بخش، نوع منبع، استاد، ترم، مرتب‌سازی) با لینک اشتراکی
- 📚 صفحه هر درس با ۴ تب: جزوه / فیلم آموزشی / نمونه سوال / خلاصه‌نویسی
- ⬆️ آپلود منبع توسط دانشجو + صف **تایید ادمین** + آپلود مستقیم ادمین
- 👤 ثبت‌نام/ورود با شماره دانشجویی (JWT + رفرش خودکار) و پروفایل با لیست آپلودها
- 🌙 دارک مود ملایم با ذخیره انتخاب کاربر

## 🗂️ ساختار ریپو

```
Medino/
├── frontend/          # React + Vite + TS + Tailwind v4
├── backend/           # Django REST (JWT via simplejwt)
├── docs/              # مستندات (از جمله آدیت قرارداد API)
├── plan.md            # پلن و قرارداد API (مرجع حقیقت)
├── task.md            # تسک‌بندی و لاگ پیشرفت
└── LICENSE            # MIT
```

## 🚀 شروع سریع (توسعه لوکال)

### بک‌اند — `http://127.0.0.1:8000`

راهنمای کامل در [`backend/README.md`](backend/README.md). خلاصه:

```bash
cd backend
python -m venv .venv
# ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
# ساخت backend/.env از روی .env.example (طبق همان فایل)
python manage.py migrate
python manage.py seed_academics     # سید ۶ بخش + درس‌ها
python manage.py createsuperuser    # یوزر staff برای پنل ادمین
python manage.py runserver
```

### فرانت‌اند — `http://localhost:5173`

```bash
cd frontend
npm install
cp .env.example .env    # بعد مقادیر واقعی را بگذار
npm run dev
```

| متغیر | توسعه با Mock | اتصال واقعی |
|---|---|---|
| `VITE_USE_MOCK` | `true` | `false` |
| `VITE_API_URL` | — | `http://127.0.0.1:8000/api` |

> ⚠️ **هماهنگی سقف آپلود:** سقف فرانت (۵۰MB) و `MAX_UPLOAD_SIZE` بک‌اند باید یکی باشند؛
> الان مقدار نمونه بک‌اند ۲۰۰MB است — قبل از دیپلوی یکی را انتخاب و هر دو را ست کنید.
> `CORS_ALLOWED_ORIGINS` بک‌اند هم باید origin دقیق فرانت (با scheme و پورت) را داشته باشد.

## 👥 نقش‌ها

| نقش | دسترسی |
|---|---|
| مهمان | مشاهده خانه، دروس، جزئیات، سرچ/فیلتر |
| دانشجو (لاگین) | آپلود منبع، پروفایل و لیست آپلودها |
| ادمین (`is_staff`) | داشبورد `/admin`، تایید/رد صف، آپلود مستقیم |

## 📦 بیلد و دیپلوی فرانت

```bash
cd frontend
npm run build     # خروجی: dist/ (route-level code-split)
npm run preview   # پیش‌نمایش لوکال
```

روی هاست استاتیک (Nginx/Netlify/Vercel/cPanel) محتویات `dist/` را سرو کنید و همه روت‌ها را به
`index.html` برگردانید (`try_files $uri /index.html;`). بعد از هر تغییر `.env` دوباره build بگیرید.

## 🤝 همکاری

- قرارداد کامل API در [`plan.md`](plan.md) بند ۷ است؛ آدیت سازگاری در [`docs/`](docs/).
- فرانت بدون بک‌اند هم با `VITE_USE_MOCK=true` کامل کار می‌کند.

## 📄 لایسنس

MIT — فایل [`LICENSE`](LICENSE).
