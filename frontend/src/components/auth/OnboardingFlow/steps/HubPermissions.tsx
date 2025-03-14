import React, { useState } from 'react';
import { Button } from '../../../ui/Button';
import { Check, Info } from 'lucide-react';

interface HubCategory {
  id: string;
  name: string;
  description: string;
}

const defaultHubs: HubCategory[] = [
  {
    id: 'general',
    name: 'General Knowledge',
    description: 'Company-wide information and resources'
  },
  {
    id: 'hr',
    name: 'HR Policies',
    description: 'Human resources documentation and guidelines'
  },
  {
    id: 'sales',
    name: 'Sales Materials',
    description: 'Sales decks, pricing, and customer information'
  },
  {
    id: 'marketing',
    name: 'Marketing',
    description: 'Brand assets, campaigns, and marketing materials'
  },
  {
    id: 'technical',
    name: 'Technical Documentation',
    description: 'Product specifications and technical guides'
  },
  {
    id: 'finance',
    name: 'Finance',
    description: 'Financial reports and accounting information'
  }
];

interface HubPermissionsProps {
  onComplete: () => void;
}

const HubPermissions: React.FC<HubPermissionsProps> = ({ onComplete }) => {
  const [selectedHubs, setSelectedHubs] = useState<string[]>(['general']);

  const toggleHub = (hubId: string) => {
    if (selectedHubs.includes(hubId)) {
      // Don't allow deselecting 'general'
      if (hubId === 'general') return;
      setSelectedHubs(selectedHubs.filter(id => id !== hubId));
    } else {
      setSelectedHubs([...selectedHubs, hubId]);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Knowledge Hub Access</h1>
        <p className="text-gray-600">
          Select which knowledge hubs you need access to
        </p>
      </div>

      <div className="space-y-6">
        <div className="bg-blue-50 p-4 rounded-lg flex items-start gap-3">
          <Info size={20} className="text-blue-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-blue-700">
            Your administrator will review your access requests. Some hubs may require additional approval.
          </p>
        </div>

        <div className="space-y-3">
          {defaultHubs.map(hub => (
            <div 
              key={hub.id}
              onClick={() => toggleHub(hub.id)}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedHubs.includes(hub.id) 
                  ? 'border-emerald-400 bg-emerald-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{hub.name}</h3>
                  <p className="text-sm text-gray-500">{hub.description}</p>
                </div>
                <div className={`w-5 h-5 rounded-full flex items-center justify-center ${
                  selectedHubs.includes(hub.id) 
                    ? 'bg-emerald-400 text-white' 
                    : 'border border-gray-300'
                }`}>
                  {selectedHubs.includes(hub.id) && <Check size={12} />}
                </div>
              </div>
            </div>
          ))}
        </div>

        <Button
          onClick={onComplete}
          className="w-full"
        >
          Continue
        </Button>
      </div>
    </div>
  );
};

export default HubPermissions;
