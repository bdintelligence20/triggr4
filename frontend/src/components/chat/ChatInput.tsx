// components/chat/ChatInput.tsx
import React from 'react';
import { Send, Zap } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { useAppContext } from '../../contexts/AppContext';

const ChatInput: React.FC = () => {
  const { 
    newMessage,
    setNewMessage,
    useEnhancedRAG,
    setUseEnhancedRAG
  } = useAppContext();
  
  const { handleSendMessage } = useChat();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-end mb-1">
        <div 
          className="flex items-center cursor-pointer text-sm"
          onClick={() => setUseEnhancedRAG(!useEnhancedRAG)}
        >
          <span className={`mr-2 ${useEnhancedRAG ? 'text-emerald-500' : 'text-gray-500'}`}>
            Enhanced RAG
          </span>
          <div className={`relative inline-block w-10 h-5 transition-colors duration-200 ease-in-out rounded-full ${useEnhancedRAG ? 'bg-emerald-400' : 'bg-gray-300'}`}>
            <div className={`absolute left-0.5 top-0.5 w-4 h-4 transition-transform duration-200 ease-in-out transform ${useEnhancedRAG ? 'translate-x-5' : 'translate-x-0'} bg-white rounded-full shadow-md`}></div>
          </div>
          <Zap size={16} className={`ml-2 ${useEnhancedRAG ? 'text-emerald-500' : 'text-gray-500'}`} />
        </div>
      </div>
      <div className="flex">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message..."
          className="flex-grow px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-l-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 dark:focus:ring-emerald-500 transition-colors"
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={handleSendMessage}
          disabled={!newMessage.trim()}
          className="px-4 py-3 bg-emerald-400 hover:bg-emerald-300 text-white rounded-r-lg transition-colors disabled:bg-gray-200 disabled:text-gray-500 dark:disabled:bg-gray-700 dark:disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
