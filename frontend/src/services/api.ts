// API base URL - replace with your actual backend URL
const API_BASE_URL = 'https://triggr4bg.onrender.com';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Generic fetch function with error handling and authentication
async function fetchApi<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    const headers = {
      ...options.headers,
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });
    
    // Handle 401 Unauthorized by redirecting to login
    if (response.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_email');
      window.location.href = '/login';
      return {
        error: 'Authentication required. Please log in again.',
        status: 401
      };
    }
    
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

// Authentication API functions

// Register
export async function register(email: string, password: string, fullName?: string): Promise<ApiResponse<{token: string, user: any}>> {
  return fetchApi<{token: string, user: any}>('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, fullName }),
  });
}

// Login
export async function login(email: string, password: string): Promise<ApiResponse<{token: string, user: any}>> {
  return fetchApi<{token: string, user: any}>('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
}

// Forgot password
export async function forgotPassword(email: string): Promise<ApiResponse<{message: string}>> {
  return fetchApi<{message: string}>('/auth/forgot-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  });
}

// Reset password
export async function resetPassword(token: string, password: string): Promise<ApiResponse<{message: string}>> {
  return fetchApi<{message: string}>('/auth/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token, password }),
  });
}

// Logout
export async function logout(): Promise<ApiResponse<{message: string}>> {
  return fetchApi<{message: string}>('/auth/logout', {
    method: 'POST',
  });
}

// Create organization
export async function createOrganization(
  organizationName: string,
  industry: string,
  organizationSize: string
): Promise<ApiResponse<{organizationId: string, organizationName: string}>> {
  return fetchApi<{organizationId: string, organizationName: string}>('/auth/create-organization', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ organizationName, industry, organizationSize }),
  });
}

// Validate token
export async function validateToken(): Promise<ApiResponse<any>> {
  return fetchApi<any>('/auth/validate-token', {
    method: 'POST',
  });
}
