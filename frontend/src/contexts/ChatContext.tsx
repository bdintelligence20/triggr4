import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAppContext } from './AppContext';
import { useAuth } from './AuthContext';
import { useChat as useExistingChat } from '../hooks/useChat';
import { API_URL } from '../types';
import * as api from '../services/api';

// Define types for chat threads and messages
export interface ChatSender {
  name: string;
  department?: string;
}

export interface ChatThread {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  type: 'ai' | 'employee';
  status?: 'pending' | 'resolved';
  hubName?: string;
  unreadCount: number;
  sender: ChatSender;
}

export interface ChatMessage {
  id: string;
  type: 'ai' | 'employee';
  content: string;
  timestamp: string;
  sender: ChatSender;
  isRead: boolean;
  sources?: Array<{id: string, relevance_score: number}>;
}

export interface ChatSession {
  id: string;
  title: string;
  last_message: string;
  updated_at: any;
  created_at: any;
  category: string;
  message_count: number;
}

interface ChatContextType {
  threads: ChatThread[];
  activeThread: ChatThread | null;
  messages: ChatMessage[];
  chatHistory: ChatSession[];
  setActiveThread: (threadId: string) => void;
  sendMessage: (content: string) => Promise<void>;
  createThread: (title: string) => string;
  loadChatHistory: () => Promise<void>;
  loadChatSession: (sessionId: string) => Promise<void>;
  saveChatSession: (title?: string) => Promise<string>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThread, setActiveThreadState] = useState<ChatThread | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Get user and organization info from auth context
  const { user } = useAuth();
  const organizationId = user?.organizationId;
  
  const { 
    chatCategory, 
    setChatCategory,
    chatMessages, 
    setChatMessages,
    newMessage,
    setNewMessage
  } = useAppContext();
  
  const { handleSendMessage } = useExistingChat();
  
  // Initialize with a default thread if none exists
  useEffect(() => {
    if (threads.length === 0) {
      const defaultThread: ChatThread = {
        id: 'default',
        title: 'AI Conversation',
        lastMessage: 'How can I assist you today?',
        timestamp: new Date().toISOString(),
        type: 'ai',
        unreadCount: 0,
        sender: {
          name: 'AI Assistant'
        }
      };
      setThreads([defaultThread]);
      setActiveThreadState(defaultThread);
    }
  }, [threads.length]);
  
  // Convert AppContext chat messages to thread messages
  useEffect(() => {
    if (activeThread && chatMessages.length > 0) {
      const threadMessages: ChatMessage[] = chatMessages.map(msg => ({
        id: msg.id.toString(),
        type: msg.sender === 'user' ? 'employee' as const : 'ai' as const,
        content: msg.content,
        timestamp: msg.timestamp.toISOString(),
        sender: {
          name: msg.sender === 'user' ? 'You' : 'AI Assistant'
        },
        isRead: true,
        sources: msg.sources
      }));
      setMessages(threadMessages);
    }
  }, [activeThread, chatMessages]);
  
  // Create threads from chat messages
  useEffect(() => {
    // Group messages by category
    const messagesByCategory: Record<string, typeof chatMessages> = {};
    
    chatMessages.forEach(msg => {
      if (msg.category) {
        if (!messagesByCategory[msg.category]) {
          messagesByCategory[msg.category] = [];
        }
        messagesByCategory[msg.category].push(msg);
      }
    });
    
    // Create threads from categories
    const newThreads: ChatThread[] = Object.entries(messagesByCategory).map(([category, msgs]) => {
      const lastMsg = msgs[msgs.length - 1];
      return {
        id: category,
        title: `Chat about ${category}`,
        lastMessage: lastMsg.content,
        timestamp: lastMsg.timestamp.toISOString(),
        type: lastMsg.sender === 'user' ? 'employee' as const : 'ai' as const,
        unreadCount: 0,
        sender: {
          name: lastMsg.sender === 'user' ? 'You' : 'AI Assistant'
        }
      };
    });
    
    // Add default thread if no threads exist
    if (newThreads.length === 0 && threads.length === 0) {
      newThreads.push({
        id: 'default',
        title: 'AI Conversation',
        lastMessage: 'How can I assist you today?',
        timestamp: new Date().toISOString(),
        type: 'ai',
        unreadCount: 0,
        sender: {
          name: 'AI Assistant'
        }
      });
    }
    
    if (newThreads.length > 0) {
      setThreads(newThreads);
    }
  }, [chatMessages, threads.length]);
  
  const setActiveThread = (threadId: string) => {
    const thread = threads.find(t => t.id === threadId);
    if (thread) {
      setActiveThreadState(thread);
      setChatCategory(threadId);
    }
  };
  
  const createThread = (title: string) => {
    const newThreadId = Date.now().toString();
    const newThread: ChatThread = {
      id: newThreadId,
      title,
      lastMessage: '',
      timestamp: new Date().toISOString(),
      type: 'ai',
      unreadCount: 0,
      sender: {
        name: 'AI Assistant'
      }
    };
    setThreads(prev => [...prev, newThread]);
    setActiveThreadState(newThread);
    setChatCategory(newThreadId);
    return newThreadId;
  };
  
  // Use the existing useChat hook functionality
  const sendMessage = async (content: string) => {
    if (!content.trim()) return;
    
    // Set the message in AppContext
    setNewMessage(content);
    
    // Use the existing hook to send the message
    await handleSendMessage();
  };
  
  // Load chat history from the server
  const loadChatHistory = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_URL}/chat/history`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load chat history');
      }
      
      const data = await response.json();
      setChatHistory(data.sessions || []);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load a specific chat session
  const loadChatSession = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_URL}/chat/session/${sessionId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load chat session');
      }
      
      const session = await response.json();
      
      // Convert session messages to app format
      const sessionMessages = session.messages.map((msg: any) => ({
        id: msg.id.toString(),
        type: msg.sender === 'user' ? 'employee' as const : 'ai' as const,
        content: msg.content,
        timestamp: msg.timestamp,
        sender: {
          name: msg.sender === 'user' ? 'You' : 'AI Assistant'
        },
        isRead: true,
        sources: msg.sources
      }));
      
      // Update AppContext with session messages
      setChatMessages(sessionMessages.map((msg: any) => {
        // Safely create a Date object from the timestamp
        let timestamp;
        try {
          timestamp = msg.timestamp ? new Date(msg.timestamp) : new Date();
          // Validate the date is valid
          if (isNaN(timestamp.getTime())) {
            timestamp = new Date(); // Fallback to current date if invalid
          }
        } catch (e) {
          timestamp = new Date(); // Fallback to current date if error
        }
        
        return {
          id: msg.id,
          content: msg.content,
          sender: msg.type === 'employee' ? 'user' : 'ai',
          timestamp: timestamp,
          category: session.category,
          sources: msg.sources
        };
      }));
      
      setChatCategory(session.category);
      
      // Create or update thread
      const thread: ChatThread = {
        id: sessionId,
        title: session.title,
        lastMessage: session.last_message,
        timestamp: new Date(session.updated_at).toISOString(),
        type: 'ai',
        unreadCount: 0,
        sender: { name: 'AI Assistant' }
      };
      
      setActiveThreadState(thread);
      
      // Update threads list if needed
      setThreads(prev => {
        const exists = prev.some(t => t.id === sessionId);
        if (!exists) {
          return [...prev, thread];
        }
        return prev.map(t => t.id === sessionId ? thread : t);
      });
    } catch (error) {
      console.error('Failed to load chat session:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Save current chat session
  const saveChatSession = async (title?: string) => {
    try {
      if (chatMessages.length === 0) return '';
      
      // Format messages for API
      const messages = chatMessages.map(msg => ({
        id: msg.id.toString(),
        content: msg.content,
        sender: msg.sender,
        timestamp: msg.timestamp.toISOString(),
        sources: msg.sources
      }));
      
      // Use active thread title or generate one from first message
      const sessionTitle = title || (activeThread ? activeThread.title : 
        chatMessages.length > 0 ? `Chat about ${chatMessages[0].content.substring(0, 30)}...` : 'Chat Session');
      
      const response = await fetch(`${API_URL}/chat/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          session_id: activeThread?.id !== 'default' ? activeThread?.id : undefined,
          title: sessionTitle,
          messages,
          category: chatCategory
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to save chat session');
      }
      
      const data = await response.json();
      
      // Update active thread with new ID if it was a new session
      if (!activeThread || activeThread.id === 'default') {
        const newThread: ChatThread = {
          id: data.session_id,
          title: sessionTitle,
          lastMessage: messages[messages.length - 1].content,
          timestamp: new Date().toISOString(),
          type: 'ai',
          unreadCount: 0,
          sender: { name: 'AI Assistant' }
        };
        setActiveThreadState(newThread);
        setThreads(prev => [...prev.filter(t => t.id !== 'default'), newThread]);
      }
      
      // Refresh chat history
      loadChatHistory();
      
      return data.session_id;
    } catch (error) {
      console.error('Failed to save chat session:', error);
      return '';
    }
  };
  
  // Load chat history when component mounts or organization changes
  useEffect(() => {
    if (organizationId) {
      console.log(`Loading chat history for organization: ${organizationId}`);
      loadChatHistory();
      
      // Reset state when organization changes
      return () => {
        setThreads([]);
        setActiveThreadState(null);
        setMessages([]);
        setChatHistory([]);
      };
    }
  }, [organizationId]);
  
  // Auto-save chat session when messages change
  useEffect(() => {
    if (chatMessages.length > 0 && activeThread && organizationId) {
      const saveTimeout = setTimeout(() => {
        saveChatSession();
      }, 2000);
      
      return () => clearTimeout(saveTimeout);
    }
  }, [chatMessages, organizationId]);
  
  return (
    <ChatContext.Provider value={{
      threads,
      activeThread,
      messages,
      chatHistory,
      setActiveThread,
      sendMessage,
      createThread,
      loadChatHistory,
      loadChatSession,
      saveChatSession
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
