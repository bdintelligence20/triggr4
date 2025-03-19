import React, { useEffect } from 'react';
import { Folder, File, Search, Plus, Trash } from 'lucide-react';
import FileUploader from '../../../library/FileUploader';
import { useKnowledgeBase } from '../../../../hooks/useKnowledgeBase';
import { useAppContext } from '../../../../contexts/AppContext';

interface HubLibraryProps {
  hubId: number;
}

const HubLibrary: React.FC<HubLibraryProps> = ({ hubId }) => {
  const { loadDocuments, deleteKnowledgeItem } = useKnowledgeBase();
  const { 
    knowledgeItems, 
    isProcessingFile, 
    processingProgress,
    searchQuery,
    setSearchQuery,
    selectedCategory,
    setSelectedCategory,
    categories
  } = useAppContext();

  // Load documents on component mount
  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Hub Library</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300">
          <Plus size={20} />
          Add Content
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search and Filters */}
          <div className="flex gap-4">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            </div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            >
              <option value="all">All Categories</option>
              <option value="documents">Documents</option>
              <option value="images">Images</option>
              <option value="videos">Videos</option>
            </select>
          </div>

          {/* File Upload Area */}
          <div className="border-2 border-dashed rounded-lg p-8 text-center transition-colors border-gray-300">
            <FileUploader />
            <p className="mt-4 text-sm text-gray-600">
              Supported formats: PDF, DOC, DOCX, TXT
            </p>
          </div>

          {/* File List */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="p-4 border-b">
              <h3 className="font-medium">Knowledge Items</h3>
            </div>
            <div className="divide-y">
              {knowledgeItems.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-50 rounded-lg">
                      <File className="text-emerald-400" size={20} />
                    </div>
                    <div>
                      <p className="font-medium">{item.title}</p>
                      <p className="text-sm text-gray-500">
                        {item.fileSize || 'Unknown size'}
                      </p>
                    </div>
                  </div>
                  <button 
                    onClick={() => deleteKnowledgeItem(item.id)}
                    className="p-2 text-gray-400 hover:text-red-400"
                  >
                    <Trash size={20} />
                  </button>
                </div>
              ))}
              
              {knowledgeItems.length === 0 && (
                <div className="p-4 text-center text-gray-500">
                  No knowledge items found. Upload some files to get started.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Categories */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="font-medium mb-4">Categories</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-50">
                <Folder className="text-emerald-400" size={20} />
                <span>Documents</span>
              </button>
              <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-50">
                <Folder className="text-emerald-400" size={20} />
                <span>Images</span>
              </button>
              <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-50">
                <Folder className="text-emerald-400" size={20} />
                <span>Videos</span>
              </button>
            </div>
          </div>

          {/* Storage Usage */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="font-medium mb-4">Storage Usage</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Documents</span>
                  <span className="text-emerald-400">45%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-400 rounded-full" style={{ width: '45%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Images</span>
                  <span className="text-emerald-400">30%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-400 rounded-full" style={{ width: '30%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Videos</span>
                  <span className="text-emerald-400">25%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-400 rounded-full" style={{ width: '25%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HubLibrary;
