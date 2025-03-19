import React from 'react';
import { motion } from 'framer-motion';
import WelcomeBanner from './WelcomeBanner';
import ActivitySummary from './ActivitySummary';
import TrendingIssues from './TrendingIssues';
import NotificationsPanel from './NotificationsPanel';
import AnalyticsGrid from './AnalyticsGrid';

const Dashboard = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gray-50"
    >
      <WelcomeBanner />
      <div className="max-w-[1920px] mx-auto px-6 py-6 space-y-6 pb-12">
        <ActivitySummary />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <TrendingIssues />
            <AnalyticsGrid />
          </div>
          
          {/* Right Column */}
          <div className="space-y-6">
            <NotificationsPanel />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;