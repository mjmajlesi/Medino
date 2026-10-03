import { Download, FileText, ListChecks, NotebookPen, Video } from 'lucide-react';
import type { Resource } from '../../types/models';

const ICONS = { note: FileText, video: Video, sample: ListChecks, summary: NotebookPen } as const;

/** در حالت Mock آدرس فایل '#' است — دکمه واقعی فقط با URL واقعی فعال می‌شود */
const isPlaceholder = (url: string) => url === '#' || url.trim() === '';

function faDate(iso: string) {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('fa-IR');
}

export default function FileRow({ resource }: { resource: Resource }) {
  const Icon = ICONS[resource.type];
  const placeholder = isPlaceholder(resource.file_url);

  return (
    <li className="px-2 py-4">
      <div className="flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
          <Icon size={19} aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <h4 className="text-sm font-medium leading-6">{resource.title}</h4>
          {resource.description && (
            <p className="mt-0.5 text-xs leading-5 text-slate-500">{resource.description}</p>
          )}
          <p className="mt-1 text-xs text-slate-400">
            {resource.uploader_name} · {faDate(resource.created_at)}
            {resource.duration && ` · ${resource.duration}`}
          </p>
        </div>
        {resource.type !== 'video' &&
          (placeholder ? (
            <span className="shrink-0 rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-400">
              فایل نمایشی
            </span>
          ) : (
            <a
              href={resource.file_url}
              download
              className="flex shrink-0 items-center gap-1.5 rounded-lg bg-brand-500 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-brand-600"
            >
              <Download size={15} aria-hidden="true" />
              دانلود
            </a>
          ))}
      </div>

      {resource.type === 'video' &&
        (placeholder ? (
          <p className="mt-3 rounded-xl bg-slate-50 px-4 py-6 text-center text-xs text-slate-400">
            پیش‌نمایش ویدیو بعد از اتصال به API فعال می‌شود (فایل نمایشی)
          </p>
        ) : (
          <video controls preload="metadata" src={resource.file_url} className="mt-3 w-full rounded-xl bg-black">
            مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
          </video>
        ))}
    </li>
  );
}
