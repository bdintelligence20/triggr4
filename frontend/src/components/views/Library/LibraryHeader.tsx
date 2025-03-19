import React from 'react';
import { Plus, Cloud, Users } from 'lucide-react';

interface LibraryHeaderProps {
  onAddContent: () => void;
  activeTab: 'files' | 'cloud' | 'teams';
  onTabChange: (tab: 'files' | 'cloud' | 'teams') => void;
}

const LibraryHeader: React.FC<LibraryHeaderProps> = ({ 
  onAddContent, 
  activeTab, 
  onTabChange 
}) => {
  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Knowledge Library</h1>
        <button
          onClick={onAddContent}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
        >
          <Plus size={20} />
          <span>Add Content</span>
        </button>
      </div>
      
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => onTabChange('files')}
          className={`px-4 py-2 font-medium text-sm ${
            activeTab === 'files'
              ? 'text-emerald-500 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Files
        </button>
        <button
          onClick={() => onTabChange('cloud')}
          className={`px-4 py-2 font-medium text-sm flex items-center gap-1 ${
            activeTab === 'cloud'
              ? 'text-emerald-500 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Cloud size={16} />
          <span>Cloud Storage</span>
        </button>
        <button
          onClick={() => onTabChange('teams')}
          className={`px-4 py-2 font-medium text-sm flex items-center gap-1 ${
            activeTab === 'teams'
              ? 'text-emerald-500 border-b-2 border-emerald-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Users size={16} />
          <span>Teams</span>
        </button>
      </div>
    </div>
  );
};

export default LibraryHeader;
