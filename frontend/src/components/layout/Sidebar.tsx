// components/layout/Sidebar.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Book, FileText, MessageSquare, LogOut, Bell, User, Settings, ChevronDown, ChevronLeft } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const {
    sidebarOpen,
    setSidebarOpen,
    toggleSidebar,
    selectedCategory,
    setSelectedCategory,
    categories,
    setCategories,
    categoriesOpen,
    setCategoriesOpen,
    showNotification
  } = useAppContext();
  
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);
  
  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const isActive = (path: string) => {
    return location.pathname.includes(path);
  };

  const handleAddCategory = () => {
    const newCategoryName = prompt("Enter new category name:");
    if (newCategoryName && newCategoryName.trim()) {
      const newId = newCategoryName.toLowerCase().replace(/\s+/g, '-');
      setCategories([...categories, { id: newId, name: newCategoryName.trim() }]);
      showNotification("Category added");
    }
  };

  return (
    <>
      {/* Mobile overlay - only closes when clicking outside the sidebar */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      <aside 
        className={`fixed lg:relative w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 h-full z-30 ${
          sidebarOpen ? 'left-0' : '-left-64 lg:left-0'
        }`}
      >
        <div className="flex-grow overflow-y-auto flex flex-col h-full">
        {/* User Profile */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700" ref={profileRef}>
          <div 
            className="flex items-center space-x-3 cursor-pointer"
            onClick={() => setProfileOpen(!profileOpen)}
          >
            <div className="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center overflow-hidden">
              {user?.photoUrl ? (
                <img src={user.photoUrl} alt={user.fullName} className="w-full h-full object-cover" />
              ) : (
                <User size={24} className="text-emerald-400" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user?.fullName || 'User'}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user?.email || 'user@example.com'}
              </p>
            </div>
            <ChevronDown 
              size={16} 
              className={`text-gray-500 transition-transform ${profileOpen ? 'transform rotate-180' : ''}`} 
            />
          </div>
          
          {profileOpen && (
            <div className="mt-3 bg-gray-50 dark:bg-gray-800 rounded-md p-2">
              <Link
                to="/dashboard/profile"
                className="flex items-center px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md w-full text-left"
                onClick={() => setProfileOpen(false)}
              >
                <User size={16} className="mr-2" />
                Profile
              </Link>
              <Link
                to="/dashboard/settings"
                className="flex items-center px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md w-full text-left"
                onClick={() => setProfileOpen(false)}
              >
                <Settings size={16} className="mr-2" />
                Settings
              </Link>
            </div>
          )}
        </div>
        <nav className="px-4 space-y-1 flex-grow py-4">
          {/* Main Navigation */}
          <div className="mb-4">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Main Navigation
            </div>
            <Link
              to="/dashboard"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/dashboard') 
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-400 dark:text-emerald-400' 
                  : 'text-gray-900 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <Book size={20} className="mr-3" />
              <span>Dashboard</span>
            </Link>
            
            <Link
              to="/hub"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/hub') 
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-400 dark:text-emerald-400' 
                  : 'text-gray-900 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <FileText size={20} className="mr-3" />
              <span>Hub</span>
            </Link>
            
            <Link
              to="/library"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/library') 
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-400 dark:text-emerald-400' 
                  : 'text-gray-900 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <Book size={20} className="mr-3" />
              <span>Library</span>
            </Link>
            
            <Link
              to="/notify"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/notify') 
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-400 dark:text-emerald-400' 
                  : 'text-gray-900 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <Bell size={20} className="mr-3" />
              <span>Notify</span>
            </Link>
          </div>
          
        </nav>
        
        {/* Bottom buttons */}
        <div className="px-4 mt-auto pb-4 space-y-2">
          <Link
            to="/chat"
            className="w-full flex items-center justify-center px-3 py-2 rounded-md bg-emerald-400 hover:bg-emerald-500 text-white transition-colors"
          >
            <MessageSquare size={20} className="mr-2" />
            <span>Chat</span>
          </Link>
          
          <button
            onClick={logout}
            className="w-full flex items-center px-3 py-2 rounded-md text-gray-900 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <LogOut size={20} className="mr-3" />
            <span>Logout</span>
          </button>
        </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
