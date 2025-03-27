import React from 'react';
import ChatCategories from '../../../components/chat/ChatCategories';
import ChatWindow from '../../../components/chat/ChatWindow';
import { useAppContext } from '../../../contexts/AppContext';
import { PlusCircle } from 'lucide-react';

const Chat = () => {
  const { setChatMessages, setChatCategory } = useAppContext();
  
  const handleNewChat = () => {
    // Clear chat messages and reset category to default
    setChatMessages([]);
    setChatCategory('default');
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 transition-colors duration-300 h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Ask questions about your company data</h2>
        <button 
          onClick={handleNewChat}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors"
        >
          <PlusCircle size={16} />
          <span>New Chat</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-[calc(100%-4rem)]">
        <ChatCategories />
        <ChatWindow />
      </div>
    </div>
  );
};

export default Chat;
