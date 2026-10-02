import { Route, Routes } from 'react-router-dom';
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
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="sections" element={<SectionsPage />} />
        <Route path="lessons" element={<LessonsListPage />} />
        <Route path="lessons/:id" element={<LessonDetailPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="admin" element={<AdminDashboardPage />} />
        <Route path="admin/pending" element={<AdminPendingPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
