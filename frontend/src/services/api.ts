// API base URL - updated to GCP Cloud Run
const API_BASE_URL = 'https://knowledge-hub-backend-114820695484.us-central1.run.app';

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
    console.log(`Making API request to: ${API_BASE_URL}${endpoint}`);
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    const headers = {
      ...options.headers,
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
    
    // Log request details for debugging
    console.log('Request options:', {
      method: options.method || 'GET',
      headers,
      body: options.body ? (typeof options.body === 'string' ? options.body : 'FormData or other body type') : undefined
    });
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });
    
    console.log(`Response status: ${response.status}`);
    
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
    
    // Handle 404 Not Found specifically for our endpoints
    if (response.status === 404) {
      console.error(`Endpoint not found: ${endpoint}`);
      return {
        error: `The requested endpoint (${endpoint}) was not found on the server. This may indicate that the backend service needs to be updated.`,
        status: 404
      };
    }
    
    let data;
    try {
      data = await response.json();
      console.log('Response data:', data);
    } catch (jsonError) {
      console.error('Error parsing JSON response:', jsonError);
      return {
        error: 'Invalid response format from server',
        status: response.status
      };
    }
    
    return {
      data: response.ok ? data : undefined,
      error: !response.ok ? (data.error || 'An unknown error occurred') : undefined,
      status: response.status
    };
  } catch (error) {
    console.error('API call failed:', error);
    
    // Provide more detailed error message for network errors
    let errorMessage = 'Network error';
    if (error instanceof Error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('Network request failed')) {
        errorMessage = `Cannot connect to server at ${API_BASE_URL}. Please check your internet connection or contact support.`;
      } else {
        errorMessage = error.message;
      }
    }
    
    return {
      error: errorMessage,
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

// Chat History API functions

// Get chat history
export async function getChatHistory(): Promise<ApiResponse<{sessions: any[]}>> {
  return fetchApi<{sessions: any[]}>('/chat/history', {
    method: 'GET',
  });
}

// Get chat session
export async function getChatSession(sessionId: string): Promise<ApiResponse<any>> {
  return fetchApi<any>(`/chat/session/${sessionId}`, {
    method: 'GET',
  });
}

// Save chat session
export async function saveChatSession(data: {
  session_id?: string;
  title: string;
  messages: any[];
  category: string;
}): Promise<ApiResponse<{session_id: string}>> {
  return fetchApi<{session_id: string}>('/chat/save', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

// Member Management API functions

// Get all members for the current user's organization
export async function getMembers(): Promise<ApiResponse<{members: any[]}>> {
  return fetchApi<{members: any[]}>('/members', {
    method: 'GET',
  });
}

// Add a new member to the organization
export async function addMember(data: {
  name?: string;
  email: string;
  phone: string;
  position?: string;
  role?: string;
}): Promise<ApiResponse<{memberId: string, member: any}>> {
  return fetchApi<{memberId: string, member: any}>('/members', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

// Update a member's details
export async function updateMember(
  memberId: string,
  data: {
    name?: string;
    position?: string;
    role?: string;
    status?: string;
  }
): Promise<ApiResponse<{memberId: string}>> {
  return fetchApi<{memberId: string}>(`/members/${memberId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

// Delete a member
export async function deleteMember(memberId: string): Promise<ApiResponse<{memberId: string}>> {
  return fetchApi<{memberId: string}>(`/members/${memberId}`, {
    method: 'DELETE',
  });
}

// Send WhatsApp verification to a member
export async function sendWhatsAppVerification(memberId: string): Promise<ApiResponse<{memberId: string}>> {
  return fetchApi<{memberId: string}>('/members/send-verification', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ memberId }),
  });
}

// Send bulk WhatsApp message to members
export async function sendBulkWhatsAppMessage(data: {
  title: string;
  message: string;
  memberIds?: string[];
  sendEmail?: boolean;
  sendInApp?: boolean;
  scheduledFor?: string;
}): Promise<ApiResponse<{
  broadcastId: string;
  status: string;
  totalCount: number;
  successCount: number;
  failedCount: number;
  results: any[];
}>> {
  return fetchApi<{
    broadcastId: string;
    status: string;
    totalCount: number;
    successCount: number;
    failedCount: number;
    results: any[];
  }>('/whatsapp/send-bulk-message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}
