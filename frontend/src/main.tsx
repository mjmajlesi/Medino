import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode, useEffect, useState } from 'react';
import type { ComponentType } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App.tsx';

const queryClient = new QueryClient();

/**
 * اورلی بازخورد بصری محیط توسعه (agentation) — فقط در dev لود می‌شود.
 * ایمپورت داینامیک + گارد DEV باعث می‌شود بیلد production بدون این پکیج
 * (که جزو وابستگی‌های پروژه نیست) سبز بماند. حذفش بی‌خطر است.
 */
function DevOverlay() {
  const [Comp, setComp] = useState<ComponentType<{ endpoint: string }> | null>(null);

  useEffect(() => {
    if (import.meta.env.DEV) {
      import('agentation')
        .then((m) => setComp(() => m.Agentation))
        .catch((err) => console.warn('[Medino] Agentation overlay failed to load:', err));
    }
  }, []);

  if (!Comp) return null;
  return <Comp endpoint="http://localhost:4747" />;
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <DevOverlay />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
