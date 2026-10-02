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
      <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-3 rounded-2xl border border-brand-100 bg-brand-50/60 px-6 py-4">
        {isPending
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-6 w-20 animate-pulse rounded bg-brand-100" />
            ))
          : items.map((it) => (
              <div key={it.label} className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-brand-700">{fa(it.value)}</span>
                <span className="text-md text-slate-500">{it.label}</span>
              </div>
            ))}
      </div>
    </section>
  );
}
