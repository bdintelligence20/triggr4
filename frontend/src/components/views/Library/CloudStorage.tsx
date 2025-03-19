import React from 'react';
import { Cloud, Database, HardDrive, Server } from 'lucide-react';

const CloudStorageIntegration: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-medium mb-4">Connect Cloud Storage</h2>
      <p className="text-gray-600 mb-6">
        Connect your cloud storage accounts to import documents directly.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="p-2 bg-blue-50 rounded-lg">
            <HardDrive className="text-blue-500" size={24} />
          </div>
          <div className="text-left">
            <p className="font-medium">Google Drive</p>
            <p className="text-sm text-gray-500">Connect your Google Drive account</p>
          </div>
        </button>
        
        <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Database className="text-blue-500" size={24} />
          </div>
          <div className="text-left">
            <p className="font-medium">Dropbox</p>
            <p className="text-sm text-gray-500">Connect your Dropbox account</p>
          </div>
        </button>
        
        <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Server className="text-blue-500" size={24} />
          </div>
          <div className="text-left">
            <p className="font-medium">OneDrive</p>
            <p className="text-sm text-gray-500">Connect your OneDrive account</p>
          </div>
        </button>
        
        <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Cloud className="text-blue-500" size={24} />
          </div>
          <div className="text-left">
            <p className="font-medium">Other Cloud</p>
            <p className="text-sm text-gray-500">Connect other cloud storage</p>
          </div>
        </button>
      </div>
      
      <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="font-medium mb-2">Why connect cloud storage?</h3>
        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
          <li>Import documents directly from your cloud storage</li>
          <li>Keep your knowledge base in sync with your cloud files</li>
          <li>Easily share documents with your team</li>
          <li>Access your documents from anywhere</li>
        </ul>
      </div>
    </div>
  );
};

export default CloudStorageIntegration;
