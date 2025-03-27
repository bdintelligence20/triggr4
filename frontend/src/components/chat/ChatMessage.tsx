// components/chat/ChatMessage.tsx
import React from 'react';
// @ts-ignore - Ignoring missing type declarations
import ReactMarkdown from 'react-markdown';
// @ts-ignore - Ignoring missing type declarations
import remarkGfm from 'remark-gfm';
// @ts-ignore - Ignoring missing type declarations
import rehypeHighlight from 'rehype-highlight';
import { ChatMessage as ChatMessageType } from '../../types';
import ChatSources from './ChatSources';
// @ts-ignore - Ignoring missing type declarations
import { Components } from 'react-markdown';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-3/4 rounded-lg p-3 ${
          message.sender === 'user' 
            ? 'bg-emerald-400 dark:bg-emerald-600 text-white' 
            : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white'
        }`}
      >
        {message.sender === 'ai' ? (
          <>
            {message.isStreaming && (
              <div className="flex items-center mb-2">
                <div className="animate-pulse h-2 w-2 mr-1 bg-emerald-400 dark:bg-emerald-500 rounded-full"></div>
                <div className="animate-pulse h-2 w-2 mr-1 bg-emerald-400 dark:bg-emerald-500 rounded-full" style={{animationDelay: '0.2s'}}></div>
                <div className="animate-pulse h-2 w-2 bg-emerald-400 dark:bg-emerald-500 rounded-full" style={{animationDelay: '0.4s'}}></div>
              </div>
            )}
            {/* Display first three lines as short description */}
            {message.content && (
              <div className="text-sm mb-3 text-gray-700 dark:text-gray-300">
                {message.content
                  .split('\n')
                  .slice(0, 3)
                  .map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
              </div>
            )}
            <div className="markdown-content">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]} 
                rehypePlugins={[rehypeHighlight]}
                components={{
                  // @ts-ignore - Ignoring type errors for custom components
                  table: ({...props}) => (
                    <div className="overflow-x-auto my-4">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 border border-gray-200 dark:border-gray-700" {...props} />
                    </div>
                  ),
                  // @ts-ignore
                  thead: ({...props}) => (
                    <thead className="bg-gray-50 dark:bg-gray-800" {...props} />
                  ),
                  // @ts-ignore
                  tbody: ({...props}) => (
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700" {...props} />
                  ),
                  // @ts-ignore
                  tr: ({...props}) => (
                    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800" {...props} />
                  ),
                  // @ts-ignore
                  th: ({...props}) => (
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider" {...props} />
                  ),
                  // @ts-ignore
                  td: ({...props}) => (
                    <td className="px-4 py-3 text-sm" {...props} />
                  ),
                  // @ts-ignore
                  code: ({inline, className, children, ...props}) => {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <div className="rounded-md overflow-hidden my-4">
                        <div className="bg-gray-800 text-gray-200 px-4 py-2 text-xs font-semibold">
                          {match[1]}
                        </div>
                        <code
                          className={`${className} block p-4 bg-gray-900 text-gray-100 overflow-x-auto`}
                          {...props}
                        >
                          {children}
                        </code>
                      </div>
                    ) : (
                      <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm" {...props}>
                        {children}
                      </code>
                    );
                  },
                  // @ts-ignore
                  a: ({...props}) => (
                    <a className="text-emerald-500 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300 underline" {...props} />
                  ),
                  // @ts-ignore
                  blockquote: ({...props}) => (
                    <blockquote className="border-l-4 border-gray-200 dark:border-gray-700 pl-4 py-2 my-4 italic text-gray-600 dark:text-gray-400" {...props} />
                  ),
                  // @ts-ignore
                  ul: ({...props}) => (
                    <ul className="list-disc pl-5 my-4 space-y-2" {...props} />
                  ),
                  // @ts-ignore
                  ol: ({...props}) => (
                    <ol className="list-decimal pl-5 my-4 space-y-2" {...props} />
                  ),
                  // @ts-ignore
                  li: ({...props}) => (
                    <li className="mb-1" {...props} />
                  ),
                  // @ts-ignore
                  h1: ({...props}) => (
                    <h1 className="text-2xl font-bold my-4" {...props} />
                  ),
                  // @ts-ignore
                  h2: ({...props}) => (
                    <h2 className="text-xl font-bold my-3" {...props} />
                  ),
                  // @ts-ignore
                  h3: ({...props}) => (
                    <h3 className="text-lg font-bold my-2" {...props} />
                  ),
                  // @ts-ignore
                  h4: ({...props}) => (
                    <h4 className="text-base font-bold my-2" {...props} />
                  ),
                  // @ts-ignore
                  p: ({...props}) => (
                    <p className="my-2" {...props} />
                  ),
                  // @ts-ignore
                  hr: ({...props}) => (
                    <hr className="my-4 border-gray-200 dark:border-gray-700" {...props} />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            {message.sources && message.sources.length > 0 && !message.isStreaming && (
              <ChatSources sources={message.sources} />
            )}
          </>
        ) : (
          <p>{message.content}</p>
        )}
        <p className="text-xs mt-1 opacity-70">
          {message.timestamp && message.timestamp instanceof Date && !isNaN(message.timestamp.getTime())
            ? message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};

export default ChatMessage;
