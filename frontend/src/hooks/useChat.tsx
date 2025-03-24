// hooks/useChat.tsx
import { useRef, useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { API_URL, QueryResponse, ChatMessage } from '../types';

// Approximate token counting function for client-side estimation
// This is a simplified version and won't be as accurate as the server-side tiktoken
const estimateTokenCount = (text: string): number => {
  if (!text) return 0;
  
  // GPT models use roughly 4 characters per token on average
  // This is a very rough estimate
  return Math.ceil(text.length / 4);
};

// Maximum tokens to include in conversation history
const MAX_HISTORY_TOKENS = 6000;

export const useChat = () => {
  const chatContainerRef = useRef<HTMLDivElement>(null);
  
  const { 
    chatCategory,
    categories,
    newMessage,
    setNewMessage,
    chatMessages,
    setChatMessages,
    activeEventSource,
    setActiveEventSource
  } = useAppContext();
  
  // Build conversation history from the current chat messages with token management
  const buildConversationHistory = () => {
    // Start with the most recent messages and work backwards
    const reversedMessages = [...chatMessages].reverse();
    const historyParts: string[] = [];
    let tokenCount = 0;
    
    for (const msg of reversedMessages) {
      const prefix = msg.sender === 'user' ? "User:" : "AI:";
      const formattedMsg = `${prefix} ${msg.content}`;
      const msgTokens = estimateTokenCount(formattedMsg);
      
      // If adding this message would exceed our token budget, stop
      if (tokenCount + msgTokens > MAX_HISTORY_TOKENS) {
        break;
      }
      
      // Add message to history and update token count
      historyParts.unshift(formattedMsg);
      tokenCount += msgTokens;
    }
    
    return historyParts.join("\n");
  };
  
  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    
    // Close any existing EventSource
    if (activeEventSource) {
      activeEventSource.close();
      setActiveEventSource(null);
    }
    
    // Add the user message
    const userMessageId = Date.now();
    const userMessage: ChatMessage = {
      id: userMessageId,
      content: newMessage,
      sender: 'user' as const,
      timestamp: new Date(),
      category: chatCategory
    };
    
    setChatMessages((prevMessages: ChatMessage[]) => [...prevMessages, userMessage]);
    setNewMessage('');
    
    // Add an initial AI acknowledgment
    const acknowledgeId = userMessageId + 1;
    const acknowledgmentMessage: ChatMessage = {
      id: acknowledgeId,
      content: "⏳ I'm searching through our knowledge base...",
      sender: 'ai' as const,
      timestamp: new Date(),
      category: chatCategory,
      isStreaming: true
    };
    
    setChatMessages((prevMessages: ChatMessage[]) => [...prevMessages, acknowledgmentMessage]);
    
    try {
      // Determine category name for the API call
      const categoryName = categories.find(c => c.id === chatCategory)?.name || '';
      
      // Build conversation history
      const conversationHistory = buildConversationHistory();
      
      // Send the POST request including conversation history in the payload
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: newMessage,
          stream: true,
          history: conversationHistory
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to get response: ${response.status}`);
      }
      
      const result: QueryResponse = await response.json();
      if (result.error) {
        throw new Error(result.error);
      }
      
      // Replace the acknowledgment with the actual AI response
      setChatMessages((prevMessages: ChatMessage[]) => 
        prevMessages.map((msg: ChatMessage) =>
          msg.id === acknowledgeId
            ? {
                ...msg,
                content: result.response || "I couldn't find an answer to your question.",
                sources: result.sources,
                isStreaming: false
              }
            : msg
        )
      );
      
      // Optionally add a completion message
      if (result.response) {
        setTimeout(() => {
          const completionMessageId = Date.now();
          const completionMessage: ChatMessage = {
            id: completionMessageId,
            content: "✅ That completes my answer. Let me know if you need any clarification!",
            sender: 'ai' as const,
            timestamp: new Date(),
            category: chatCategory,
            isStreaming: false
          };
          // Add the completion message
          setChatMessages((prevMessages: ChatMessage[]) => [...prevMessages, completionMessage]);
        }, 1000);
      }
      
    } catch (err) {
      console.error('Error getting AI response:', err);
      setChatMessages((prevMessages: ChatMessage[]) =>
        prevMessages.map((msg: ChatMessage) =>
          msg.id === acknowledgeId
            ? {
                ...msg,
                content: "Sorry, I encountered an error while processing your request. Please try again later.",
                isStreaming: false
              }
            : msg
        )
      );
    }
  };
  
  // Scroll to bottom of chat when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);
  
  return {
    chatContainerRef,
    handleSendMessage
  };
};
