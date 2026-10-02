import { useQuery } from '@tanstack/react-query';
import { getStats } from '../../services/lessons.service';

const fa = (n: number) => n.toLocaleString('fa-IR');

export default function StatsBar() {
  const { data, isPending } = useQuery({ queryKey: ['stats'], queryFn: getStats });

  const items = [
    { value: data?.lessons ?? 0, label: 'درس' },
    { value: data?.notes ?? 0, label: 'جزوه' },
    { value: data?.videos ?? 0, label: 'فیلم آموزشی' },
    { value: data?.samples ?? 0, label: 'نمونه سوال' },
    { value: data?.summaries ?? 0, label: 'خلاصه‌نویسی' },
  ];

  return (
    <section aria-label="آمار مدینو" className="mx-auto max-w-6xl px-4 pt-8">
      <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-4 rounded-3xl bg-gradient-to-l from-brand-800 via-brand-700 to-brand-600 px-6 py-6 shadow-lg shadow-brand-200">
        {isPending
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-7 w-24 animate-pulse rounded-lg bg-white/20" />
            ))
          : items.map((it) => (
              <div key={it.label} className="flex min-w-20 flex-col items-center">
                <span className="text-3xl font-extrabold leading-none text-white tabular-nums md:text-4xl">
                  {fa(it.value)}
                </span>
                <span className="mt-1 text-xs text-brand-100">{it.label}</span>
              </div>
            ))}
      </div>
    </section>
  );
}
