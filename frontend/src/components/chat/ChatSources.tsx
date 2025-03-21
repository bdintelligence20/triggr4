// components/chat/ChatSources.tsx
import React, { useState } from 'react';
import { FileText, ExternalLink, ChevronDown, ChevronUp, File, FileImage } from 'lucide-react';
import { Source } from '../../types';

interface ChatSourcesProps {
  sources: Array<Source>;
}

const ChatSources: React.FC<ChatSourcesProps> = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  // Sort sources by relevance score (highest first)
  const sortedSources = [...sources].sort((a, b) => b.relevance_score - a.relevance_score);
  
  // Get the top 3 sources for the collapsed view
  const topSources = sortedSources.slice(0, 3);
  const hasMoreSources = sources.length > 3;

  // Get source name - use document title if available, otherwise format the ID
  const getSourceName = (source: Source) => {
    if (source.document && source.document.title) {
      return source.document.title;
    }
    
    // Fallback to ID parsing
    const parts = source.id.split('_');
    return parts[0]; // Return the first part of the ID
  };
  
  // Get file icon based on type
  const getFileIcon = (source: Source) => {
    if (!source.document) return <FileText size={14} />;
    
    const fileType = source.document.file_type;
    switch(fileType) {
      case 'pdf': return <File size={14} />;
      case 'doc': case 'docx': return <FileText size={14} />;
      case 'jpg': case 'png': case 'gif': return <FileImage size={14} />;
      default: return <FileText size={14} />;
    }
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
              <div className="flex flex-col">
                <div className="flex items-center">
                  {getFileIcon(source)}
                  <span className="font-medium ml-1">{getSourceName(source)}</span>
                </div>
                {source.document && source.document.file_type && (
                  <span className="text-gray-500 dark:text-gray-400 text-[10px]">
                    {source.document.file_type.toUpperCase()}
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-gray-500 dark:text-gray-400 mr-2">
                {(source.relevance_score * 100).toFixed(0)}% match
              </span>
              {source.document && source.document.file_url ? (
                <a 
                  href={source.document.file_url} 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-500 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300"
                  title="View source document"
                >
                  <ExternalLink size={12} />
                </a>
              ) : (
                <span 
                  className="text-gray-400 dark:text-gray-600 cursor-not-allowed"
                  title="Source document not available"
                >
                  <ExternalLink size={12} />
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatSources;
