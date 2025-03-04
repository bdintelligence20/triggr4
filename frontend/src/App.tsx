import { useState, useRef, useEffect } from 'react';
import { Book, MessageSquare, Send, Upload, Plus, Trash2, FileText, File as FilePdf, FileIcon, Smartphone, Navigation, Search, X, Menu, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';
import * as pdfjs from 'pdfjs-dist';
import * as mammoth from 'mammoth';

// Set worker path for PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

// Replace with your actual backend URL
const API_URL = 'https://triggr4bg.onrender.com';

interface KnowledgeItem {
  id: string;
  title: string;
  content?: string;
  category: string;
  createdAt: Date;
  type: 'text' | 'pdf' | 'doc';
  fileSize?: string;
  fileUrl?: string;
}

interface Category {
  id: string;
  name: string;
  whatsappNumber?: string;
}

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  category?: string;
}

function App() {
  const [activeTab, setActiveTab] = useState<'hub' | 'whatsapp' | 'chat'>('hub');
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([
    { id: '1', name: 'General' },
    { id: '2', name: 'Documents' }
  ]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>('1');
  const [newItemTitle, setNewItemTitle] = useState('');
  const [newItemContent, setNewItemContent] = useState('');
  const [newCategoryName, setNewCategoryName] = useState('');
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [chatCategory, setChatCategory] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

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

  // Attempt to load documents from backend
  useEffect(() => {
    const loadDocuments = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${API_URL}/documents`);
        
        if (!response.ok) {
          console.error('Failed to load documents, status:', response.status);
          return;
        }
        
        const data = await response.json();
        if (data.documents && Array.isArray(data.documents)) {
          const loadedItems = data.documents.map(doc => ({
            id: doc.id,
            title: doc.title,
            category: doc.category === 'general' ? '1' : '2', // Map category to ID
            createdAt: new Date(doc.created_at || Date.now()),
            type: doc.file_type === 'pdf' ? 'pdf' : doc.file_type === 'doc' ? 'doc' : 'text',
            fileSize: doc.word_count ? `${doc.word_count} words` : undefined,
            fileUrl: doc.file_url
          }));
          
          setKnowledgeItems(loadedItems);
        }
      } catch (e) {
        console.error('Error loading documents:', e);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadDocuments();
  }, []);

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleAddKnowledgeItem = async () => {
    if (!newItemTitle.trim() || !newItemContent.trim() || !selectedCategory) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Convert text to File object for consistent API handling
      const textBlob = new Blob([newItemContent], { type: 'text/plain' });
      const textFile = new File([textBlob], `${newItemTitle}.txt`, { type: 'text/plain' });
      
      // Build form data
      const formData = new FormData();
      formData.append('file', textFile);
      formData.append('category', selectedCategory);
      formData.append('title', newItemTitle);
      
      // Send to API
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add knowledge item');
      }
      
      const result = await response.json();
      
      // Add to local state
      const newItem: KnowledgeItem = {
        id: result.item_id || Date.now().toString(),
        title: newItemTitle,
        content: newItemContent,
        category: selectedCategory,
        createdAt: new Date(),
        type: 'text',
        fileUrl: result.file_url
      };
      
      setKnowledgeItems([...knowledgeItems, newItem]);
      setNewItemTitle('');
      setNewItemContent('');
    } catch (err) {
      console.error('Error adding knowledge item:', err);
      setError(`Failed to add knowledge item: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddCategory = () => {
    if (!newCategoryName.trim()) return;
    
    const newCategory: Category = {
      id: Date.now().toString(),
      name: newCategoryName
    };
    
    setCategories([...categories, newCategory]);
    setNewCategoryName('');
    setShowAddCategory(false);
    setSelectedCategory(newCategory.id);
  };

  const handleDeleteKnowledgeItem = async (id: string) => {
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
    } catch (err) {
      console.error('Error deleting knowledge item:', err);
      setError(`Failed to delete: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateWhatsappNumber = (categoryId: string) => {
    // In a real app, this would call an API to generate a WhatsApp number
    const randomNumber = '+1' + Math.floor(Math.random() * 9000000000 + 1000000000);
    
    setCategories(categories.map(category => 
      category.id === categoryId 
        ? { ...category, whatsappNumber: randomNumber } 
        : category
    ));
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !chatCategory) return;
    
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: newMessage,
      sender: 'user',
      timestamp: new Date(),
      category: chatCategory
    };
    
    setChatMessages([...chatMessages, userMessage]);
    
    try {
      const categoryName = categories.find(c => c.id === chatCategory)?.name || '';
      
      // Call API to get response
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: newMessage,
          category: categoryName
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to get response: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: result.response || "I couldn't find an answer to your question.",
        sender: 'ai',
        timestamp: new Date(),
        category: chatCategory
      };
      
      setChatMessages(prevMessages => [...prevMessages, aiMessage]);
    } catch (err) {
      console.error('Error getting AI response:', err);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error while processing your request. Please try again later.",
        sender: 'ai',
        timestamp: new Date(),
        category: chatCategory
      };
      
      setChatMessages(prevMessages => [...prevMessages, errorMessage]);
    }
    
    setNewMessage('');
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    setIsProcessingFile(true);
    setProcessingProgress(0);
    setError(null);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileName = file.name;
      
      try {
        // Update progress
        setProcessingProgress(((i + 0.5) / files.length) * 100);
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', selectedCategory || '2'); // Default to Documents category
        formData.append('title', fileName);
        
        // Send file to backend
        console.log(`Uploading file to ${API_URL}/upload`);
        const response = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Server returned ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Upload response:', result);
        
        // Create new knowledge item
        const newItem: KnowledgeItem = {
          id: result.item_id || Date.now().toString() + i,
          title: fileName,
          category: selectedCategory || '2',
          createdAt: new Date(),
          type: fileName.toLowerCase().endsWith('.pdf') ? 'pdf' : 'doc',
          fileSize: formatFileSize(file.size),
          fileUrl: result.file_url
        };
        
        setKnowledgeItems(prev => [...prev, newItem]);
        setProcessingProgress(((i + 1) / files.length) * 100);
      } catch (error) {
        console.error(`Error uploading file ${fileName}:`, error);
        setError(`Failed to upload ${fileName}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
    
    setIsProcessingFile(false);
    setProcessingProgress(0);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const extractTextFromPDF = async (file: File): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise;
        let fullText = '';
        
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const textContent = await page.getTextContent();
          const pageText = textContent.items.map((item: any) => item.str).join(' ');
          fullText += pageText + '\n';
        }
        
        resolve(fullText);
      } catch (error) {
        reject(error);
      }
    });
  };

  const extractTextFromDOCX = async (file: File): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      try {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        resolve(result.value);
      } catch (error) {
        reject(error);
      }
    });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  const filteredKnowledgeItems = knowledgeItems.filter(item => {
    const matchesCategory = !selectedCategory || item.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (item.content && item.content.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesCategory && matchesSearch;
  });

  const filteredChatMessages = chatMessages.filter(message => 
    !message.category || message.category === chatCategory
  );

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FilePdf className="text-red-500" />;
      case 'doc':
        return <FileText className="text-blue-500" />;
      default:
        return <FileIcon />;
    }
  };

  const getCategoryWhatsappNumber = (categoryId: string) => {
    const category = categories.find(c => c.id === categoryId);
    return category?.whatsappNumber;
  };

  const getCategoryKnowledgeCount = (categoryId: string, type: 'text' | 'pdf' | 'doc') => {
    return knowledgeItems.filter(item => item.category === categoryId && item.type === type).length;
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-indigo-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Book size={28} />
            <h1 className="text-xl md:text-2xl font-bold">Knowledge Hub</h1>
          </div>
          
          <div className="hidden md:flex space-x-4">
            <button 
              onClick={() => setActiveTab('hub')}
              className={`px-4 py-2 rounded-md transition-colors ${activeTab === 'hub' ? 'bg-indigo-800' : 'hover:bg-indigo-600'}`}
            >
              Knowledge Base
            </button>
            <button 
              onClick={() => setActiveTab('whatsapp')}
              className={`px-4 py-2 rounded-md transition-colors ${activeTab === 'whatsapp' ? 'bg-indigo-800' : 'hover:bg-indigo-600'}`}
            >
              WhatsApp Integration
            </button>
            <button 
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-md transition-colors ${activeTab === 'chat' ? 'bg-indigo-800' : 'hover:bg-indigo-600'}`}
            >
              Chat Simulation
            </button>
          </div>
          
          <button 
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        
        {isMobileMenuOpen && (
          <div className="container mx-auto px-4 pb-4 md:hidden">
            <div className="flex flex-col space-y-2">
              <button 
                onClick={() => {
                  setActiveTab('hub');
                  setIsMobileMenuOpen(false);
                }}
                className={`px-4 py-2 rounded-md transition-colors ${activeTab === 'hub' ? 'bg-indigo-800' : 'hover:bg-indigo-600'}`}
              >
                Knowledge Base
              </button>
              <button 
                onClick={() => {
                  setActiveTab('whatsapp');
                  setIsMobileMenuOpen(false);
                }}
                className={`px-4 py-2 rounded-md transition-colors ${activeTab === 'whatsapp' ? 'bg-indigo-800' : 'hover:bg-indigo-600'}`}
              >
                WhatsApp Integration
              </button>
              <button 
                onClick={() => {
                  setActiveTab('chat');
                  setIsMobileMenuOpen(false);
                }}
                className={`px-4 py-2 rounded-md transition-colors ${activeTab === 'chat' ? 'bg-indigo-800' : 'hover:bg-indigo-600'}`}
              >
                Chat Simulation
              </button>
            </div>
          </div>
        )}
      </header>
      
      <main className="flex-grow container mx-auto px-4 py-8">
        {/* Display error message if present */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start">
            <AlertCircle size={20} className="mr-2 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Error</p>
              <p>{error}</p>
            </div>
          </div>
        )}
        
        {isLoading && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">Loading...</p>
            <p>Please wait while we process your request.</p>
          </div>
        )}
        
        {activeTab === 'hub' && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-1 bg-white rounded-lg shadow-md p-4">
              <h2 className="text-lg font-semibold mb-4">Categories</h2>
              
              <div className="space-y-2 mb-4">
                <button 
                  onClick={() => setSelectedCategory(null)}
                  className={`w-full text-left px-3 py-2 rounded-md flex items-center ${!selectedCategory ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-gray-100'}`}
                >
                  <FileIcon size={18} className="mr-2" />
                  All Items
                </button>
                
                {categories.map(category => (
                  <button 
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full text-left px-3 py-2 rounded-md flex items-center ${selectedCategory === category.id ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-gray-100'}`}
                  >
                    {category.name === 'Documents' ? (
                      <FilePdf size={18} className="mr-2 text-red-500" />
                    ) : (
                      <FileText size={18} className="mr-2" />
                    )}
                    {category.name}
                  </button>
                ))}
              </div>
              
              {showAddCategory ? (
                <div className="mt-4">
                  <input
                    type="text"
                    value={newCategoryName}
                    onChange={(e) => setNewCategoryName(e.target.value)}
                    placeholder="Category name"
                    className="w-full px-3 py-2 border rounded-md mb-2"
                  />
                  <div className="flex space-x-2">
                    <button
                      onClick={handleAddCategory}
                      className="px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => {
                        setShowAddCategory(false);
                        setNewCategoryName('');
                      }}
                      className="px-3 py-1 bg-gray-300 rounded-md hover:bg-gray-400 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowAddCategory(true)}
                  className="flex items-center text-indigo-600 hover:text-indigo-800 transition-colors"
                >
                  <Plus size={18} className="mr-1" />
                  Add Category
                </button>
              )}
            </div>
            
            <div className="md:col-span-3">
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                  <h2 className="text-xl font-semibold mb-2 md:mb-0">Knowledge Base</h2>
                  
                  <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-2">
                    <div className="relative">
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search knowledge base..."
                        className="pl-9 pr-3 py-2 border rounded-md w-full"
                      />
                      <Search size={18} className="absolute left-3 top-2.5 text-gray-400" />
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center"
                        disabled={isProcessingFile}
                      >
                        <Upload size={18} className="mr-1" />
                        Upload Documents
                      </button>
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        accept=".pdf,.doc,.docx"
                        multiple
                        className="hidden"
                      />
                    </div>
                  </div>
                </div>
                
                {isProcessingFile && (
                  <div className="mb-6">
                    <p className="text-sm text-gray-600 mb-1">Processing documents...</p>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className="bg-indigo-600 h-2.5 rounded-full" 
                        style={{ width: `${processingProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                {filteredKnowledgeItems.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {filteredKnowledgeItems.map(item => (
                      <div key={item.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-start space-x-2">
                            {getFileIcon(item.type)}
                            <h3 className="font-medium">{item.title}</h3>
                          </div>
                          <button
                            onClick={() => handleDeleteKnowledgeItem(item.id)}
                            className="text-red-500 hover:text-red-700 transition-colors"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                        
                        {item.type !== 'text' && (
                          <div className="text-xs text-gray-500 mb-2 flex items-center">
                            <span className="uppercase bg-gray-200 rounded px-2 py-0.5 mr-2">
                              {item.type}
                            </span>
                            {item.fileSize}
                          </div>
                        )}
                        
                        <p className="text-gray-600 text-sm mb-2 line-clamp-3">
                          {item.content 
                            ? `${item.content.substring(0, 150)}${item.content.length > 150 ? '...' : ''}` 
                            : 'Content stored on server'}
                        </p>
                        
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <span>
                            {categories.find(c => c.id === item.category)?.name || 'Uncategorized'}
                          </span>
                          <span>
                            {item.createdAt.toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText size={48} className="mx-auto text-gray-300 mb-2" />
                    <h3 className="text-lg font-medium text-gray-700 mb-1">No knowledge items found</h3>
                    <p className="text-gray-500">
                      {searchQuery ? 'Try a different search term' : 'Add some knowledge items to get started'}
                    </p>
                  </div>
                )}
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Add New Knowledge</h2>
                
                <div className="space-y-4">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                      Title
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={newItemTitle}
                      onChange={(e) => setNewItemTitle(e.target.value)}
                      placeholder="Enter a title"
                      className="w-full px-3 py-2 border rounded-md"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                      Category
                    </label>
                    <select
                      id="category"
                      value={selectedCategory || ''}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="" disabled>Select a category</option>
                      {categories.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                      Content
                    </label>
                    <textarea
                      id="content"
                      value={newItemContent}
                      onChange={(e) => setNewItemContent(e.target.value)}
                      placeholder="Enter the knowledge content"
                      className="w-full px-3 py-2 border rounded-md h-32"
                    ></textarea>
                  </div>
                  
                  <button
                    onClick={handleAddKnowledgeItem}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                    disabled={!newItemTitle || !newItemContent || !selectedCategory || isLoading}
                  >
                    Add Knowledge Item
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'whatsapp' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-6">WhatsApp Integration</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium mb-4">WhatsApp Numbers by Category</h3>
                
                <div className="space-y-4">
                  {categories.map(category => (
                    <div key={category.id} className="border rounded-lg p-4">
                      <h4 className="font-medium mb-3">{category.name}</h4>
                      
                      {category.whatsappNumber ? (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <div className="flex items-center mb-2">
                          <Smartphone size={18} className="text-green-600 mr-2" />
                            <span className="font-medium text-green-800">WhatsApp Number</span>
                          </div>
                          <p className="text-lg font-semibold text-green-700">{category.whatsappNumber}</p>
                        </div>
                      ) : (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                          <p className="text-gray-600 mb-3">
                            Generate a WhatsApp number for the {category.name} category.
                          </p>
                          <button
                            onClick={() => handleGenerateWhatsappNumber(category.id)}
                            className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center text-sm"
                          >
                            <Smartphone size={14} className="mr-1" />
                            Generate WhatsApp Number
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-4">WhatsApp Integration Guide</h3>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h4 className="font-medium text-blue-800 mb-2">How It Works</h4>
                  <ol className="list-decimal list-inside text-blue-700 space-y-2 text-sm">
                    <li>Generate a dedicated WhatsApp number for each knowledge category</li>
                    <li>Users can chat with the AI assistant through WhatsApp</li>
                    <li>The AI will respond based on the specific category's knowledge base</li>
                    <li>All interactions are logged and can be reviewed</li>
                    <li>Knowledge base is continuously updated based on new information</li>
                  </ol>
                </div>
                
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <h4 className="font-medium text-indigo-800 mb-2">Best Practices</h4>
                  <ul className="list-disc list-inside text-indigo-700 space-y-2 text-sm">
                    <li>Organize your knowledge into meaningful categories</li>
                    <li>Add detailed and accurate information to your knowledge base</li>
                    <li>Regularly update your knowledge base to keep information current</li>
                    <li>Monitor chat interactions to identify knowledge gaps</li>
                    <li>Use clear and concise language in your knowledge entries</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'chat' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-6">Chat Simulation</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="md:col-span-1">
                <h3 className="text-lg font-medium mb-4">Knowledge Sources</h3>
                
                <div className="mb-4">
                  <label htmlFor="chatCategory" className="block text-sm font-medium text-gray-700 mb-2">
                    Select Category to Chat With
                  </label>
                  <select
                    id="chatCategory"
                    value={chatCategory || ''}
                    onChange={(e) => setChatCategory(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md mb-2"
                  >
                    <option value="" disabled>Select a category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  
                  {chatCategory && !getCategoryWhatsappNumber(chatCategory) && (
                    <div className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded mb-2">
                      This category doesn't have a WhatsApp number yet. 
                      <button 
                        onClick={() => setActiveTab('whatsapp')}
                        className="text-indigo-600 hover:underline ml-1"
                      >
                        Generate one
                      </button>
                    </div>
                  )}
                </div>
                
                {chatCategory && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">{categories.find(c => c.id === chatCategory)?.name}</span> has:
                    </p>
                    <ul className="space-y-2">
                      <li className="flex items-center text-sm">
                        <FileText size={16} className="text-indigo-600 mr-2" />
                        <span>{getCategoryKnowledgeCount(chatCategory, 'text')} Text Entries</span>
                      </li>
                      <li className="flex items-center text-sm">
                        <FilePdf size={16} className="text-red-500 mr-2" />
                        <span>{getCategoryKnowledgeCount(chatCategory, 'pdf')} PDF Documents</span>
                      </li>
                      <li className="flex items-center text-sm">
                        <FileText size={16} className="text-blue-500 mr-2" />
                        <span>{getCategoryKnowledgeCount(chatCategory, 'doc')} Word Documents</span>
                      </li>
                    </ul>
                  </div>
                )}
                
                <div className="bg-indigo-50 rounded-lg p-4">
                  <h4 className="font-medium text-indigo-800 mb-2">About This Simulation</h4>
                  <p className="text-sm text-indigo-700 mb-2">
                    This chat simulates how users will interact with your knowledge hub through WhatsApp.
                  </p>
                  <p className="text-sm text-indigo-700">
                    The AI assistant uses Claude 3.5 Sonnet to provide intelligent responses based on your selected category's knowledge.
                  </p>
                </div>
              </div>
              
              <div className="md:col-span-3">
                {chatCategory ? (
                  <div className="border rounded-lg flex flex-col h-[500px]">
                    <div className="bg-green-500 text-white p-3 rounded-t-lg flex items-center">
                      <Smartphone size={20} className="mr-2" />
                      <span className="font-medium">
                        WhatsApp Chat - {categories.find(c => c.id === chatCategory)?.name} 
                        {getCategoryWhatsappNumber(chatCategory) ? ` (${getCategoryWhatsappNumber(chatCategory)})` : ''}
                      </span>
                    </div>
                    
                    <div 
                      ref={chatContainerRef}
                      className="flex-grow p-4 overflow-y-auto bg-[#e5ded8]"
                    >
                      {filteredChatMessages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-center">
                          <MessageSquare size={48} className="text-gray-400 mb-4" />
                          <h3 className="text-lg font-medium text-gray-700 mb-2">No Messages Yet</h3>
                          <p className="text-gray-600">
                            Start a conversation to see how the AI responds to your queries about the {categories.find(c => c.id === chatCategory)?.name} category.
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {filteredChatMessages.map(message => (
                            <div 
                              key={message.id}
                              className={`max-w-[80%] p-3 rounded-lg ${
                                message.sender === 'user' 
                                  ? 'ml-auto bg-[#dcf8c6]' 
                                  : 'mr-auto bg-white'
                              }`}
                            >
                              {message.sender === 'ai' ? (
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                              ) : (
                                <p>{message.content}</p>
                              )}
                              <p className="text-right text-xs text-gray-500 mt-1">
                                {message.timestamp.toLocaleDateString([], { hour: '2-digit', minute: '2-digit' })}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="p-3 border-t flex">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-grow px-3 py-2 border rounded-l-md"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSendMessage();
                        }}
                      />
                      <button
                        onClick={handleSendMessage}
                        className="px-4 py-2 bg-green-500 text-white rounded-r-md hover:bg-green-600 transition-colors"
                        disabled={!newMessage.trim()}
                      >
                        <Send size={20} />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="h-[500px] flex flex-col items-center justify-center text-center p-6 bg-gray-50 rounded-md">
                    <MessageSquare size={48} className="text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-700 mb-2">Chat Not Available</h3>
                    <p className="text-gray-600 mb-4">
                      Select a category to chat with.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
      
      <footer className="bg-gray-800 text-white p-4 mt-8">
        <div className="container mx-auto text-center">
          <p>Knowledge Hub with WhatsApp AI Integration &copy; 2025</p>
          <p className="text-sm text-gray-400 mt-1">
            Powered by Claude 3.5 Sonnet
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;