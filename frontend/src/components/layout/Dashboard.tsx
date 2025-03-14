import React, { useRef } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import Notification from '../ui/Notification';
import Error from '../ui/Error';
import Loading from '../ui/Loading';
import { useAppContext } from '../../contexts/AppContext';

const Dashboard: React.FC = () => {
  const { activeTab } = useAppContext();
  const mainContentRef = useRef<HTMLDivElement>(null);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-800 transition-colors duration-300">
      <div className="flex flex-col h-screen overflow-hidden">
        <Header />
        
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          
          <main 
            ref={mainContentRef}
            className="flex-1 overflow-y-auto p-6 lg:p-8 bg-gray-50 dark:bg-gray-800 relative"
          >
            <Notification />
            <Error />
            <Loading />
            
            <div className="max-w-7xl mx-auto">
              <Outlet />
            </div>
            
            <Footer />
          </main>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
