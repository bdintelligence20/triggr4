import React, { useState } from 'react';
import { motion } from 'framer-motion';
import OpenTicketsOverview from '../../Dashboard/OpenTicketsOverview';
import TrendingIssues from '../../Dashboard/TrendingIssues';

interface HubIssuesProps {
  hubId: number;
}

const HubIssues: React.FC<HubIssuesProps> = ({ hubId }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
    </div>
  );
};

export default HubIssues;