// components/chat/ChatSources.tsx
import React from 'react';

interface ChatSourcesProps {
  sources: Array<{id: string, relevance_score: number}>;
}

const ChatSources: React.FC<ChatSourcesProps> = ({ sources }) => {
  return (
    <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
      <p className="text-xs text-gray-500 dark:text-gray-400">Sources:</p>
      <div className="mt-1 flex flex-wrap gap-1">
        {sources.map((source, index) => (
          <span 
            key={index}
            className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full"
            title={`Relevance: ${(source.relevance_score * 100).toFixed(1)}%`}
          >
            {source.id.split('_')[0]}
          </span>
        ))}
      </div>
    </div>
  );
};

export default ChatSources;