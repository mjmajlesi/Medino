import { useState } from 'react';
import type { FormEvent } from 'react';
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
        className="flex gap-2 rounded-2xl border border-brand-100 bg-brand-50/60 p-2"
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="نام درس یا استاد رو بنویس... مثلا آناتومی"
          className="w-full rounded-xl bg-white px-4 py-2.5 text-sm outline-none placeholder:text-slate-400 focus:ring-2 focus:ring-brand-200"
        />
        <button
          type="submit"
          className="shrink-0 rounded-xl bg-brand-500 px-6 py-2.5 text-sm text-white transition-colors hover:bg-brand-600"
        >
          جستجو
        </button>
      </form>
    </section>
  );
}
