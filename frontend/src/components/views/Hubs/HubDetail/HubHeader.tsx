import React from 'react';
import { ArrowLeft } from 'lucide-react';

interface HubHeaderProps {
  hubId: number;
  onBack: () => void;
}

const HubHeader: React.FC<HubHeaderProps> = ({ hubId, onBack }) => {
  const getHubInfo = () => {
    const hubs = {
      1: {
        name: 'Customer Service Hub',
        description: 'Manage client relationships and support',
        image: 'https://images.unsplash.com/photo-1664575602276-acd073f104c1?q=80&w=2070&auto=format&fit=crop'
      },
      2: {
        name: 'HR Hub',
        description: 'Handle employee management and HR processes',
        image: 'https://images.unsplash.com/photo-1542744094-24638eff58bb?q=80&w=2070&auto=format&fit=crop'
      },
      3: {
        name: 'Project Management Hub',
        description: 'Oversee project planning and execution',
        image: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=2070&auto=format&fit=crop'
      },
      4: {
        name: 'QHSE Hub',
        description: 'Monitor quality, health, safety, and environmental compliance',
        image: 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?q=80&w=2070&auto=format&fit=crop'
      }
    };
    return hubs[hubId as keyof typeof hubs] || hubs[1];
  };

  const hub = getHubInfo();

  return (
    <div className="relative">
      <div className="h-48 relative">
        <img 
          src={hub.image}
          alt={hub.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/30" />
        <button
          onClick={onBack}
          className="absolute top-4 left-4 p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
      </div>
      
      <div className="max-w-7xl mx-auto px-6">
        <div className="bg-white -mt-24 relative rounded-lg shadow-lg p-6">
          <div className="space-y-2">
            <h1 className="text-2xl font-bold">{hub.name}</h1>
            <p className="text-gray-600">{hub.description}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HubHeader;