// components/integration/ApiAccess.tsx
import React from 'react';
import { FileText } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import { API_URL } from '../../types';

const ApiAccess: React.FC = () => {
  const { showNotification } = useAppContext();

  const handleViewDocumentation = () => {
    showNotification("API documentation not available yet");
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-medium text-gray-900 dark:text-white text-lg flex items-center">
          <FileText className="text-gray-500 mr-2" size={20} />
          API Access
        </h3>
      </div>
      
      <div className="p-6">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Access your knowledge base programmatically using our REST API.
        </p>
        
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg mb-4 font-mono text-sm overflow-x-auto">
          <code className="text-gray-700 dark:text-gray-300">
            curl -X GET {API_URL}/documents \<br />
            &nbsp;&nbsp;-H "Content-Type: application/json"
          </code>
        </div>
        
        <div className="flex justify-end">
          <button 
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            onClick={handleViewDocumentation}
          >
            View API Documentation
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApiAccess;