import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext';

interface HubContextType {
  hubName: string;
  hubId: string;
  isAdmin: boolean;
}

const HubContext = createContext<HubContextType | undefined>(undefined);

export const HubProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  
  // Use organization data as hub data
  const hubData = {
    hubName: user?.organizationName || 'Knowledge Hub',
    hubId: user?.organizationId || 'default',
    isAdmin: user?.organizationRole === 'admin' || false
  };
  
  return <HubContext.Provider value={hubData}>{children}</HubContext.Provider>;
};

export const useHub = () => {
  const context = useContext(HubContext);
  if (context === undefined) {
    throw new Error('useHub must be used within a HubProvider');
  }
  return context;
};
