import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import useRoleStore from '../store/roleStore';
import { API_URL } from '../types';

interface User {
  id: string;
  email: string;
  fullName: string;
  photoUrl?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  verifyOTP: (otp: string) => Promise<boolean>;
  forgotPassword: (email: string) => Promise<boolean>;
  resetPassword: (token: string, password: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { role, setRole } = useRoleStore();
  const navigate = useNavigate();

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        setIsLoading(true);
        // For now, we'll just check if there's a token in localStorage
        const token = localStorage.getItem('auth_token');
        
        if (token) {
          // In a real app, you would validate the token with your backend
          // For now, we'll simulate a successful auth check
          setUser({
            id: '1',
            email: 'user@example.com',
            fullName: 'Test User',
            role: role
          });
          setRole(role || 'user');
        }
      } catch (err) {
        console.error('Auth check failed:', err);
        setError('Authentication check failed');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, [setRole, role]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      // In a real app, you would make an API call to your backend
      // For now, we'll simulate a successful login
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store token in localStorage
      localStorage.setItem('auth_token', 'dummy_token');
      localStorage.setItem('auth_email', email);
      
      return true;
    } catch (err) {
      console.error('Login failed:', err);
      setError('Login failed. Please check your credentials.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOTP = async (otp: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      // In a real app, you would verify the OTP with your backend
      // For now, we'll simulate a successful verification
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Set user data
      const email = localStorage.getItem('auth_email') || 'user@example.com';
      setUser({
        id: '1',
        email,
        fullName: 'Test User',
        role: 'user'
      });
      
      setRole('user');
      
      return true;
    } catch (err) {
      console.error('OTP verification failed:', err);
      setError('OTP verification failed. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_email');
    setUser(null);
    setRole('guest');
    navigate('/login');
  };

  const forgotPassword = async (email: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      // In a real app, you would make an API call to your backend
      // For now, we'll simulate a successful request
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return true;
    } catch (err) {
      console.error('Forgot password request failed:', err);
      setError('Failed to send password reset email. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const resetPassword = async (token: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      // In a real app, you would make an API call to your backend
      // For now, we'll simulate a successful password reset
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return true;
    } catch (err) {
      console.error('Password reset failed:', err);
      setError('Failed to reset password. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    logout,
    verifyOTP,
    forgotPassword,
    resetPassword
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
