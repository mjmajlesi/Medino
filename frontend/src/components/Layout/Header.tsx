import { Link, NavLink } from 'react-router-dom';
import { useAuthStore } from '../../store/auth.store';
import ThemeToggle from './ThemeToggle';

const links = [
  { to: '/', label: 'خانه' },
  { to: '/sections', label: 'بخش‌ها' },
  { to: '/lessons', label: 'دروس' },
  { to: '/upload', label: 'آپلود' },
];

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
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
          <ThemeToggle />
          {user ? (
            <>
              <Link
                to="/profile"
                className="ms-2 rounded-md bg-brand-50 px-4 py-2 text-brand-700 transition-colors hover:bg-brand-100"
              >
                {user.first_name} {user.last_name}
              </Link>
              <button
                type="button"
                onClick={logout}
                className="rounded-md px-3 py-2 text-slate-500 transition-colors hover:text-red-600"
              >
                خروج
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="ms-2 rounded-md bg-brand-500 px-4 py-2 text-white transition-colors hover:bg-brand-600"
            >
              ورود
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
