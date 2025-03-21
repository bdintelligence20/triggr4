// components/chat/ChatSources.tsx
import React, { useState } from 'react';
import { FileText, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

interface ChatSourcesProps {
  sources: Array<{id: string, relevance_score: number}>;
}

const ChatSources: React.FC<ChatSourcesProps> = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  // Sort sources by relevance score (highest first)
  const sortedSources = [...sources].sort((a, b) => b.relevance_score - a.relevance_score);
  
  // Get the top 3 sources for the collapsed view
  const topSources = sortedSources.slice(0, 3);
  const hasMoreSources = sources.length > 3;

  // Format the source ID for display
  const formatSourceName = (id: string) => {
    const parts = id.split('_');
    return parts[0]; // Return the first part of the ID
  };

  return (
    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center">
          <FileText size={14} className="mr-1" />
          Sources ({sources.length})
        </p>
        {hasMoreSources && (
          <button 
            onClick={() => setExpanded(!expanded)} 
            className="text-xs text-emerald-500 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300 flex items-center"
          >
            {expanded ? (
              <>
                <ChevronUp size={14} className="mr-1" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown size={14} className="mr-1" />
                Show all
              </>
            )}
          </button>
        )}
      </div>
      
      <div className="mt-2 space-y-2">
        {(expanded ? sortedSources : topSources).map((source, index) => (
          <div 
            key={index}
            className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-md text-xs"
          >
            <div className="flex items-center">
              <div className="w-5 h-5 flex items-center justify-center bg-emerald-100 dark:bg-emerald-900 text-emerald-600 dark:text-emerald-400 rounded-full mr-2 text-[10px] font-bold">
                {index + 1}
              </div>
              <span className="font-medium">{formatSourceName(source.id)}</span>
            </div>
            <div className="flex items-center">
              <span className="text-gray-500 dark:text-gray-400 mr-2">
                {(source.relevance_score * 100).toFixed(0)}% match
              </span>
              <a 
                href={`#source-${source.id}`} 
                className="text-emerald-500 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300"
                title="View source document"
              >
                <ExternalLink size={12} />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatSources;
