import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertTriangle, Book, Users, Share2, Upload } from 'lucide-react';
import { useHub } from '../../../contexts/HubContext';
import { useAuth } from '../../../contexts/AuthContext';

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
  const { hubName } = useHub();
  const { user } = useAuth();
  const [customBgImage, setCustomBgImage] = useState<string | null>(null);
  const [showImageUpload, setShowImageUpload] = useState(false);
  
  const getHubInfo = () => {
    const defaultImages = {
      1: 'https://images.unsplash.com/photo-1664575602276-acd073f104c1?q=80&w=2070&auto=format&fit=crop',
      2: 'https://images.unsplash.com/photo-1542744094-24638eff58bb?q=80&w=2070&auto=format&fit=crop',
      3: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=2070&auto=format&fit=crop',
      4: 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?q=80&w=2070&auto=format&fit=crop'
    };
    
    return {
      name: `The ${user?.organizationName || 'Organization'} Hub`,
      description: 'Your centralized knowledge repository',
      image: customBgImage || defaultImages[hubId as keyof typeof defaultImages] || defaultImages[1]
    };
  };

  const hub = getHubInfo();
  
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setCustomBgImage(event.target.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
    setShowImageUpload(false);
  };

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
        <div className="absolute top-4 right-4 flex items-center gap-2">
          {isAdmin && (
            <button
              onClick={() => setShowImageUpload(!showImageUpload)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Upload size={18} />
              <span>Change Background</span>
            </button>
          )}
          {onShare && (
            <button
              onClick={onShare}
              className="flex items-center gap-2 px-4 py-2 bg-[#25D366] text-white rounded-lg hover:bg-[#1da851] transition-colors"
            >
              <Share2 size={18} />
              <span>Share WhatsApp</span>
            </button>
          )}
        </div>
        
        {showImageUpload && (
          <div className="absolute top-16 right-4 bg-white p-4 rounded-lg shadow-lg">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="text-sm"
            />
          </div>
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

              {/* Integrations tab hidden as requested */}

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
