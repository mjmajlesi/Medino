import { isAxiosError } from 'axios';
import type { FieldValues, Path, UseFormSetError } from 'react-hook-form';

/**
 * خطاهای DRF ({field: [msg]} یا {detail}) را روی فرم می‌نشاند؛
 * اگر چیزی قابل نگاشت نبود false برمی‌گرداند تا پیام عمومی نشان داده شود.
 */
export function applyServerErrors<T extends FieldValues>(
  setError: UseFormSetError<T>,
  mapKey: (serverKey: string) => string | null,
  error: unknown,
): boolean {
  if (!isAxiosError(error)) return false;
  const data = error.response?.data as Record<string, unknown> | undefined;
  if (!data || typeof data !== 'object') return false;
  let handled = false;
  for (const [key, value] of Object.entries(data)) {
    const msg = Array.isArray(value) ? String(value[0]) : typeof value === 'string' ? value : null;
    if (!msg) continue;
    const local = mapKey(key);
    if (local) {
      setError(local as Path<T>, { type: 'server', message: msg });
      handled = true;
    }
  }
  return handled;
}
