// App.tsx
import React, { useRef } from 'react';
import { AppProvider } from './contexts/AppContext';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';
import LibraryPanel from './components/library/LibraryPanel';
import ChatPanel from './components/chat/ChatPanel';
import IntegrationPanel from './components/integration/IntegrationPanel';
import Notification from './components/ui/Notification';
import Error from './components/ui/Error';
import Loading from './components/ui/Loading';
import './index.css'; // Assuming you have a CSS file
import { useAppContext } from './contexts/AppContext';

// Import needed libraries if your app uses them
// Don't worry about importing pdfjs and mammoth, they will be imported in the specific components that need them

// Main app wrapper that provides context
const App: React.FC = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

// Actual app content that uses the context
const AppContent: React.FC = () => {
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
              {activeTab === 'library' && <LibraryPanel />}
              {activeTab === 'chat' && <ChatPanel />}
              {activeTab === 'integration' && <IntegrationPanel />}
            </div>
            
            <Footer />
          </main>
        </div>
      </div>
    </div>
  );
};

export default App;