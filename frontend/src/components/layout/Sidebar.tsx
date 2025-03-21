// components/layout/Sidebar.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Book, FileText, Plug, ChevronDown, ChevronRight, Plus, MessageSquare, LogOut } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const {
    sidebarOpen,
    selectedCategory,
    setSelectedCategory,
    categories,
    setCategories,
    categoriesOpen,
    setCategoriesOpen,
    showNotification
  } = useAppContext();
  
  const { logout } = useAuth();

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
    <aside 
      className={`w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 fixed lg:relative z-40 h-[calc(100vh-4rem)]`}
    >
      <div className="flex-grow overflow-y-auto py-4 flex flex-col h-full">
        <nav className="px-4 space-y-1 flex-grow">
          {/* Main Navigation */}
          <div className="mb-4">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Main Navigation
            </div>
            <Link
              to="/dashboard"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/dashboard') 
                  ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' 
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <Book size={20} className="mr-3" />
              <span>Dashboard</span>
            </Link>
            
            <Link
              to="/hub"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/hub') 
                  ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' 
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <FileText size={20} className="mr-3" />
              <span>Hub</span>
            </Link>
            
            <Link
              to="/library"
              className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                isActive('/library') 
                  ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' 
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <Book size={20} className="mr-3" />
              <span>Library</span>
            </Link>
          </div>
          
        </nav>
        
        {/* Bottom buttons */}
        <div className="px-4 mt-auto pb-4 space-y-2">
          <Link
            to="/chat"
            className="w-full flex items-center justify-center px-3 py-2 rounded-md bg-emerald-500 hover:bg-emerald-600 text-white transition-colors"
          >
            <MessageSquare size={20} className="mr-2" />
            <span>Knowledge Chat</span>
          </Link>
          
          <button
            onClick={logout}
            className="w-full flex items-center px-3 py-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <LogOut size={20} className="mr-3" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
