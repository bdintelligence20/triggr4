// src/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Categories API
export const categoriesAPI = {
  getAll: async () => {
    const response = await api.get('/categories');
    return response.data;
  },
  
  getOne: async (id) => {
    const response = await api.get(`/categories/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/categories', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/categories/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/categories/${id}`);
    return response.data;
  },
  
  generateWhatsappNumber: async (id) => {
    const response = await api.post(`/categories/${id}/whatsapp`);
    return response.data;
  },
  
  addContact: async (categoryId, data) => {
    const response = await api.post(`/categories/${categoryId}/contacts`, data);
    return response.data;
  },
  
  deleteContact: async (categoryId, contactId) => {
    const response = await api.delete(`/categories/${categoryId}/contacts/${contactId}`);
    return response.data;
  }
};

// Knowledge API
export const knowledgeAPI = {
  getAll: async (categoryId = null, search = null) => {
    const params = {};
    if (categoryId) params.categoryId = categoryId;
    if (search) params.search = search;
    
    const response = await api.get('/knowledge', { params });
    return response.data;
  },
  
  getOne: async (id) => {
    const response = await api.get(`/knowledge/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/knowledge', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/knowledge/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/knowledge/${id}`);
    return response.data;
  },
  
  uploadFile: async (file, categoryId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', categoryId);
    
    const response = await axios.post(`${API_BASE_URL}/knowledge/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  }
};

// Chat API
export const chatAPI = {
  getMessages: async (categoryId) => {
    const response = await api.get(`/chat/${categoryId}`);
    return response.data;
  },
  
  sendMessage: async (categoryId, message) => {
    const response = await api.post(`/chat/${categoryId}`, { message });
    return response.data;
  },
  
  deleteMessage: async (categoryId, messageId) => {
    const response = await api.delete(`/chat/${categoryId}/messages/${messageId}`);
    return response.data;
  },
  
  sendBroadcast: async (categoryId, message) => {
    const response = await api.post('/chat/broadcast', { categoryId, message });
    return response.data;
  }
};

// Add interceptors for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.data);
      
      // You could dispatch to a global error handler here
      // Or return specific error messages for different status codes
      
      if (error.response.status === 401) {
        // Handle unauthorized/authentication errors
        console.error('Authentication error');
      } else if (error.response.status === 403) {
        // Handle forbidden/authorization errors
        console.error('Authorization error');
      } else if (error.response.status === 404) {
        // Handle not found errors
        console.error('Resource not found');
      } else if (error.response.status >= 500) {
        // Handle server errors
        console.error('Server error');
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response from server:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;