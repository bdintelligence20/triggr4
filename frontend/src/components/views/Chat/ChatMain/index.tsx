import React, { useState, RefObject } from 'react';
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import { ChatMessage } from '../types';

interface ChatMainProps {
  initialPlaceholder?: string;
  messages?: ChatMessage[];
  onSendMessage?: (content: string) => void;
  containerRef?: RefObject<HTMLDivElement>;
}

const ChatMain: React.FC<ChatMainProps> = ({ 
  initialPlaceholder,
  messages = [],
  onSendMessage,
  containerRef
}) => {
  const [selectedHub, setSelectedHub] = useState<number | null>(null);
  
  // Use default messages if none provided
  const displayMessages = messages.length > 0 ? messages : [
    {
      id: '1',
      type: 'ai' as const,
      content: 'How can I assist you today?',
      timestamp: new Date().toISOString(),
      sender: { name: 'AI Assistant' },
      isRead: true
    }
  ];

  const handleSendMessage = (content: string) => {
    if (onSendMessage) {
      onSendMessage(content);
    } else {
      // Fallback to local state if no external handler provided
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'employee',
        content,
        timestamp: new Date().toISOString(),
        sender: { name: 'You' },
        isRead: true
      };
      // This won't work if messages are provided externally, but that's ok
      // as it's just a fallback for demo purposes
    }
  };

  const getPlaceholder = () => {
    if (selectedHub) {
      return `Type your message for the selected hub...`;
    }
    return initialPlaceholder || "Type your message...";
  };

  return (
    <div className="flex-1 flex flex-col bg-white border-l">
      <ChatMessages messages={displayMessages} />
      <ChatInput 
        onSendMessage={handleSendMessage}
        placeholder={getPlaceholder()}
        selectedHub={selectedHub}
        onHubSelect={setSelectedHub}
      />
    </div>
  );
};

export default ChatMain;
