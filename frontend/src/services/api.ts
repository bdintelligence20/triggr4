// Create a new file: src/services/api.ts

// API base URL - replace with your actual backend URL
const API_BASE_URL = 'https://triggr4bg.onrender.com';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Generic fetch function with error handling
async function fetchApi<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
      }
    });
    
    const data = await response.json();
    
    return {
      data: response.ok ? data : undefined,
      error: !response.ok ? (data.error || 'An unknown error occurred') : undefined,
      status: response.status
    };
  } catch (error) {
    console.error('API call failed:', error);
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 0
    };
  }
}

// Upload document
export async function uploadDocument(
  file: File, 
  category: string, 
  title?: string
): Promise<ApiResponse<{item_id: string, file_url: string}>> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  if (title) formData.append('title', title);
  
  return fetchApi<{item_id: string, file_url: string}>('/upload', {
    method: 'POST',
    body: formData,
  });
}

// Query the knowledge base
export async function queryKnowledge(
  query: string, 
  category?: string
): Promise<ApiResponse<{response: string, retrieved: any[]}>> {
  return fetchApi<{response: string, retrieved: any[]}>('/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, category }),
  });
}

// Fetch document categories
export async function fetchCategories(): Promise<ApiResponse<{categories: string[]}>> {
  return fetchApi<{categories: string[]}>('/categories', {
    method: 'GET',
  });
}

// Fetch documents
export async function fetchDocuments(
  category?: string
): Promise<ApiResponse<{documents: any[], count: number}>> {
  const queryParams = category ? `?category=${encodeURIComponent(category)}` : '';
  return fetchApi<{documents: any[], count: number}>(`/documents${queryParams}`, {
    method: 'GET',
  });
}

// Delete a document
export async function deleteDocument(itemId: string): Promise<ApiResponse<{message: string}>> {
  return fetchApi<{message: string}>(`/delete/${itemId}`, {
    method: 'DELETE',
  });
}

// Health check
export async function checkHealth(): Promise<ApiResponse<{status: string, services: any}>> {
  return fetchApi<{status: string, services: any}>('/health', {
    method: 'GET',
  });
}