import React from 'react';
import { motion } from 'framer-motion';
import { Building, Users, AlertTriangle } from 'lucide-react';
import { demoHubs } from '../../../data/demo-data';

const HubMemberships = () => {
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Hub Memberships</h2>
        <div className="space-y-4">
          {demoHubs.map((hub) => (
            <div key={hub.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-emerald-50 rounded-lg">
                    <Building className="text-emerald-400" size={20} />
                  </div>
                  <div>
                    <h3 className="font-medium">{hub.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{hub.description}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Users size={16} />
                        <span>{hub.members} members</span>
                      </div>
                      {hub.pendingIssues > 0 && (
                        <div className="flex items-center gap-1 text-sm text-amber-500">
                          <AlertTriangle size={16} />
                          <span>{hub.pendingIssues} pending</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <span className="px-2 py-1 bg-emerald-100 text-emerald-600 rounded-full text-xs">
                  Member
                </span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default HubMemberships;