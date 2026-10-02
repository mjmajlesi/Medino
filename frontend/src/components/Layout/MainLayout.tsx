import { Outlet } from 'react-router-dom';
import Footer from './Footer';
import Header from './Header';

export default function MainLayout() {
  return (
    <div className="flex min-h-svh flex-col bg-white">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:start-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-brand-600 focus:px-4 focus:py-2 focus:text-white"
      >
        پرش به محتوای اصلی
      </a>
      <Header />
      <main id="main-content" className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
