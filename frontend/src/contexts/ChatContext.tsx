import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAppContext } from './AppContext';
import { useChat as useExistingChat } from '../hooks/useChat';

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

interface ChatContextType {
  threads: ChatThread[];
  activeThread: ChatThread | null;
  messages: ChatMessage[];
  setActiveThread: (threadId: string) => void;
  sendMessage: (content: string) => Promise<void>;
  createThread: (title: string) => string;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThread, setActiveThreadState] = useState<ChatThread | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  
  const { 
    chatCategory, 
    setChatCategory,
    chatMessages, 
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
  
  return (
    <ChatContext.Provider value={{
      threads,
      activeThread,
      messages,
      setActiveThread,
      sendMessage,
      createThread
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
