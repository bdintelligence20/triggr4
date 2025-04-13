// components/integration/IntegrationPanel.tsx
import React from 'react';
import WhatsAppIntegration from './WhatsappIntegration';
import ApiAccess from './ApiAccess';
import McpIntegration from './McpIntegration';

const IntegrationPanel: React.FC = () => {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 transition-colors duration-300">
      <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">Integration Options</h2>
      
      <div className="grid grid-cols-1 gap-6">
        <WhatsAppIntegration />
        <ApiAccess />
        <McpIntegration />
      </div>
    </div>
  );
};

export default IntegrationPanel;
