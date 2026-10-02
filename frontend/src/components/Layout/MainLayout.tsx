import { Outlet } from 'react-router-dom';
import Footer from './Footer';
import Header from './Header';

export default function MainLayout() {
  return (
    <div className="flex min-h-svh flex-col bg-white">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
