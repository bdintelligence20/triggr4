import { useState, useRef, useEffect } from 'react';
import { Book, FileText, File as FilePdf, Upload, Search, MessageSquare, Send, Moon, Sun, Menu, X, Home, 
  Users, Plug, ChevronDown, ChevronRight, Plus, Share2, Copy, Mail, Phone, AlertCircle, FileIcon, Trash2 } from 'lucide-react';
import * as pdfjs from 'pdfjs-dist';
import * as mammoth from 'mammoth';
import ReactMarkdown from 'react-markdown';

// Set worker path for PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

// Replace with your actual backend URL
const API_URL = 'https://triggr4bg.onrender.com';

interface KnowledgeItem {
  id: string;
  title: string;
  content?: string;
  category: string;
  file_type?: string;
  type?: 'text' | 'pdf' | 'doc'; // For UI display
  createdAt: Date;
  processing_status?: string;
  vectors_stored?: number;
  word_count?: number;
  fileSize?: string;
  fileUrl?: string;
}

interface Category {
  id: string;
  name: string;
  whatsappNumber?: string;
}

interface ChatMessage {
  id: string | number;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  category?: string;
}

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('library');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categoriesOpen, setCategoriesOpen] = useState(true);
  
  // Chat related states
  const [chatCategory, setChatCategory] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  
  // App specific states
  const [notification, setNotification] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [whatsappNumber, setWhatsappNumber] = useState<string | null>(null);
  const [showShareOptions, setShowShareOptions] = useState(false);
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([
    { id: 'all', name: 'All Items' },
    { id: 'general', name: 'General' },
    { id: 'documents', name: 'Documents' }
  ]);
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  
  // Refs
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mainContentRef = useRef<HTMLDivElement>(null);

  // Filter knowledge items based on search query and selected category
  const filteredKnowledgeItems = knowledgeItems.filter(item => {
    const matchesSearch = !searchQuery || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.content && item.content.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || 
                           (selectedCategory === 'documents' ? (item.type === 'pdf' || item.type === 'doc') 
                            : item.category === selectedCategory);
    
    return matchesSearch && matchesCategory;
  });

  // Filter chat messages based on selected chat category
  const filteredChatMessages = chatCategory ? chatMessages.filter(msg => !msg.category || msg.category === chatCategory) : [];

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

  // Load documents from backend
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
            category: doc.category === 'general' ? 'general' : 'documents',
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
    
    loadDocuments();
  }, []);

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Toggle dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Function to handle file upload
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
        formData.append('category', selectedCategory === 'all' ? 'general' : selectedCategory);
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
        
        // Determine file type
        const fileType = fileName.toLowerCase().endsWith('.pdf') ? 'pdf' : 
                        (fileName.toLowerCase().endsWith('.doc') || fileName.toLowerCase().endsWith('.docx')) ? 'doc' : 'text';
        
        // Create new knowledge item
        const newItem: KnowledgeItem = {
          id: result.item_id || Date.now().toString() + i,
          title: fileName,
          category: selectedCategory === 'all' ? 'general' : selectedCategory,
          createdAt: new Date(),
          type: fileType,
          fileSize: formatFileSize(file.size),
          fileUrl: result.file_url,
          processing_status: 'completed'
        };
        
        setKnowledgeItems(prev => [...prev, newItem]);
        setProcessingProgress(((i + 1) / files.length) * 100);
        
        // Show notification
        setNotification("File uploaded successfully");
        setTimeout(() => setNotification(null), 3000);
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

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !chatCategory) return;
    
    // Add user message
    const userMessageId = Date.now();
    const userMessage = {
      id: userMessageId,
      content: newMessage,
      sender: 'user',
      timestamp: new Date(),
      category: chatCategory
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    
    // Create placeholder for AI response
    const aiMessageId = userMessageId + 1;
    const aiPlaceholder = {
      id: aiMessageId,
      content: "",
      sender: 'ai',
      timestamp: new Date(),
      category: chatCategory,
      isStreaming: true
    };
    
    setChatMessages(prev => [...prev, aiPlaceholder]);
    
    try {
      // Convert category ID to name for API call
      const categoryName = categories.find(c => c.id === chatCategory)?.name || '';
      
      if (window.EventSource) {
        // Use Server-Sent Events for streaming
        const source = new EventSource(`${API_URL}/query?stream=true`, {
          withCredentials: false
        });
        
        // Set up event handlers for SSE
        source.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.chunk) {
            // Update AI message with new chunk
            setChatMessages(prev => 
              prev.map(msg => 
                msg.id === aiMessageId 
                  ? { ...msg, content: msg.content + data.chunk }
                  : msg
              )
            );
          }
          
          if (data.done) {
            // Stream is complete
            source.close();
            
            // Update message to mark streaming as complete
            setChatMessages(prev => 
              prev.map(msg => 
                msg.id === aiMessageId 
                  ? { ...msg, isStreaming: false }
                  : msg
              )
            );
          }
        };
        
        source.onerror = (error) => {
          console.error('EventSource error:', error);
          source.close();
          
          // Update message to indicate error
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === aiMessageId 
                ? { 
                    ...msg, 
                    content: msg.content || "Sorry, I encountered an error while processing your request.",
                    isStreaming: false
                  }
                : msg
            )
          );
        };
        
        // Post the query to initiate streaming
        fetch(`${API_URL}/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: newMessage,
            category: categoryName === 'All Items' ? '' : categoryName.toLowerCase(),
            stream: true  // Enable streaming
          })
        }).catch(err => {
          console.error('Error sending streaming query:', err);
          source.close();
        });
        
      } else {
        // Fallback for browsers not supporting SSE
        const response = await fetch(`${API_URL}/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: newMessage,
            category: categoryName === 'All Items' ? '' : categoryName.toLowerCase(),
            stream: false  // Disable streaming for fallback
          }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to get response: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Update AI message with complete response
        setChatMessages(prev => 
          prev.map(msg => 
            msg.id === aiMessageId 
              ? { 
                  ...msg, 
                  content: result.response || "I couldn't find an answer to your question.",
                  isStreaming: false
                }
              : msg
          )
        );
      }
    } catch (err) {
      console.error('Error getting AI response:', err);
      
      // Update error message
      setChatMessages(prev => 
        prev.map(msg => 
          msg.id === aiMessageId 
            ? { 
                ...msg, 
                content: "Sorry, I encountered an error while processing your request. Please try again later.",
                isStreaming: false
              }
            : msg
        )
      );
    }
  };
  
  // Inside the render of the chat message
  {message.sender === 'ai' ? (
    <div className={`max-w-3/4 rounded-lg p-3 ${
      message.sender === 'user' 
        ? 'bg-emerald-400 dark:bg-emerald-600 text-white' 
        : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white'
    }`}>
      {message.isStreaming && (
        <div className="flex items-center mb-2">
          <div className="animate-pulse h-2 w-2 mr-1 bg-emerald-400 dark:bg-emerald-500 rounded-full"></div>
          <div className="animate-pulse h-2 w-2 mr-1 bg-emerald-400 dark:bg-emerald-500 rounded-full" style={{animationDelay: '0.2s'}}></div>
          <div className="animate-pulse h-2 w-2 bg-emerald-400 dark:bg-emerald-500 rounded-full" style={{animationDelay: '0.4s'}}></div>
        </div>
      )}
      <ReactMarkdown>{message.content}</ReactMarkdown>
      <p className="text-xs mt-1 opacity-70">
        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </p>
    </div>
  ) : (
    <p>{message.content}</p>
  )}

  // Function to handle deleting a knowledge item
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
      
      // Show notification
      setNotification("Item deleted successfully");
      setTimeout(() => setNotification(null), 3000);
    } catch (err) {
      console.error('Error deleting knowledge item:', err);
      setError(`Failed to delete: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate a WhatsApp number
  const generateWhatsappNumber = () => {
    // In a real app, this would call an API to generate a WhatsApp number
    const countryCode = '+1'; // US code
    const areaCode = Math.floor(Math.random() * 900) + 100; // Random 3-digit area code
    const firstPart = Math.floor(Math.random() * 900) + 100; // Random 3-digit number
    const secondPart = Math.floor(Math.random() * 9000) + 1000; // Random 4-digit number
    
    const number = `${countryCode} (${areaCode}) ${firstPart}-${secondPart}`;
    setWhatsappNumber(number);
    setShowShareOptions(true);
    
    // Update categories with whatsapp number if a category is selected
    if (chatCategory && chatCategory !== 'all') {
      setCategories(categories.map(category => 
        category.id === chatCategory 
          ? { ...category, whatsappNumber: number } 
          : category
      ));
    }
    
    // Show notification
    setNotification("WhatsApp number generated");
    setTimeout(() => setNotification(null), 3000);
  };

  // Copy WhatsApp number to clipboard
  const copyToClipboard = () => {
    if (whatsappNumber) {
      navigator.clipboard.writeText(whatsappNumber);
      setNotification("Number copied to clipboard");
      setTimeout(() => setNotification(null), 3000);
    }
  };

  // Share number via different methods
  const shareVia = (method: string) => {
    if (!whatsappNumber) return;
    
    let shareUrl = '';
    const message = `Here's the WhatsApp number for my knowledge base: ${whatsappNumber}`;
    
    switch (method) {
      case 'whatsapp':
        shareUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
        break;
      case 'email':
        shareUrl = `mailto:?subject=Knowledge%20Base%20WhatsApp%20Number&body=${encodeURIComponent(message)}`;
        break;
      case 'sms':
        shareUrl = `sms:?body=${encodeURIComponent(message)}`;
        break;
      default:
        return;
    }
    
    // Open in a new tab
    window.open(shareUrl, '_blank');
  };

  // Helper function to format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  // Function to get count of knowledge entries by category and type
  const getCategoryKnowledgeCount = (categoryId: string, type: string) => {
    if (categoryId === 'all') {
      return knowledgeItems.filter(item => item.type === type).length;
    } else if (categoryId === 'documents') {
      return knowledgeItems.filter(item => (item.type === 'pdf' || item.type === 'doc') && item.type === type).length;
    } else {
      return knowledgeItems.filter(item => item.category === categoryId && item.type === type).length;
    }
  };

  // Function to get file icon based on type
  const getFileIcon = (type?: string) => {
    switch (type) {
      case 'pdf':
        return <FilePdf size={20} className="text-red-500 dark:text-red-400 ml-2 flex-shrink-0" />;
      case 'doc':
        return <FileText size={20} className="text-blue-500 dark:text-blue-400 ml-2 flex-shrink-0" />;
      default:
        return <FileText size={20} className="text-gray-500 dark:text-gray-400 ml-2 flex-shrink-0" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-800 transition-colors duration-300">
      <div className="flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 py-4 px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 mr-3 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
              >
                {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
              <h1 className="text-xl font-bold text-emerald-500">triggrHub</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
              >
                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  placeholder="Search knowledge..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 dark:focus:ring-emerald-500 transition-colors w-64"
                />
              </div>
            </div>
          </div>
        </header>
        
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <aside 
            className={`w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${
              sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            } lg:translate-x-0 fixed lg:relative z-40 h-[calc(100vh-4rem)]`}
          >
            <div className="flex-grow overflow-y-auto py-4 flex flex-col h-full">
              <nav className="px-4 space-y-1 flex-grow">
                <button
                  onClick={() => setActiveTab('library')}
                  className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                    activeTab === 'library' 
                      ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <Book size={20} className="mr-3" />
                  <span>Library</span>
                </button>
                
                <div className="pt-2">
                  <button
                    onClick={() => setCategoriesOpen(!categoriesOpen)}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="flex items-center">
                      <FileText size={20} className="mr-3" />
                      <span>Hubs</span>
                    </div>
                    {categoriesOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  </button>
                  
                  {categoriesOpen && (
                    <div className="ml-6 mt-1 space-y-1">
                      {categories.map(category => (
                        <button
                          key={category.id}
                          onClick={() => {
                            setSelectedCategory(category.id);
                            setActiveTab('library');
                          }}
                          className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                            selectedCategory === category.id && activeTab === 'library'
                              ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' 
                              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                          }`}
                        >
                          <span>{category.name}</span>
                        </button>
                      ))}
                      
                      <button
                        className="w-full flex items-center px-3 py-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        onClick={() => {
                          const newCategoryName = prompt("Enter new category name:");
                          if (newCategoryName && newCategoryName.trim()) {
                            const newId = newCategoryName.toLowerCase().replace(/\s+/g, '-');
                            setCategories([...categories, { id: newId, name: newCategoryName.trim() }]);
                            setNotification("Category added");
                            setTimeout(() => setNotification(null), 3000);
                          }
                        }}
                      >
                        <Plus size={16} className="mr-2" />
                        <span>Add Category</span>
                      </button>
                    </div>
                  )}
                </div>
                
                <button
                  onClick={() => setActiveTab('integration')}
                  className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
                    activeTab === 'integration' 
                      ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <Plug size={20} className="mr-3" />
                  <span>Integration</span>
                </button>
              </nav>
              
              {/* Chat button at the bottom */}
              <div className="px-4 mt-auto pb-4">
                <button
                  onClick={() => setActiveTab('chat')}
                  className="w-full flex items-center px-3 py-2 rounded-md bg-emerald-500 hover:bg-emerald-600 text-white transition-colors"
                >
                  <MessageSquare size={20} className="mr-3" />
                  <span>Chat</span>
                </button>
              </div>
            </div>
          </aside>
          
          {/* Main content */}
          <main 
            ref={mainContentRef}
            className="flex-1 overflow-y-auto p-6 lg:p-8 bg-gray-50 dark:bg-gray-800 relative"
          >
            {/* Notification */}
            {notification && (
              <div className="fixed top-20 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded-md shadow-lg z-50 animate-fade-in-out">
                {notification}
              </div>
            )}
            
            {/* Error message if present */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start">
                <AlertCircle size={20} className="mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Error</p>
                  <p>{error}</p>
                </div>
              </div>
            )}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-6">
                <p className="font-medium">Loading...</p>
                <p>Please wait while we process your request.</p>
              </div>
            )}
            
            <div className="max-w-7xl mx-auto">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 md:mb-0">
                  {activeTab === 'library' && 'Knowledge Library'}
                  {activeTab === 'integration' && 'Integration'}
                  {activeTab === 'chat' && 'AI Chat Assistant'}
                </h1>
                
                {activeTab === 'library' && (
                  <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      accept=".pdf,.doc,.docx,.txt"
                      className="hidden"
                    />
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="btn-primary flex items-center justify-center"
                      disabled={isProcessingFile}
                    >
                      <Upload size={18} className="mr-2" />
                      <span>{isProcessingFile ? 'Uploading...' : 'Add Knowledge'}</span>
                    </button>
                  </div>
                )}
              </div>
              
              {isProcessingFile && (
                <div className="mb-6">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Processing documents... {Math.round(processingProgress)}%</p>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                    <div 
                      className="bg-emerald-500 h-2.5 rounded-full" 
                      style={{ width: `${processingProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {activeTab === 'library' && (
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
                        <div key={item.id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                          <div className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h3 className="font-medium text-gray-900 dark:text-white">{item.title}</h3>
                              {getFileIcon(item.type)}
                            </div>
                            
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                              {item.content ? 
                                 `${item.content.substring(0, 150)}${item.content.length > 150 ? '...' : ''}` 
                                : `File: ${item.fileUrl || item.title}`}
                            </p>
                            
                            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                              <span>
                                {item.createdAt.toLocaleDateString('en-US', { 
                                  year: 'numeric', 
                                  month: 'short', 
                                  day: 'numeric' 
                                })}
                              </span>
                              <span className="capitalize px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full">
                                {item.category}
                              </span>
                            </div>
                          </div>
                          
                          <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 flex justify-between">
                            <button 
                              className="text-sm text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors"
                              onClick={() => {
                                // View functionality - could open a modal or navigate to a detail page
                                setNotification(`Viewing "${item.title}"`);
                                setTimeout(() => setNotification(null), 3000);
                              }}
                            >
                              View
                            </button>
                            <button 
                              className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
                              onClick={() => handleDeleteKnowledgeItem(item.id)}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
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
                    </div>
                  )}
                </div>
              )}
            
              {activeTab === 'integration' && (
                <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 transition-colors duration-300">
                  <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">Integration Options</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* WhatsApp Integration Card */}
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                      <div className="bg-emerald-50 dark:bg-emerald-900/20 p-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="font-medium text-gray-900 dark:text-white text-lg flex items-center">
                          <MessageSquare className="text-emerald-500 mr-2" size={20} />
                          WhatsApp Integration
                        </h3>
                      </div>
                      
                      <div className="p-6">
                        <p className="text-gray-600 dark:text-gray-400 mb-6">
                          Generate a WhatsApp number to connect with your knowledge base and share it with your team or customers.
                        </p>
                        
                        {whatsappNumber ? (
                          <div className="mb-6">
                            <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-lg mb-4">
                              <span className="font-medium text-gray-900 dark:text-white">{whatsappNumber}</span>
                              <button 
                                onClick={copyToClipboard}
                                className="text-emerald-500 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300"
                              >
                                <Copy size={18} />
                              </button>
                            </div>
                            
                            {showShareOptions && (
                              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">Share via:</p>
                                <div className="flex space-x-4">
                                  <button 
                                    onClick={() => shareVia('whatsapp')}
                                    className="flex flex-col items-center justify-center text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400"
                                  >
                                    <MessageSquare size={24} className="mb-1" />
                                    <span className="text-xs">WhatsApp</span>
                                  </button>
                                  
                                  <button 
                                    onClick={() => shareVia('email')}
                                    className="flex flex-col items-center justify-center text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400"
                                  >
                                    <Mail size={24} className="mb-1" />
                                    <span className="text-xs">Email</span>
                                  </button>
                                  
                                  <button 
                                    onClick={() => shareVia('sms')}
                                    className="flex flex-col items-center justify-center text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400"
                                  >
                                    <Phone size={24} className="mb-1" />
                                    <span className="text-xs">Text</span>
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        ) : (
                          <button 
                            onClick={generateWhatsappNumber}
                            className="btn-primary w-full flex items-center justify-center"
                          >
                            <MessageSquare size={18} className="mr-2" />
                            <span>Generate WhatsApp Number</span>
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {/* API Access Card */}
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
                            className="btn-secondary"
                            onClick={() => {
                              setNotification("API documentation not available yet");
                              setTimeout(() => setNotification(null), 3000);
                            }}
                          >
                            View API Documentation
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            
              {activeTab === 'chat' && (
                <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 transition-colors duration-300">
                  <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">Chat Simulation</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="md:col-span-1">
                      <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Knowledge Sources</h3>
                      
                      <div className="space-y-4">
                        {categories.map(category => (
                          <button
                            key={category.id}
                            onClick={() => setChatCategory(category.id)}
                            className={`w-full text-left p-3 rounded-lg border transition-colors ${
                              chatCategory === category.id 
                                ? 'border-emerald-400 dark:border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20' 
                                : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center">
                                {category.name === 'Documents' ? (
                                  <FilePdf size={18} className="text-red-600 dark:text-red-500 mr-2" />
                                ) : (
                                  <FileText size={18} className="text-blue-500 dark:text-blue-400 mr-2" />
                                )}
                                <span className="font-medium text-gray-900 dark:text-white">{category.name}</span>
                              </div>
                              {chatCategory === category.id && (
                                <div className="h-2 w-2 rounded-full bg-emerald-400 dark:bg-emerald-500"></div>
                              )}
                            </div>
                            
                            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-2">
                              <span>{getCategoryKnowledgeCount(category.id, 'text')} text items</span>
                              <span>•</span>
                              <span>{getCategoryKnowledgeCount(category.id, 'pdf') + getCategoryKnowledgeCount(category.id, 'doc')} documents</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="md:col-span-3 flex flex-col">
                      <div 
                        ref={chatContainerRef}
                        className="flex-grow bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4 h-96 overflow-y-auto"
                      >
                      {chatCategory ? (
                        <>
                          {filteredChatMessages.length > 0 ? (
                            <div className="space-y-4">
                              {filteredChatMessages.map(message => (
                                <div 
                                  key={message.id} 
                                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                  <div 
                                    className={`max-w-3/4 rounded-lg p-3 ${
                                      message.sender === 'user' 
                                        ? 'bg-emerald-400 dark:bg-emerald-600 text-white' 
                                        : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white'
                                    }`}
                                  >
                                    {message.sender === 'ai' ? (
                                      <ReactMarkdown>{message.content}</ReactMarkdown>
                                    ) : (
                                      <p>{message.content}</p>
                                    )}
                                    <p className="text-xs mt-1 opacity-70">
                                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="h-full flex flex-col items-center justify-center text-center">
                              <MessageSquare size={48} className="text-gray-300 dark:text-gray-600 mb-2" />
                              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No messages yet</h3>
                              <p className="text-gray-500 dark:text-gray-400 max-w-md">
                                Start chatting with the AI assistant to get information from the {categories.find(c => c.id === chatCategory)?.name} knowledge base.
                              </p>
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="h-full flex flex-col items-center justify-center text-center">
                          <Book size={48} className="text-gray-300 dark:text-gray-600 mb-2" />
                          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">Select a knowledge source</h3>
                          <p className="text-gray-500 dark:text-gray-400 max-w-md">
                            Choose a category from the left to start chatting with the AI assistant.
                          </p>
                        </div>
                      )}
                      </div>
                    
                      <div className="flex">
                        <input
                          type="text"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          placeholder={chatCategory ? "Type your message..." : "Select a knowledge source first"}
                          className="flex-grow px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-l-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 dark:focus:ring-emerald-500 transition-colors"
                          disabled={!chatCategory}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                              e.preventDefault();
                              handleSendMessage();
                            }
                          }}
                        />
                        <button
                          onClick={handleSendMessage}
                          disabled={!newMessage.trim() || !chatCategory}
                          className="px-4 py-3 bg-emerald-400 hover:bg-emerald-300 text-white rounded-r-lg transition-colors disabled:bg-gray-200 disabled:text-gray-500 dark:disabled:bg-gray-700 dark:disabled:text-gray-400 disabled:cursor-not-allowed"
                        >
                          <Send size={20} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Footer - always at the bottom of content */}
            <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 py-6 text-center text-sm text-gray-500 dark:text-gray-400 mt-8">
              <div className="flex flex-col items-center justify-center space-y-2">
                <p className="text-emerald-500 font-bold">triggrHub</p>
                <p>Made by triggrHub © 2025</p>
                <p>Powered by Claude 3.5 Sonnet</p>
              </div>
            </footer>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;