import React from 'react';
import { useChat } from '../../contexts/ChatContext';
import { MessageCircle, Clock } from 'lucide-react';

const ChatHistory: React.FC = () => {
  const { chatHistory, loadChatSession, activeThread } = useChat();
  
  if (chatHistory.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
        No chat history found. Start a new chat to see it here.
      </div>
    );
  }
  
  return (
    <div className="h-full flex flex-col overflow-hidden">
      <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">{new Date().toLocaleString()}</h3>
      
      <div className="space-y-3 overflow-y-auto flex-grow">
        {chatHistory.map(session => (
          <button
            key={session.id}
            onClick={() => loadChatSession(session.id)}
            className={`w-full text-left p-3 rounded-lg border transition-colors ${
              activeThread?.id === session.id 
                ? 'border-emerald-400 dark:border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20' 
                : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-900 dark:text-white truncate">
                {session.title}
              </span>
              {activeThread?.id === session.id && (
                <div className="h-2 w-2 rounded-full bg-emerald-400 dark:bg-emerald-500"></div>
              )}
            </div>
            
            <div className="mt-1 text-sm text-gray-500 dark:text-gray-400 truncate">
              {session.last_message}
            </div>
            
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
              <div className="flex items-center">
                <MessageCircle size={12} className="mr-1" />
                <span>{session.message_count} messages</span>
              </div>
              <div className="flex items-center">
                <Clock size={12} className="mr-1" />
                <span>
                  {session.created_at && session.created_at.seconds ? 
                    new Date(session.created_at.seconds * 1000).toLocaleString() : 
                    'Recent'}
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChatHistory;
