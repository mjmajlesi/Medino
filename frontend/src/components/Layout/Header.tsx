import { Link, NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'خانه' },
  { to: '/sections', label: 'بخش‌ها' },
  { to: '/lessons', label: 'دروس' },
  { to: '/upload', label: 'آپلود' },
];

export default function Header() {
  return (
    <header className="border-b border-brand-100 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="flex items-center gap-2">
          {/* لوگوی موقت تا رسیدن فایل اصلی کارفرما */}
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500 text-xl font-bold text-white">
            م
          </span>
          <span className="text-lg font-bold text-slate-900">مدینو</span>
        </Link>

        <nav className="flex items-center gap-1 text-sm">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `rounded-md px-3 py-2 transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-slate-600 hover:bg-slate-50'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
          <Link
            to="/login"
            className="ms-2 rounded-md bg-brand-500 px-4 py-2 text-white transition-colors hover:bg-brand-600"
          >
            ورود
          </Link>
        </nav>
      </div>
    </header>
  );
}
