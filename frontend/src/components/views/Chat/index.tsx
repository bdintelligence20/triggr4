import React from 'react';
import ChatCategories from '../../../components/chat/ChatCategories';
import ChatWindow from '../../../components/chat/ChatWindow';

const Chat = () => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 transition-colors duration-300 h-full">
      <h2 className="text-xl font-semibold mb-6 text-gray-900">Knowledge Hub Chat</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-[calc(100%-4rem)]">
        <ChatCategories />
        <ChatWindow />
      </div>
    </div>
  );
};

export default Chat;
