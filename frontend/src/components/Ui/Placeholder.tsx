interface PlaceholderProps {
  title: string;
  note: string;
}

export default function Placeholder({ title, note }: PlaceholderProps) {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-2xl">{title}</h1>
      <p className="mt-2 rounded-lg border border-dashed border-brand-200 bg-brand-50 px-4 py-6 text-slate-500">
        {note}
      </p>
    </div>
  );
}
