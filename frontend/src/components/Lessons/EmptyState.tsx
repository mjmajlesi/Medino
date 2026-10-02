import { SearchX } from 'lucide-react';

interface EmptyStateProps {
  onReset: () => void;
}

export default function EmptyState({ onReset }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-brand-200 bg-brand-50/50 px-6 py-14 text-center">
      <SearchX size={40} className="text-brand-300" aria-hidden="true" />
      <h3 className="text-lg">درسی پیدا نشد</h3>
      <p className="max-w-sm text-sm text-slate-500">
        با این مشخصات چیزی نداریم. عبارت دیگه‌ای رو امتحان کن یا فیلترها رو بردار.
      </p>
      <button
        type="button"
        onClick={onReset}
        className="mt-1 rounded-xl bg-brand-500 px-6 py-2 text-sm text-white transition-colors hover:bg-brand-600"
      >
        حذف جستجو
      </button>
    </div>
  );
}
