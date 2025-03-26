// components/library/FileUploader.tsx
import React from 'react';
import { Upload } from 'lucide-react';
import { useFileUpload } from '../../hooks/useFileUpload';
import { useAppContext } from '../../contexts/AppContext';

const FileUploader: React.FC = () => {
  const { fileInputRef, handleFileUpload, openFileSelector } = useFileUpload();
  const { isProcessingFile, processingProgress } = useAppContext();

  return (
    <>
      <button 
        onClick={openFileSelector}
        className="btn-primary flex items-center justify-center bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg transition-colors"
        disabled={isProcessingFile}
      >
        <Upload size={18} className="mr-2" />
        <span>{isProcessingFile ? 'Uploading...' : 'Add Knowledge'}</span>
      </button>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.doc,.docx,.txt,.csv"
        className="hidden"
      />
      
      {isProcessingFile && (
        <div className="mt-4">
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
    </>
  );
};

export default FileUploader;
