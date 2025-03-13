// components/chat/ChatPanel.tsx
import React from 'react';
import ChatCategories from './ChatCategories';
import ChatWindow from './ChatWindow';

const ChatPanel: React.FC = () => {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 transition-colors duration-300">
      <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">Chat Simulation</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <ChatCategories />
        <ChatWindow />
      </div>
    </div>
  );
};

export default ChatPanel;