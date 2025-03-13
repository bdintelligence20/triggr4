// components/chat/ChatCategories.tsx
import React from 'react';
import { FileText, File } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';

const ChatCategories: React.FC = () => {
  const { 
    categories, 
    chatCategory, 
    setChatCategory,
    getCategoryKnowledgeCount
  } = useAppContext();

  return (
    <div className="md:col-span-1">
      <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Knowledge Sources</h3>
      
      <div className="space-y-4">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setChatCategory(category.id)}
            className={`w-full text-left p-3 rounded-lg border transition-colors ${
              chatCategory === category.id 
                ? 'border-emerald-400 dark:border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20' 
                : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {category.name === 'Documents' ? (
                  <File size={18} className="text-red-600 dark:text-red-500 mr-2" />
                ) : (
                  <FileText size={18} className="text-blue-500 dark:text-blue-400 mr-2" />
                )}
                <span className="font-medium text-gray-900 dark:text-white">{category.name}</span>
              </div>
              {chatCategory === category.id && (
                <div className="h-2 w-2 rounded-full bg-emerald-400 dark:bg-emerald-500"></div>
              )}
            </div>
            
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-2">
              <span>{getCategoryKnowledgeCount(category.id, 'text')} text items</span>
              <span>•</span>
              <span>{getCategoryKnowledgeCount(category.id, 'pdf') + getCategoryKnowledgeCount(category.id, 'doc')} documents</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChatCategories;