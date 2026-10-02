import { Search, X } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (v: string) => void;
}

export default function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <div className="flex items-center gap-2 rounded-2xl border border-brand-100 bg-white p-2 shadow-lg shadow-brand-100/70">
      <Search size={20} className="ms-2 shrink-0 text-brand-400" aria-hidden="true" />
      <label htmlFor="lesson-search" className="sr-only">
        جستجوی درس یا استاد
      </label>
      <input
        id="lesson-search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="جستجو... نام درس یا استاد"
        autoComplete="off"
        className="w-full bg-transparent py-2.5 text-sm outline-none placeholder:text-slate-400"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange('')}
          aria-label="پاک کردن جستجو"
          className="shrink-0 rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}
