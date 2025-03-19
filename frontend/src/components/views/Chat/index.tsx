import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ChatSidebar from './ChatSidebar';
import ChatMain from './ChatMain';
import { useChat } from '../../../hooks/useChat';
import { useAppContext } from '../../../contexts/AppContext';
import { ChatMessage } from './types';

const Chat = () => {
  const [activeThreadId, setActiveThreadId] = useState<string | undefined>('default');
  const location = useLocation();
  const { chatType, placeholder } = location.state || {};
  
  const { chatContainerRef, handleSendMessage } = useChat();
  const { setChatCategory, chatMessages } = useAppContext();

  // Convert AppContext ChatMessages to the format expected by ChatMain
  const convertedMessages: ChatMessage[] = chatMessages.map(msg => ({
    id: msg.id.toString(),
    content: msg.content,
    timestamp: msg.timestamp.toISOString(),
    sender: {
      name: msg.sender === 'user' ? 'You' : 'AI Assistant'
    },
    type: msg.sender === 'user' ? 'employee' : 'ai',
    isRead: true
  }));

  // Handle thread selection
  const handleThreadSelect = (threadId: string) => {
    setActiveThreadId(threadId);
    setChatCategory(threadId);
  };

  // Create a new thread when redirected from FAB
  useEffect(() => {
    if (chatType) {
      const newThreadId = Date.now().toString();
      setActiveThreadId(newThreadId);
      setChatCategory(newThreadId);
    }
  }, [chatType, setChatCategory]);

  return (
    <div className="flex h-[calc(100vh-64px)]">
      <ChatSidebar 
        onThreadSelect={handleThreadSelect}
        activeThreadId={activeThreadId}
      />
      <ChatMain 
        initialPlaceholder={placeholder}
        messages={convertedMessages}
        onSendMessage={handleSendMessage}
        containerRef={chatContainerRef}
      />
    </div>
  );
};

export default Chat;
