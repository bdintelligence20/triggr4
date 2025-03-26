import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth, APP_EVENTS } from './AuthContext';

interface HubContextType {
  hubName: string;
  hubId: string;
  isAdmin: boolean;
  organizationId: string | undefined;
}

const HubContext = createContext<HubContextType | undefined>(undefined);

export const HubProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [hubData, setHubData] = useState<HubContextType>({
    hubName: 'Knowledge Hub',
    hubId: 'default',
    isAdmin: false,
    organizationId: undefined
  });
  
  // Update hub data when user or organization changes
  useEffect(() => {
    if (user) {
      setHubData({
        hubName: user.organizationName || 'Knowledge Hub',
        hubId: user.organizationId || 'default',
        isAdmin: user.organizationRole === 'admin',
        organizationId: user.organizationId
      });
      
      console.log(`Hub context updated for organization: ${user.organizationId}`);
    } else {
      // Reset to defaults when user logs out
      setHubData({
        hubName: 'Knowledge Hub',
        hubId: 'default',
        isAdmin: false,
        organizationId: undefined
      });
    }
  }, [user]);
  
  // Listen for logout events to reset state
  useEffect(() => {
    const handleLogout = () => {
      // Reset hub data to defaults
      setHubData({
        hubName: 'Knowledge Hub',
        hubId: 'default',
        isAdmin: false,
        organizationId: undefined
      });
      console.log('Hub state reset due to logout event');
    };
    
    // Add event listener
    window.addEventListener(APP_EVENTS.LOGOUT, handleLogout);
    
    // Clean up
    return () => {
      window.removeEventListener(APP_EVENTS.LOGOUT, handleLogout);
    };
  }, []);
  
  return <HubContext.Provider value={hubData}>{children}</HubContext.Provider>;
};

export const useHub = () => {
  const context = useContext(HubContext);
  if (context === undefined) {
    throw new Error('useHub must be used within a HubProvider');
  }
  return context;
};
