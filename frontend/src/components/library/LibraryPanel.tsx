// components/library/LibraryPanel.tsx
import React from 'react';
import { Upload } from 'lucide-react';
import KnowledgeGrid from './KnowledgeGrid';
import FileUploader from './FileUploader';
import { useAppContext } from '../../contexts/AppContext';

const LibraryPanel: React.FC = () => {
  const { 
    isProcessingFile,
    processingProgress 
  } = useAppContext();

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 md:mb-0">
          Knowledge Library
        </h1>
        
        <FileUploader />
      </div>
      
      {isProcessingFile && (
        <div className="mb-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Processing documents... {Math.round(processingProgress)}%
          </p>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
            <div 
              className="bg-emerald-500 h-2.5 rounded-full" 
              style={{ width: `${processingProgress}%` }}
            ></div>
          </div>
        </div>
      )}
      
      <KnowledgeGrid />
    </div>
  );
};

export default LibraryPanel;