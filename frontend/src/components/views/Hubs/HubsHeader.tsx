import React from 'react';
import { Plus } from 'lucide-react';

interface HubsHeaderProps {
  onNewHub: () => void;
}

const HubsHeader: React.FC<HubsHeaderProps> = ({ onNewHub }) => (
  <div className="flex items-center justify-between w-full">
    <div>
      <h2 className="text-2xl font-semibold text-gray-900">Hubs</h2>
      <p className="text-gray-500 mt-2">Access your specialized hubs for different business functions</p>
    </div>
    <div className="flex items-center gap-4">
      <button
        onClick={onNewHub}
        className="flex items-center gap-2 px-6 py-2.5 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 transition-colors"
      >
        <Plus size={20} />
        New Hub
      </button>
    </div>
  </div>
);

export default HubsHeader;