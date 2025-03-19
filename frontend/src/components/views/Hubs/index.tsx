import React, { useState } from 'react';
import { Plus, Share2 } from 'lucide-react';
import HubsHeader from './HubsHeader';
import HubFilters from './HubFilters';
import CompactHubCard from './CompactHubCard';
import HubDetails from '../HubDetails';
import NewHubModal from './NewHubModal';
import ShareModal from './ShareModal';
import { demoHubs } from '../../data/demo-data';

const Hubs = () => {
  const [selectedHubId, setSelectedHubId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [isNewHubModalOpen, setIsNewHubModalOpen] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  const filteredHubs = demoHubs
    .filter(hub => {
      const matchesSearch = hub.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        hub.description.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesFilter = filterStatus === 'all' ||
        (filterStatus === 'pending' && hub.pendingIssues > 0) ||
        (filterStatus === 'none' && hub.pendingIssues === 0);

      return matchesSearch && matchesFilter;
    });

  if (selectedHubId) {
    return (
      <HubDetails 
        hubId={selectedHubId} 
        onBack={() => setSelectedHubId(null)} 
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-8">
        <div className="max-w-[1920px] mx-auto space-y-8">
          {/* Section Header */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Hubs</h2>
            <p className="text-gray-500 mt-2">Access and manage your specialized business function hubs</p>
          </div>

          <div className="flex justify-end gap-4">
            <button
              onClick={() => setIsShareModalOpen(true)}
              className="flex items-center gap-2 px-6 py-2.5 bg-[#25D366] text-white rounded-lg hover:bg-[#1da851] transition-colors"
            >
              <Share2 size={20} />
              Share WhatsApp
            </button>
            <button
              onClick={() => setIsNewHubModalOpen(true)}
              className="flex items-center gap-2 px-6 py-2.5 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 transition-colors"
            >
              <Plus size={20} />
              New Hub
            </button>
          </div>

          <HubFilters
            onSearch={setSearchQuery}
            onFilter={setFilterStatus}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {filteredHubs.map((hub) => (
              <CompactHubCard 
                key={hub.id} 
                {...hub} 
                onClick={setSelectedHubId}
              />
            ))}
          </div>
        </div>
      </div>

      <NewHubModal 
        isOpen={isNewHubModalOpen}
        onClose={() => setIsNewHubModalOpen(false)}
      />

      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
      />
    </div>
  );
};

export default Hubs;