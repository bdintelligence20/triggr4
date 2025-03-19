import React from 'react';
import { motion } from 'framer-motion';
import OpenTicketsOverview from '../Dashboard/OpenTicketsOverview';
import TrendingIssues from '../Dashboard/TrendingIssues';
import NotificationsPanel from '../Dashboard/NotificationsPanel';

interface HubContentProps {
  hubId: number;
  hub: {
    description?: string;
    relevantDates?: { label: string; date: string }[];
    links?: { label: string; url: string }[];
    customFields?: { label: string; value: string }[];
  };
}

const HubContent: React.FC<HubContentProps> = ({ hubId }) => {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <OpenTicketsOverview />
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <TrendingIssues />
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <NotificationsPanel />
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default HubContent;