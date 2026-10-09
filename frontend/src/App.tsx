import { lazy, Suspense, useEffect } from 'react';
import type { ReactNode } from 'react';
import { Route, Routes } from 'react-router-dom';
import RequireAdmin from './components/Auth/RequireAdmin';
import RequireAuth from './components/Auth/RequireAuth';
import MainLayout from './components/Layout/MainLayout';
import HomePage from './pages/HomePage';
import NotFoundPage from './pages/NotFoundPage';
import { useAuthStore } from './store/auth.store';

// Code-splitting: صفحه اصلی و 404 در باندل اول، بقیه lazy
const SectionsPage = lazy(() => import('./pages/SectionsPage'));
const LessonsListPage = lazy(() => import('./pages/LessonsListPage'));
const LessonDetailPage = lazy(() => import('./pages/LessonDetailPage'));
const UploadPage = lazy(() => import('./pages/UploadPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'));
const AdminPendingPage = lazy(() => import('./pages/AdminPendingPage'));

function PageFallback() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16" aria-busy="true">
      <div className="mx-auto h-8 w-48 animate-pulse rounded-lg bg-brand-50" />
      <div className="mt-4 h-40 animate-pulse rounded-2xl bg-brand-50" />
    </div>
  );
}

function lazyPage(node: ReactNode) {
  return <Suspense fallback={<PageFallback />}>{node}</Suspense>;
}

export default function App() {
  const restore = useAuthStore((s) => s.restore);
  useEffect(() => {
    restore();
  }, [restore]);

  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="sections" element={lazyPage(<SectionsPage />)} />
        <Route path="lessons" element={lazyPage(<LessonsListPage />)} />
        <Route path="lessons/:id" element={lazyPage(<LessonDetailPage />)} />
        <Route path="upload" element={<RequireAuth>{lazyPage(<UploadPage />)}</RequireAuth>} />
        <Route path="login" element={lazyPage(<LoginPage />)} />
        <Route path="register" element={lazyPage(<RegisterPage />)} />
        <Route path="profile" element={<RequireAuth>{lazyPage(<ProfilePage />)}</RequireAuth>} />
        {/* گارد نقش ادمین فعال است — اتصال کامل به API در TASK-16 */}
        <Route path="admin" element={<RequireAuth><RequireAdmin>{lazyPage(<AdminDashboardPage />)}</RequireAdmin></RequireAuth>} />
        <Route path="admin/pending" element={<RequireAuth><RequireAdmin>{lazyPage(<AdminPendingPage />)}</RequireAdmin></RequireAuth>} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
