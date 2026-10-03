import { FileText, ListChecks, NotebookPen, Video } from 'lucide-react';
import type { ResourceType } from '../../types/models';
import { RESOURCE_TYPE_LABELS } from '../../types/models';

const ORDER: ResourceType[] = ['note', 'video', 'sample', 'summary'];
const ICONS = { note: FileText, video: Video, sample: ListChecks, summary: NotebookPen } as const;

interface ResourceTabsProps {
  counts: Record<ResourceType, number>;
  active: ResourceType;
  onChange: (t: ResourceType) => void;
}

export default function ResourceTabs({ counts, active, onChange }: ResourceTabsProps) {
  return (
    <div role="tablist" aria-label="انواع منابع درس" className="flex gap-2 overflow-x-auto pb-1">
      {ORDER.map((t) => {
        const Icon = ICONS[t];
        const isActive = t === active;
        return (
          <button
            key={t}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(t)}
            className={`flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${
              isActive
                ? 'bg-brand-500 text-white shadow-md shadow-brand-200'
                : 'border border-brand-100 bg-white text-slate-600 hover:border-brand-300 hover:text-brand-700'
            }`}
          >
            <Icon size={17} aria-hidden="true" />
            {RESOURCE_TYPE_LABELS[t]}
            <span
              className={`rounded-full px-2 py-0.5 text-xs ${
                isActive ? 'bg-white/25 text-white' : 'bg-brand-50 text-brand-700'
              }`}
            >
              {counts[t].toLocaleString('fa-IR')}
            </span>
          </button>
        );
      })}
    </div>
  );
}
