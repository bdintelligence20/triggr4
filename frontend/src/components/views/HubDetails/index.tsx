import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import HubHeader from './HubHeader';
import HubLibrary from './sections/HubLibrary';
import HubIntegrations from './sections/HubIntegrations';
import HubIssues from './sections/HubIssues';
import HubMembers from './sections/HubMembers';
import ShareModal from '../Hubs/ShareModal';
import { useHub } from '../../../contexts/HubContext';
import { useAuth } from '../../../contexts/AuthContext';

interface HubDetailsProps {
  hubId?: number;
  onBack?: () => void;
}

const HubDetails: React.FC<HubDetailsProps> = ({ hubId = 1, onBack }) => {
  const navigate = useNavigate();
  const { hubName, isAdmin } = useHub();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'issues' | 'library' | 'integrations' | 'members'>('library');
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  
  // Create a hub object from the HubContext
  const hub = {
    id: hubId,
    name: hubName || user?.organizationName || 'Knowledge Hub',
    description: 'Your centralized knowledge repository',
    members: 1,
    pendingIssues: 0
  };
  
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate('/dashboard');
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'library':
        return <HubLibrary hubId={hubId} />;
      case 'integrations':
        return isAdmin ? <HubIntegrations hubId={hubId} /> : null;
      case 'members':
        return isAdmin ? <HubMembers hubId={hubId} /> : null;
      case 'issues':
      default:
        return <HubIssues hubId={hubId} />;
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)]">
      <HubHeader 
        hubId={hubId}
        onBack={handleBack}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isAdmin={isAdmin}
        onShare={() => setIsShareModalOpen(true)}
      />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {renderContent()}
      </div>

      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
      />
    </div>
  );
};

export default HubDetails;
