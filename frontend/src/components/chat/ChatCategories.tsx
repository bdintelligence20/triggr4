// components/chat/ChatCategories.tsx
import React from 'react';
import ChatHistory from './ChatHistory';

const ChatCategories: React.FC = () => {
  return (
    <div className="md:col-span-1">
      {/* Only show Chat History section */}
      <ChatHistory />
    </div>
  );
};

export default ChatCategories;
