import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';
import { useAuthStore } from '../../store/auth.store';
import ThemeToggle from './ThemeToggle';

const links = [
  { to: '/', label: 'خانه' },
  { to: '/sections', label: 'بخش‌ها' },
  { to: '/lessons', label: 'دروس' },
  { to: '/upload', label: 'آپلود' },
];

function navCls({ isActive }: { isActive: boolean }) {
  return `rounded-md px-3 py-2 transition-colors ${
    isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-50'
  }`;
}

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [open, setOpen] = useState(false);

  return (
    <header className="border-b border-brand-100 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 py-3">
        <Link to="/" className="flex shrink-0 items-center gap-2" onClick={() => setOpen(false)}>
          <img src="/logo.jpg" alt="لوگوی مدینو" className="h-9 w-auto rounded-md" />
        </Link>

        {/* دسکتاپ */}
        <nav className="hidden items-center gap-1 text-sm md:flex" aria-label="ناوبری اصلی">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} className={navCls}>
              {l.label}
            </NavLink>
          ))}
          <ThemeToggle />
          {user ? (
            <>
              {user.is_staff && (
                <Link
                  to="/admin"
                  className="rounded-md bg-amber-100 px-4 py-2 text-amber-700 transition-colors hover:bg-amber-200"
                >
                  مدیریت
                </Link>
              )}
              <Link
                to="/profile"
                className="ms-2 max-w-32 truncate rounded-md bg-brand-50 px-4 py-2 text-brand-700 transition-colors hover:bg-brand-100"
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

        {/* موبایل: تاگل + همبرگر */}
        <div className="flex items-center gap-1 md:hidden">
          <ThemeToggle />
          {user ? (
            <Link
              to="/profile"
              className="max-w-24 truncate rounded-md bg-brand-50 px-3 py-2 text-sm text-brand-700"
            >
              {user.first_name}
            </Link>
          ) : (
            <Link to="/login" className="rounded-md bg-brand-500 px-4 py-2 text-sm text-white">
              ورود
            </Link>
          )}
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            aria-label={open ? 'بستن منو' : 'باز کردن منو'}
            className="rounded-md p-2 text-slate-600 transition-colors hover:bg-slate-100"
          >
            {open ? <X size={22} aria-hidden="true" /> : <Menu size={22} aria-hidden="true" />}
          </button>
        </div>
      </div>

      {/* پنل موبایل */}
      {open && (
        <nav className="border-t border-brand-100 bg-white px-4 py-2 md:hidden" aria-label="منوی موبایل">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  isActive ? 'bg-brand-50 font-medium text-brand-700' : 'text-slate-600'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
          {user && (
            <>
              {user.is_staff && (
                <Link
                  to="/admin"
                  onClick={() => setOpen(false)}
                  className="block rounded-lg bg-amber-100 px-3 py-2.5 text-sm text-amber-700"
                >
                  مدیریت
                </Link>
              )}
              <button
                type="button"
                onClick={() => {
                  logout();
                  setOpen(false);
                }}
                className="block w-full rounded-lg px-3 py-2.5 text-start text-sm text-red-600"
              >
                خروج از حساب
              </button>
            </>
          )}
        </nav>
      )}
    </header>
  );
}
