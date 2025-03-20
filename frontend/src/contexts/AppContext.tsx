// contexts/AppContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { KnowledgeItem, Category, ChatMessage, API_URL } from '../types';

interface AppContextType {
  // UI States
  darkMode: boolean;
  setDarkMode: (value: boolean) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (value: boolean) => void;
  activeTab: string;
  setActiveTab: (value: string) => void;
  notification: string | null;
  setNotification: (value: string | null) => void;
  isLoading: boolean;
  setIsLoading: (value: boolean) => void;
  error: string | null;
  setError: (value: string | null) => void;
  
  // Knowledge States
  searchQuery: string;
  setSearchQuery: (value: string) => void;
  selectedCategory: string;
  setSelectedCategory: (value: string) => void;
  categoriesOpen: boolean;
  setCategoriesOpen: (value: boolean) => void;
  knowledgeItems: KnowledgeItem[];
  setKnowledgeItems: (value: KnowledgeItem[]) => void;
  categories: Category[];
  setCategories: (value: Category[]) => void;
  
  // File Upload States
  isProcessingFile: boolean;
  setIsProcessingFile: (value: boolean) => void;
  processingProgress: number;
  setProcessingProgress: (value: number) => void;
  
  // Chat States
  chatCategory: string;
  setChatCategory: (value: string) => void;
  newMessage: string;
  setNewMessage: (value: string) => void;
  chatMessages: ChatMessage[];
  setChatMessages: (value: ChatMessage[] | ((prev: ChatMessage[]) => ChatMessage[])) => void;
  activeEventSource: EventSource | null;
  setActiveEventSource: (value: EventSource | null) => void;
  
  // WhatsApp States
  whatsappNumber: string | null;
  setWhatsappNumber: (value: string | null) => void;
  showShareOptions: boolean;
  setShowShareOptions: (value: boolean) => void;
  
  // Computed Properties
  filteredKnowledgeItems: KnowledgeItem[];
  filteredChatMessages: ChatMessage[];
  
  // Helper Functions
  showNotification: (message: string, duration?: number) => void;
  getCategoryKnowledgeCount: (categoryId: string, type: string) => number;
  formatFileSize: (bytes: number) => string;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // UI States
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('library');
  const [notification, setNotification] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Knowledge States
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categoriesOpen, setCategoriesOpen] = useState(true);
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([
    { id: 'all', name: 'All Items' },
    { id: 'hrhub', name: 'HR Hub' }
  ]);
  
  // File Upload States
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  
  // Chat States
  const [chatCategory, setChatCategory] = useState('default');
  const [newMessage, setNewMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [activeEventSource, setActiveEventSource] = useState<EventSource | null>(null);
  
  // WhatsApp States
  const [whatsappNumber, setWhatsappNumber] = useState<string | null>(null);
  const [showShareOptions, setShowShareOptions] = useState(false);
  
  // Check backend connection on load
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        console.log('Backend connection:', response.ok ? 'successful' : 'failed');
        if (!response.ok) {
          setError('Cannot connect to the knowledge base. Please check your connection.');
        }
      } catch (error) {
        console.error('Backend connection error:', error);
        setError('Cannot connect to the knowledge base server.');
      }
    };
    
    checkBackendConnection();
  }, []);
  
  // Clean up EventSource on unmount
  useEffect(() => {
    return () => {
      if (activeEventSource) {
        activeEventSource.close();
      }
    };
  }, [activeEventSource]);
  
  // The loadDocuments function has been moved to the useKnowledgeBase hook
  // Initial data loading will be handled by the hook
  
  // Toggle dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);
  
  // Filter knowledge items based on search query and selected category
  const filteredKnowledgeItems = knowledgeItems.filter(item => {
    const matchesSearch = !searchQuery || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.content && item.content.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || 
      (selectedCategory === 'hrhub' ? (item.type === 'pdf' || item.type === 'doc') 
        : item.category === selectedCategory);
    
    return matchesSearch && matchesCategory;
  });
  
  // Filter chat messages based on selected chat category
  const filteredChatMessages = chatCategory 
    ? chatMessages.filter(msg => !msg.category || msg.category === chatCategory) 
    : [];
  
  // Helper function to display notifications
  const showNotification = (message: string, duration = 3000) => {
    setNotification(message);
    setTimeout(() => setNotification(null), duration);
  };
  
  // Helper function to get count of knowledge entries by category and type
  const getCategoryKnowledgeCount = (categoryId: string, type: string) => {
    if (categoryId === 'all') {
      return knowledgeItems.filter(item => item.type === type).length;
    } else if (categoryId === 'documents') {
      return knowledgeItems.filter(item => (item.type === 'pdf' || item.type === 'doc') && item.type === type).length;
    } else {
      return knowledgeItems.filter(item => item.category === categoryId && item.type === type).length;
    }
  };
  
  // Helper function to format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };
  
  const value = {
    // UI States
    darkMode,
    setDarkMode,
    sidebarOpen,
    setSidebarOpen,
    activeTab,
    setActiveTab,
    notification,
    setNotification,
    isLoading,
    setIsLoading,
    error,
    setError,
    
    // Knowledge States
    searchQuery,
    setSearchQuery,
    selectedCategory,
    setSelectedCategory,
    categoriesOpen,
    setCategoriesOpen,
    knowledgeItems,
    setKnowledgeItems,
    categories,
    setCategories,
    
    // File Upload States
    isProcessingFile,
    setIsProcessingFile,
    processingProgress,
    setProcessingProgress,
    
    // Chat States
    chatCategory,
    setChatCategory,
    newMessage,
    setNewMessage,
    chatMessages,
    setChatMessages,
    activeEventSource,
    setActiveEventSource,
    
    // WhatsApp States
    whatsappNumber,
    setWhatsappNumber,
    showShareOptions,
    setShowShareOptions,
    
    // Computed Properties
    filteredKnowledgeItems,
    filteredChatMessages,
    
    // Helper Functions
    showNotification,
    getCategoryKnowledgeCount,
    formatFileSize,
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
