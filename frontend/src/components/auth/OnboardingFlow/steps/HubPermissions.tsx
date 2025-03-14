import React from 'react';
import { motion } from 'framer-motion';
import { Shield, ArrowRight } from 'lucide-react';
import { demoHubs } from '../../../data/demo-data';

interface HubPermissionsProps {
  onComplete: () => void;
}

const HubPermissions: React.FC<HubPermissionsProps> = ({ onComplete }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Your Hub Access</h1>
        <p className="text-gray-600">
          You have been granted access to the following hubs
        </p>
      </div>

      <div className="space-y-4 mb-8">
        {demoHubs.slice(0, 2).map((hub, index) => (
          <motion.div
            key={hub.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 border rounded-lg"
          >
            <div className="flex items-start gap-4">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Shield className="text-emerald-400" size={24} />
              </div>
              <div>
                <h3 className="font-medium">{hub.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{hub.description}</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="px-2 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs">
                    View Content
                  </span>
                  <span className="px-2 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs">
                    Create Reports
                  </span>
                  <span className="px-2 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs">
                    Submit Requests
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <button
        onClick={onComplete}
        className="w-full py-2 px-4 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 flex items-center justify-center gap-2"
      >
        Continue
        <ArrowRight size={18} />
      </button>
    </div>
  );
};

export default HubPermissions;