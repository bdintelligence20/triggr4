import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertTriangle, Book, Plug, Users, Share2 } from 'lucide-react';

interface HubHeaderProps {
  hubId: number;
  onBack: () => void;
  activeTab: 'issues' | 'library' | 'integrations' | 'members';
  onTabChange: (tab: 'issues' | 'library' | 'integrations' | 'members') => void;
  isAdmin: boolean;
  onShare?: () => void;
}

const HubHeader: React.FC<HubHeaderProps> = ({
  hubId,
  onBack,
  activeTab,
  onTabChange,
  isAdmin,
  onShare
}) => {
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
          className="absolute top-4 left-8 px-3 py-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft size={18} />
        </button>
        {onShare && (
          <button
            onClick={onShare}
            className="absolute top-4 right-4 flex items-center gap-2 px-4 py-2 bg-[#25D366] text-white rounded-lg hover:bg-[#1da851] transition-colors"
          >
            <Share2 size={18} />
            <span>Share WhatsApp</span>
          </button>
        )}
      </div>
      
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white -mt-24 relative rounded-lg shadow-lg p-6"
        >
          <div className="space-y-4">
            <div>
              <h1 className="text-2xl font-bold">{hub.name}</h1>
              <p className="text-gray-600 mt-2">{hub.description}</p>
            </div>

            <div className="flex items-center gap-4 pt-4 border-t">
              <button
                onClick={() => onTabChange('issues')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'issues'
                    ? 'bg-emerald-50 text-emerald-600'
                    : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                <AlertTriangle size={20} />
                Issues
              </button>

              <button
                onClick={() => onTabChange('library')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'library'
                    ? 'bg-emerald-50 text-emerald-600'
                    : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                <Book size={20} />
                Library
              </button>

              {isAdmin && (
                <button
                  onClick={() => onTabChange('integrations')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'integrations'
                      ? 'bg-emerald-50 text-emerald-600'
                      : 'text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  <Plug size={20} />
                  Integrations
                </button>
              )}

              {isAdmin && (
                <button
                  onClick={() => onTabChange('members')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'members'
                      ? 'bg-emerald-50 text-emerald-600'
                      : 'text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  <Users size={20} />
                  Members
                </button>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default HubHeader;