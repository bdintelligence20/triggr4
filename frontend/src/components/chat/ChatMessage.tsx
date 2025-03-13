// components/chat/ChatMessage.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage as ChatMessageType } from '../../types';
import ChatSources from './ChatSources';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-3/4 rounded-lg p-3 ${
          message.sender === 'user' 
            ? 'bg-emerald-400 dark:bg-emerald-600 text-white' 
            : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white'
        }`}
      >
        {message.sender === 'ai' ? (
          <>
            {message.isStreaming && (
              <div className="flex items-center mb-2">
                <div className="animate-pulse h-2 w-2 mr-1 bg-emerald-400 dark:bg-emerald-500 rounded-full"></div>
                <div className="animate-pulse h-2 w-2 mr-1 bg-emerald-400 dark:bg-emerald-500 rounded-full" style={{animationDelay: '0.2s'}}></div>
                <div className="animate-pulse h-2 w-2 bg-emerald-400 dark:bg-emerald-500 rounded-full" style={{animationDelay: '0.4s'}}></div>
              </div>
            )}
            <ReactMarkdown>{message.content}</ReactMarkdown>
            {message.sources && message.sources.length > 0 && !message.isStreaming && (
              <ChatSources sources={message.sources} />
            )}
          </>
        ) : (
          <p>{message.content}</p>
        )}
        <p className="text-xs mt-1 opacity-70">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};

export default ChatMessage;