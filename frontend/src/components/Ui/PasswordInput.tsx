import { useState } from 'react';
import type { InputHTMLAttributes } from 'react';
import { Eye, EyeOff } from 'lucide-react';

type Props = InputHTMLAttributes<HTMLInputElement>;

/** اینپوت رمز با دکمه چشم (سمت راست فیلد) */
export default function PasswordInput(props: Props) {
  const [show, setShow] = useState(false);
  const { className = '', ...rest } = props;

  return (
    <span className="relative block">
      <input {...rest} type={show ? 'text' : 'password'} className={`${className} pr-10`} />
      <button
        type="button"
        onClick={() => setShow((s) => !s)}
        aria-label={show ? 'پنهان کردن رمز عبور' : 'نمایش رمز عبور'}
        aria-pressed={show}
        title={show ? 'پنهان کردن رمز عبور' : 'نمایش رمز عبور'}
        className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-slate-400 transition-colors hover:text-slate-600"
      >
        {show ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />}
      </button>
    </span>
  );
}
