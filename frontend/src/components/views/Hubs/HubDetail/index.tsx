import React, { useState } from 'react';
import HubHeader from './HubHeader';
import CommunicationHub from '../../CustomerService/CommunicationHub';
import AnalyticsPanel from '../../CustomerService/AnalyticsPanel';
import HRPanel from './panels/HRPanel';
import ProjectPanel from './panels/ProjectPanel';
import QHSEPanel from './panels/QHSEPanel';
import ClientsSuppliers from '../../CustomerService/ClientsSuppliers';

interface HubDetailProps {
  hubId: number;
  onBack: () => void;
}

const HubDetail: React.FC<HubDetailProps> = ({ hubId, onBack }) => {
  const [activeView, setActiveView] = useState<'main' | 'secondary'>('main');
  const [secondaryView, setSecondaryView] = useState<'clients' | 'suppliers' | null>(null);

  const getHubType = () => {
    // In a real app, this would come from your data store
    const types = {
      1: 'customer-service',
      2: 'hr',
      3: 'project',
      4: 'qhse'
    };
    return types[hubId as keyof typeof types] || 'customer-service';
  };

  const renderHubContent = () => {
    const type = getHubType();

    if (activeView === 'secondary' && type === 'customer-service') {
      return (
        <ClientsSuppliers 
          type={secondaryView === 'clients' ? 'clients' : 'suppliers'} 
          onBack={() => setActiveView('main')}
        />
      );
    }

    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <CommunicationHub />
          {type === 'customer-service' && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="grid grid-cols-2 gap-6">
                <button
                  onClick={() => {
                    setSecondaryView('clients');
                    setActiveView('secondary');
                  }}
                  className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group"
                >
                  <h3 className="text-lg font-semibold group-hover:text-emerald-400">Clients</h3>
                  <p className="text-gray-500 mt-2">Manage your client relationships and communications</p>
                </button>
                <button
                  onClick={() => {
                    setSecondaryView('suppliers');
                    setActiveView('secondary');
                  }}
                  className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group"
                >
                  <h3 className="text-lg font-semibold group-hover:text-emerald-400">Suppliers</h3>
                  <p className="text-gray-500 mt-2">Manage your supplier relationships and orders</p>
                </button>
              </div>
            </div>
          )}
          {type === 'hr' && <HRPanel />}
          {type === 'project' && <ProjectPanel />}
          {type === 'qhse' && <QHSEPanel />}
        </div>
        <div>
          <AnalyticsPanel />
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-[calc(100vh-64px)]">
      <HubHeader 
        hubId={hubId}
        onBack={onBack}
      />
      <div className="max-w-7xl mx-auto px-6 py-6">
        {renderHubContent()}
      </div>
    </div>
  );
};

export default HubDetail;