// components/chat/ChatWindow.tsx
import React from 'react';
import { Book, MessageSquare } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { useChat } from '../../hooks/useChat';
import { useAppContext } from '../../contexts/AppContext';

const ChatWindow: React.FC = () => {
  const { 
    chatCategory,
    filteredChatMessages,
    categories
  } = useAppContext();
  
  const { chatContainerRef } = useChat();

  return (
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
                  <ChatMessage key={message.id} message={message} />
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
      
      <ChatInput />
    </div>
  );
};

export default ChatWindow;