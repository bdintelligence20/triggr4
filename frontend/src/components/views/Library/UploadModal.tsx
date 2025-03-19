import React from 'react';
import { X } from 'lucide-react';
import FileUploader from '../../library/FileUploader';
import { useAppContext } from '../../../contexts/AppContext';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose }) => {
  const { isProcessingFile, processingProgress } = useAppContext();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Upload Knowledge</h3>
          <button 
            onClick={onClose}
            className="p-1 rounded-full hover:bg-gray-100"
            disabled={isProcessingFile}
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            Upload documents to add to your knowledge base. Supported formats: PDF, DOC, DOCX, TXT.
          </p>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <FileUploader />
          </div>
        </div>
        
        <div className="flex justify-end">
          <button 
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={isProcessingFile}
          >
            {isProcessingFile ? 'Processing...' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
