import React, { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import ChatThreadItem from './ChatThreadItem';
import { ChatThread } from '../types';
import { useAppContext } from '../../../../contexts/AppContext';

interface ChatSidebarProps {
  onThreadSelect: (threadId: string) => void;
  activeThreadId?: string;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({ onThreadSelect, activeThreadId }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const { categories, chatMessages } = useAppContext();

  // Create threads from categories
  const threads: ChatThread[] = useMemo(() => {
    // Start with a default thread
    const result: ChatThread[] = [
      {
        id: 'default',
        title: 'General Chat',
        lastMessage: 'How can I assist you today?',
        timestamp: new Date().toISOString(),
        type: 'ai',
        unreadCount: 0,
        sender: {
          name: 'AI Assistant'
        }
      }
    ];
    
    // Add threads for each category
    categories.forEach(category => {
      if (category.id !== 'all') {
        // Find the last message for this category
        const lastMessage = chatMessages
          .filter(msg => msg.category === category.id)
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
        
        result.push({
          id: category.id,
          title: category.name,
          lastMessage: lastMessage?.content || 'No messages yet',
          timestamp: lastMessage?.timestamp.toISOString() || new Date().toISOString(),
          type: 'ai',
          unreadCount: 0,
          sender: {
            name: 'AI Assistant'
          }
        });
      }
    });
    
    return result;
  }, [categories, chatMessages]);

  const filteredThreads = threads.filter(thread => {
    const searchString = `${thread.title} ${thread.lastMessage} ${thread.sender.name}`.toLowerCase();
    return searchString.includes(searchQuery.toLowerCase());
  });

  return (
    <div className="w-80 border-r border-gray-200 flex flex-col h-full bg-white">
      {/* Search Bar */}
      <div className="p-4 border-b">
        <div className="relative">
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {filteredThreads.map(thread => (
          <ChatThreadItem
            key={thread.id}
            thread={thread}
            isActive={thread.id === activeThreadId}
            onClick={() => onThreadSelect(thread.id)}
          />
        ))}
      </div>
    </div>
  );
};

export default ChatSidebar;
