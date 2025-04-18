// types/index.ts

export interface KnowledgeItem {
    id: string;
    title: string;
    content?: string;
    category: string;
    file_type?: string;
    type?: 'text' | 'pdf' | 'doc' | 'csv'; // For UI display
    createdAt: Date;
    processing_status?: string;
    vectors_stored?: number;
    word_count?: number;
    fileSize?: string;
    fileUrl?: string;
  }
  
  export interface Category {
    id: string;
    name: string;
    whatsappNumber?: string;
  }
  
  export interface Source {
    id: string;
    relevance_score: number;
    document?: {
      title: string;
      file_type: string;
      file_url: string | null;
    }
  }
  
  export interface ChatMessage {
    id: string | number;
    content: string;
    sender: 'user' | 'ai';
    timestamp: Date;
    category?: string;
    isStreaming?: boolean; // Property to track streaming status
    sources?: Array<Source>; // Property for sources with enhanced metadata
  }
  
  // API responses
  export interface UploadResponse {
    item_id: string;
    file_url?: string;
    error?: string;
  }
  
  export interface QueryResponse {
    response?: string;
    sources?: Array<Source>;
    error?: string;
  }
  
// API URL - Could also be in an environment variable
export const API_URL = 'https://triggr4bg.onrender.com';
