// components/library/KnowledgeGrid.tsx
import React, { useState } from 'react';
import { Search, Upload } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import KnowledgeItem from './KnowledgeItem';
import { useFileUpload } from '../../hooks/useFileUpload';
import { useKnowledgeBase } from '../../hooks/useKnowledgeBase';
import { API_URL, KnowledgeItem as KnowledgeItemType } from '../../types';

const KnowledgeGrid: React.FC = () => {
  const {
    filteredKnowledgeItems,
    selectedCategory,
    setSelectedCategory,
    categories,
    isLoading,
    setIsLoading,
    setError,
    showNotification,
    setKnowledgeItems
  } = useAppContext();

  const { fileInputRef, handleFileUpload } = useFileUpload();

  const handleDeleteKnowledgeItem = async (id: string) => {
    try {
      setIsLoading(true);
      
      // Call API to delete
      const response = await fetch(`${API_URL}/delete/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete item');
      }
      
      // Remove from local state
      const updatedItems = filteredKnowledgeItems.filter(item => item.id !== id);
      setKnowledgeItems(updatedItems);
      
      // Show notification
      showNotification("Item deleted successfully");
    } catch (err) {
      console.error('Error deleting knowledge item:', err);
      setError(`Failed to delete: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 transition-colors duration-300">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Knowledge Entries</h2>
          <div className="ml-4 px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-sm text-gray-700 dark:text-gray-300">
            {filteredKnowledgeItems.length} entries
          </div>
        </div>
        
        <div className="flex space-x-2">
          <select 
            className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 dark:focus:ring-emerald-500 transition-colors"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(category => (
              <option key={category.id} value={category.id}>{category.name}</option>
            ))}
          </select>
          
          <select className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 dark:focus:ring-emerald-500 transition-colors">
            <option>Sort by: Newest</option>
            <option>Sort by: Oldest</option>
            <option>Sort by: A-Z</option>
            <option>Sort by: Z-A</option>
          </select>
        </div>
      </div>
      
      {filteredKnowledgeItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKnowledgeItems.map(item => (
            <KnowledgeItem 
              key={item.id} 
              item={item} 
              onDelete={handleDeleteKnowledgeItem} 
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Search size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">No knowledge entries found</h3>
          <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            Try adjusting your search or category filters to find what you're looking for.
          </p>
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="mt-4 px-4 py-2 bg-emerald-400 hover:bg-emerald-300 text-white rounded-lg transition-colors inline-flex items-center"
          >
            <Upload size={18} className="mr-2" />
            Upload documents
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.doc,.docx,.txt"
            className="hidden"
          />
        </div>
      )}
    </div>
  );
};

export default KnowledgeGrid;
