import React from 'react';
import { motion } from 'framer-motion';
import WelcomeBanner from './WelcomeBanner';
import ActivitySummary from './ActivitySummary';
import AnalyticsGrid from './AnalyticsGrid';
import OpenTicketsOverview from './OpenTicketsOverview';
import TrendingIssues from './TrendingIssues';
import NotificationsPanel from './NotificationsPanel';

const Dashboard = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gray-50"
    >
      <WelcomeBanner />
      <div className="max-w-[1920px] mx-auto px-6 py-6 space-y-6">
        <ActivitySummary />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <OpenTicketsOverview />
            <AnalyticsGrid />
          </div>
          
          {/* Right Column */}
          <div className="space-y-6">
            <TrendingIssues />
            <NotificationsPanel />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;