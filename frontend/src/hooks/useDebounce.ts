import { useEffect, useState } from 'react';

/** مقدار را با تاخیر برمی‌گرداند — برای سرچ تا با هر کاراکتر ریکوئست نزنیم */
export function useDebounce<T>(value: T, delayMs = 400): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(t);
  }, [value, delayMs]);

  return debounced;
}
