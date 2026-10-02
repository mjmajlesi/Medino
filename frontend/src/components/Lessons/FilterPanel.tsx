import { RotateCcw, SlidersHorizontal } from 'lucide-react';
import type { ResourceType, Section, SectionSlug } from '../../types/models';
import { RESOURCE_TYPE_LABELS } from '../../types/models';

export interface FilterState {
  section: SectionSlug | '';
  type: ResourceType | '';
  professor: string;
  term: number | '';
  sort: 'newest' | 'popular' | '';
}

interface FilterPanelProps {
  filters: FilterState;
  onChange: (patch: Partial<FilterState>) => void;
  onReset: () => void;
  sections: Section[];
  professors: string[];
  terms: number[];
  activeCount: number;
}

const selectCls =
  'w-full rounded-xl border border-brand-100 bg-white px-3 py-2.5 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-medium text-slate-500">{label}</span>
      {children}
    </label>
  );
}

export default function FilterPanel({
  filters,
  onChange,
  onReset,
  sections,
  professors,
  terms,
  activeCount,
}: FilterPanelProps) {
  return (
    <div className="rounded-2xl border border-brand-100 bg-brand-50/50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-sm font-medium">
          <SlidersHorizontal size={16} className="text-brand-500" aria-hidden="true" />
          فیلترها
          {activeCount > 0 && (
            <span className="rounded-full bg-brand-500 px-2 py-0.5 text-xs text-white">
              {activeCount.toLocaleString('fa-IR')}
            </span>
          )}
        </span>
        <button
          type="button"
          onClick={onReset}
          disabled={activeCount === 0}
          className="flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-slate-500 transition-colors hover:bg-white hover:text-brand-600 disabled:opacity-40"
        >
          <RotateCcw size={14} aria-hidden="true" />
          حذف فیلترها
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Field label="بخش">
          <select
            value={filters.section}
            onChange={(e) => onChange({ section: e.target.value as SectionSlug | '' })}
            className={selectCls}
          >
            <option value="">همه بخش‌ها</option>
            {sections.map((s) => (
              <option key={s.id} value={s.slug}>
                {s.title}
              </option>
            ))}
          </select>
        </Field>

        <Field label="نوع منبع">
          <select
            value={filters.type}
            onChange={(e) => onChange({ type: e.target.value as ResourceType | '' })}
            className={selectCls}
          >
            <option value="">همه منابع</option>
            {(Object.keys(RESOURCE_TYPE_LABELS) as ResourceType[]).map((t) => (
              <option key={t} value={t}>
                {RESOURCE_TYPE_LABELS[t]}
              </option>
            ))}
          </select>
        </Field>

        <Field label="استاد">
          <select
            value={filters.professor}
            onChange={(e) => onChange({ professor: e.target.value })}
            className={selectCls}
          >
            <option value="">همه استادها</option>
            {professors.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </Field>

        <Field label="ترم">
          <select
            value={filters.term}
            onChange={(e) =>
              onChange({ term: e.target.value === '' ? '' : Number(e.target.value) })
            }
            className={selectCls}
          >
            <option value="">همه ترم‌ها</option>
            {terms.map((t) => (
              <option key={t} value={t}>
                ترم {t.toLocaleString('fa-IR')}
              </option>
            ))}
          </select>
        </Field>

        <Field label="مرتب‌سازی">
          <select
            value={filters.sort}
            onChange={(e) => onChange({ sort: e.target.value as FilterState['sort'] })}
            className={selectCls}
          >
            <option value="">پیش‌فرض</option>
            <option value="newest">جدیدترین</option>
            <option value="popular">پربازدیدترین</option>
          </select>
        </Field>
      </div>
    </div>
  );
}
