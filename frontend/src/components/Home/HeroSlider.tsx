import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Autoplay, Navigation, Pagination } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import slideUploadImg from '../../assets/images/bg_sec7.jpg';
import slideNewImg from '../../assets/images/images.jpg';
import slideIntroImg from '../../assets/images/umsha.webp';
import './HeroSlider.css';

interface Slide {
  badge: string;
  title: string;
  subtitle: string;
  cta: string;
  to: string;
  image: string;
  alt: string;
}

const slides: Slide[] = [
  {
    badge: 'مدینو',
    title: 'مرجع جزوات و فیلم‌های دانشجویان پزشکی',
    subtitle: 'از علوم پایه تا استاژری — همه منابع یک‌جا',
    cta: 'مشاهده دروس',
    to: '/lessons',
    image: slideIntroImg,
    alt: 'سردر دانشگاه علوم پزشکی',
  },
  {
    badge: 'تازه‌ها',
    title: 'جدیدترین جزوات و نمونه سوالات',
    subtitle: 'با جستجو و فیلتر سریع، دقیقا همون چیزی که می‌خوای',
    cta: 'جستجوی دروس',
    to: '/lessons',
    image: slideNewImg,
    alt: 'ورودی دانشگاه علوم پزشکی همدان',
  },
  {
    badge: 'مشارکت',
    title: 'جزوه‌ات رو با بقیه به اشتراک بذار',
    subtitle: 'آپلود کن، بعد از تایید ادمین منتشر می‌شه',
    cta: 'آپلود جزوه',
    to: '/upload',
    image: slideUploadImg,
    alt: 'ساختمان آموزشی دانشگاه',
  },
];

export default function HeroSlider() {
  // احترام به reduced-motion: بدون انیمیشن خودکار برای کاربران حساس به حرکت
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  return (
    <section aria-label="معرفی مدینو" className="mx-auto max-w-6xl px-4 pt-6">
      <Swiper
        modules={[Autoplay, Pagination, Navigation]}
        slidesPerView={1}
        loop
        autoplay={reducedMotion ? false : { delay: 5000, disableOnInteraction: false }}
        pagination={{ clickable: true }}
        navigation
        className="hero-swiper overflow-hidden rounded-2xl"
      >
        {slides.map((s) => (
          <SwiperSlide key={s.title}>
            <div className="relative min-h-64 md:min-h-80">
              <img
                src={s.image}
                alt={s.alt}
                className="absolute inset-0 h-full w-full object-cover"
              />
              {/* اورلی سفید برای خوانایی متن فارسی روی عکس */}
              <div className="absolute inset-0 bg-linear-to-l from-white via-white/85 to-white/10" />
              <div className="relative flex min-h-64 flex-col items-start justify-center gap-3 px-6 py-10 sm:px-12 md:min-h-80">
                <span className="rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-brand-700 shadow-sm">
                  {s.badge}
                </span>
                <h1 className="max-w-xl text-2xl leading-snug md:text-4xl">
                  {s.title}
                </h1>
                <p className="max-w-lg text-sm text-slate-800 md:text-base">
                  {s.subtitle}
                </p>
                <Link
                  to={s.to}
                  className="mt-2 rounded-lg bg-brand-500 px-6 py-2.5 text-white transition-colors hover:bg-brand-600"
                >
                  {s.cta}
                </Link>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </section>
  );
}
