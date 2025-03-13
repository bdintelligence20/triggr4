// hooks/useKnowledgeBase.tsx
import { useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { API_URL, KnowledgeItem } from '../types';

export const useKnowledgeBase = () => {
  const { 
    setKnowledgeItems, 
    setIsLoading, 
    setError,
    selectedCategory,
    searchQuery,
    knowledgeItems
  } = useAppContext();

  // Load documents from backend
  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_URL}/documents`);
      
      if (!response.ok) {
        console.error('Failed to load documents, status:', response.status);
        throw new Error(`Failed to load documents: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.documents && Array.isArray(data.documents)) {
        const loadedItems = data.documents.map((doc: any) => ({
          id: doc.id,
          title: doc.title,
          category: (doc.category === 'general' || doc.category === 'documents') ? 'hrhub' : doc.category,
          createdAt: new Date(doc.created_at || Date.now()),
          type: doc.file_type === 'pdf' ? 'pdf' : doc.file_type === 'doc' ? 'doc' : 'text',
          fileSize: doc.word_count ? `${doc.word_count} words` : undefined,
          fileUrl: doc.file_url,
          processing_status: doc.processing_status,
          vectors_stored: doc.vectors_stored,
          word_count: doc.word_count
        }));
        
        setKnowledgeItems(loadedItems);
      }
    } catch (e) {
      console.error('Error loading documents:', e);
      setError('Failed to load documents from the server.');
    } finally {
      setIsLoading(false);
    }
  };

  // Delete a knowledge item
  const deleteKnowledgeItem = async (id: string) => {
    try {
      setIsLoading(true);
      
      // Call API to delete
      const response = await fetch(`${API_URL}/delete/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete item');
      }
      
      // Remove from local state
      setKnowledgeItems(knowledgeItems.filter(item => item.id !== id));
      
      return true;
    } catch (err) {
      console.error('Error deleting knowledge item:', err);
      setError(`Failed to delete: ${err instanceof Error ? err.message : 'Unknown error'}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Search knowledge items
  const searchKnowledgeItems = (query: string): KnowledgeItem[] => {
    if (!query) return knowledgeItems;
    
    return knowledgeItems.filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      (item.content && item.content.toLowerCase().includes(query.toLowerCase()))
    );
  };

  // Filter knowledge items by category
  const filterByCategory = (category: string): KnowledgeItem[] => {
    if (category === 'all') return knowledgeItems;
    
    return knowledgeItems.filter(item => 
      category === 'hrhub' ? 
        (item.type === 'pdf' || item.type === 'doc') : 
        item.category === category
    );
  };

  // Sort knowledge items
  const sortKnowledgeItems = (
    items: KnowledgeItem[], 
    sortBy: 'newest' | 'oldest' | 'a-z' | 'z-a' = 'newest'
  ): KnowledgeItem[] => {
    const sorted = [...items];
    
    switch (sortBy) {
      case 'newest':
        return sorted.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
      case 'oldest':
        return sorted.sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime());
      case 'a-z':
        return sorted.sort((a, b) => a.title.localeCompare(b.title));
      case 'z-a':
        return sorted.sort((a, b) => b.title.localeCompare(a.title));
      default:
        return sorted;
    }
  };

  // Load documents on initial render
  useEffect(() => {
    loadDocuments();
  }, []);

  return {
    loadDocuments,
    deleteKnowledgeItem,
    searchKnowledgeItems,
    filterByCategory,
    sortKnowledgeItems
  };
};