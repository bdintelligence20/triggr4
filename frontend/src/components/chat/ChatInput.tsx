// components/chat/ChatInput.tsx
import React from 'react';
import { Send } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { useAppContext } from '../../contexts/AppContext';

const ChatInput: React.FC = () => {
  const { 
    newMessage,
    setNewMessage,
    chatCategory
  } = useAppContext();
  
  const { handleSendMessage } = useChat();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex">
      <input
        type="text"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        placeholder={chatCategory ? "Type your message..." : "Select a knowledge source first"}
        className="flex-grow px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-l-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 dark:focus:ring-emerald-500 transition-colors"
        disabled={!chatCategory}
        onKeyDown={handleKeyDown}
      />
      <button
        onClick={handleSendMessage}
        disabled={!newMessage.trim() || !chatCategory}
        className="px-4 py-3 bg-emerald-400 hover:bg-emerald-300 text-white rounded-r-lg transition-colors disabled:bg-gray-200 disabled:text-gray-500 dark:disabled:bg-gray-700 dark:disabled:text-gray-400 disabled:cursor-not-allowed"
      >
        <Send size={20} />
      </button>
    </div>
  );
};

export default ChatInput;