import { useState } from 'react';
import type { FormEvent } from 'react';
import { Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function QuickSearch() {
  const [q, setQ] = useState('');
  const navigate = useNavigate();

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const query = q.trim();
    navigate(query ? `/lessons?search=${encodeURIComponent(query)}` : '/lessons');
  };

  return (
    <section aria-label="جستجوی سریع" className="mx-auto max-w-6xl px-4 pt-6">
      <form
        onSubmit={submit}
        role="search"
        className="flex items-center gap-2 rounded-2xl border border-brand-100 bg-white p-2 shadow-lg shadow-brand-100/70"
      >
        <Search size={20} className="ms-2 shrink-0 text-brand-400" aria-hidden="true" />
        <label htmlFor="quick-search" className="sr-only">
          جستجوی درس یا استاد
        </label>
        <input
          id="quick-search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="نام درس یا استاد رو بنویس... مثلا آناتومی"
          autoComplete="off"
          className="w-full bg-transparent py-2.5 text-sm outline-none placeholder:text-slate-400"
        />
        <button
          type="submit"
          className="min-h-11 shrink-0 rounded-xl bg-brand-500 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-600"
        >
          جستجو
        </button>
      </form>
    </section>
  );
}
