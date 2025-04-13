// hooks/useKnowledgeBase.tsx
import { useEffect, useCallback, useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useAuth, APP_EVENTS } from '../contexts/AuthContext';
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
  
  // Get user and organization info from auth context
  const { user } = useAuth();
  const organizationId = user?.organizationId;
  
  // Use a ref to track if documents are currently being loaded
  const isLoadingRef = useRef(false);
  // Use a ref to track when documents were last loaded
  const lastLoadTimeRef = useRef(0);
  // Debounce time in milliseconds (5 seconds)
  const DEBOUNCE_TIME = 5000;

  // Load documents from backend - using useCallback to ensure stable function reference
  const loadDocuments = useCallback(async (force = false) => {
    // Skip if already loading or if last load was too recent (unless forced)
    const now = Date.now();
    if (
      isLoadingRef.current || 
      (!force && now - lastLoadTimeRef.current < DEBOUNCE_TIME)
    ) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      setIsLoading(true);
      
      const response = await import('../services/api').then(api => api.fetchDocuments());
      
      if (response.error) {
        console.error('Failed to load documents:', response.error);
        throw new Error(`Failed to load documents: ${response.error}`);
      }
      
      if (response.data && response.data.documents && Array.isArray(response.data.documents)) {
        const data = response.data;
        const loadedItems = data.documents.map((doc: any) => ({
          id: doc.id,
          title: doc.title,
          category: (doc.category === 'general' || doc.category === 'documents') ? 'hrhub' : doc.category,
          createdAt: new Date(doc.created_at || Date.now()),
          type: doc.file_type === 'pdf' ? 'pdf' as const : 
                doc.file_type === 'doc' ? 'doc' as const : 
                doc.file_type === 'csv' ? 'csv' as const : 'text' as const,
          fileSize: doc.word_count ? `${doc.word_count} words` : undefined,
          fileUrl: doc.file_url,
          processing_status: doc.processing_status,
          vectors_stored: doc.vectors_stored,
          word_count: doc.word_count
        }));
        
        setKnowledgeItems(loadedItems);
      }
      
      // Update last load time
      lastLoadTimeRef.current = Date.now();
    } catch (e) {
      console.error('Error loading documents:', e);
      setError('Failed to load documents from the server.');
    } finally {
      setIsLoading(false);
      isLoadingRef.current = false;
    }
  }, [setKnowledgeItems, setIsLoading, setError]);

  // Delete a knowledge item
  const deleteKnowledgeItem = async (id: string) => {
    try {
      setIsLoading(true);
      
      // Call API to delete
      const response = await import('../services/api').then(api => api.deleteDocument(id));
      
      if (response.error) {
        throw new Error(response.error || 'Failed to delete item');
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
        (item.type === 'pdf' || item.type === 'doc' || item.type === 'csv') : 
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

  // Load documents when component mounts or organization changes
  useEffect(() => {
    if (organizationId) {
      console.log(`Loading documents for organization: ${organizationId}`);
      loadDocuments(true); // Force load when organization changes
      
      // Set up a refresh interval (optional, every 30 seconds)
      const intervalId = setInterval(() => {
        loadDocuments();
      }, 30000);
      
      return () => clearInterval(intervalId);
    }
  }, [organizationId]); // Reload when organization changes
  
  // Listen for logout events to reset state
  useEffect(() => {
    const handleLogout = () => {
      // Reset loading state
      isLoadingRef.current = false;
      lastLoadTimeRef.current = 0;
      
      // Clear knowledge items
      setKnowledgeItems([]);
      console.log('Knowledge base state reset due to logout event');
    };
    
    // Add event listener
    window.addEventListener(APP_EVENTS.LOGOUT, handleLogout);
    
    // Clean up
    return () => {
      window.removeEventListener(APP_EVENTS.LOGOUT, handleLogout);
    };
  }, [setKnowledgeItems]);

  return {
    loadDocuments,
    deleteKnowledgeItem,
    searchKnowledgeItems,
    filterByCategory,
    sortKnowledgeItems
  };
};
