// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider } from './contexts/AuthContext';
import Dashboard from './components/layout/Dashboard';
import LoginLayout from './components/auth/LoginLayout';
import ForgotPassword from './components/auth/ForgotPassword';
import OTPVerification from './components/auth/OTPVerification';
import ResetPassword from './components/auth/ResetPassword';
import OnboardingFlow from './components/auth/OnboardingFlow';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LibraryPanel from './components/library/LibraryPanel';
import ChatPanel from './components/chat/ChatPanel';
import IntegrationPanel from './components/integration/IntegrationPanel';
import './index.css';

// Main app wrapper that provides context
const App: React.FC = () => {
  return (
    <Router>
      <AppProvider>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginLayout />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/verify" element={<OTPVerification />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />
            <Route path="/onboarding" element={<OnboardingFlow />} />
            
            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<Dashboard />}>
                <Route index element={<LibraryPanel />} />
                <Route path="library" element={<LibraryPanel />} />
                <Route path="chat" element={<ChatPanel />} />
                <Route path="integration" element={<IntegrationPanel />} />
              </Route>
            </Route>
            
            {/* Redirect root to login or dashboard based on auth status */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </AppProvider>
    </Router>
  );
};

export default App;
