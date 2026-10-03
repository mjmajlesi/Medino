import { useState } from 'react';
import { Moon, Sun } from 'lucide-react';

const KEY = 'medino-theme';

export function isDark() {
  return document.documentElement.classList.contains('dark');
}

export default function ThemeToggle() {
  const [dark, setDark] = useState(isDark);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle('dark', next);
    try {
      localStorage.setItem(KEY, next ? 'dark' : 'light');
    } catch {
      /* حافظه در دسترس نیست — تم فقط همین نشست */
    }
  };

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={dark ? 'حالت روشن' : 'حالت تیره'}
      title={dark ? 'حالت روشن' : 'حالت تیره'}
      className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-brand-600"
    >
      {dark ? <Sun size={19} aria-hidden="true" /> : <Moon size={19} aria-hidden="true" />}
    </button>
  );
}
