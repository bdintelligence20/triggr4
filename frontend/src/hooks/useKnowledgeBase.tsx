// hooks/useKnowledgeBase.tsx
import { useEffect, useCallback, useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
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
      
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_URL}/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
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
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_URL}/delete/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
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

  return {
    loadDocuments,
    deleteKnowledgeItem,
    searchKnowledgeItems,
    filterByCategory,
    sortKnowledgeItems
  };
};
