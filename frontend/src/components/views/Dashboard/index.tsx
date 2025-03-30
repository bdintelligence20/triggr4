import React from 'react';
import { motion } from 'framer-motion';
import WelcomeBanner from './WelcomeBanner';
import AnalyticsGrid from './AnalyticsGrid';
import CommonProblems from './CommonProblems';
import SentimentAnalysis from './SentimentAnalysis';
import DocumentUsage from './DocumentUsage';
import CommonQuestions from './CommonQuestions';
import ResponseTimeAnalytics from './ResponseTimeAnalytics';

const Dashboard = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gray-50"
    >
      <WelcomeBanner />
      <div className="max-w-[1920px] mx-auto px-6 py-6 space-y-6 pb-12">
        {/* New Analytics Section - First Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CommonProblems />
          <SentimentAnalysis />
        </div>
        
        {/* New Analytics Section - Second Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DocumentUsage />
          <CommonQuestions />
        </div>
        
        {/* Response Time Analytics - Full Width */}
        <ResponseTimeAnalytics />
        
        {/* Original Dashboard Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <AnalyticsGrid />
          </div>
          
          {/* Right Column */}
          <div className="space-y-6">
            {/* Additional content can be added here if needed */}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
