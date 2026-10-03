import { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';
import RequireAdmin from './components/Auth/RequireAdmin';
import RequireAuth from './components/Auth/RequireAuth';
import { useAuthStore } from './store/auth.store';
import MainLayout from './components/Layout/MainLayout';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminPendingPage from './pages/AdminPendingPage';
import HomePage from './pages/HomePage';
import LessonDetailPage from './pages/LessonDetailPage';
import LessonsListPage from './pages/LessonsListPage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';
import ProfilePage from './pages/ProfilePage';
import RegisterPage from './pages/RegisterPage';
import SectionsPage from './pages/SectionsPage';
import UploadPage from './pages/UploadPage';

export default function App() {
  const restore = useAuthStore((s) => s.restore);
  useEffect(() => {
    restore();
  }, [restore]);

  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="sections" element={<SectionsPage />} />
        <Route path="lessons" element={<LessonsListPage />} />
        <Route path="lessons/:id" element={<LessonDetailPage />} />
        <Route path="upload" element={<RequireAuth><UploadPage /></RequireAuth>} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        {/* گارد نقش ادمین فعال است — اتصال کامل به API در TASK-16 */}
        <Route path="admin" element={<RequireAuth><RequireAdmin><AdminDashboardPage /></RequireAdmin></RequireAuth>} />
        <Route path="admin/pending" element={<RequireAuth><RequireAdmin><AdminPendingPage /></RequireAdmin></RequireAuth>} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
