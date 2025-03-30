import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../../layout/Sidebar';
import Header from '../../layout/Header';
import Footer from '../../layout/Footer';
import { useAppContext } from '../../../contexts/AppContext';

const MainLayout: React.FC = () => {
  const { sidebarOpen } = useAppContext();
  
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-800 relative">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => useAppContext().setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content - will automatically expand when sidebar collapses */}
      <div className="flex-1 flex flex-col overflow-hidden transition-all duration-300 w-full">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default MainLayout;
