// components/library/KnowledgeItem.tsx
import React from 'react';
import { FileText, FilePdf } from 'lucide-react';
import { KnowledgeItem as KnowledgeItemType } from '../../types';
import { useAppContext } from '../../contexts/AppContext';

interface KnowledgeItemProps {
  item: KnowledgeItemType;
  onDelete: (id: string) => void;
}

const KnowledgeItem: React.FC<KnowledgeItemProps> = ({ item, onDelete }) => {
  const { showNotification } = useAppContext();

  // Function to get file icon based on type
  const getFileIcon = (type?: string) => {
    switch (type) {
      case 'pdf':
        return <FilePdf size={20} className="text-red-500 dark:text-red-400 ml-2 flex-shrink-0" />;
      case 'doc':
        return <FileText size={20} className="text-blue-500 dark:text-blue-400 ml-2 flex-shrink-0" />;
      default:
        return <FileText size={20} className="text-gray-500 dark:text-gray-400 ml-2 flex-shrink-0" />;
    }
  };

  const handleView = () => {
    showNotification(`Viewing "${item.title}"`);
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-medium text-gray-900 dark:text-white">{item.title}</h3>
          {getFileIcon(item.type)}
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
          {item.content ? 
            `${item.content.substring(0, 150)}${item.content.length > 150 ? '...' : ''}` 
            : `File: ${item.fileUrl || item.title}`}
        </p>
        
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>
            {item.createdAt.toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'short', 
              day: 'numeric' 
            })}
          </span>
          <span className="capitalize px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full">
            {item.category}
          </span>
        </div>
      </div>
      
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 flex justify-between">
        <button 
          className="text-sm text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors"
          onClick={handleView}
        >
          View
        </button>
        <button 
          className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
          onClick={() => onDelete(item.id)}
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default KnowledgeItem;