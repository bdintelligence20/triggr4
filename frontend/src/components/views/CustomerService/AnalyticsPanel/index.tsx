import React from 'react';
import { Clock, CheckCircle } from 'lucide-react';
import PerformanceMetrics from './PerformanceMetrics';
import TrendingIssues from './TrendingIssues';

const AnalyticsPanel = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Analytics & Insights</h2>
      </div>
      
      <div className="p-4 space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-emerald-50 rounded-lg">
            <div className="flex items-center gap-2 text-emerald-600">
              <Clock size={20} />
              <span className="text-sm font-medium">Avg. Response Time</span>
            </div>
            <div className="mt-2 text-2xl font-bold text-emerald-600">2.5h</div>
          </div>
          
          <div className="p-4 bg-emerald-50 rounded-lg">
            <div className="flex items-center gap-2 text-emerald-600">
              <CheckCircle size={20} />
              <span className="text-sm font-medium">Resolution Rate</span>
            </div>
            <div className="mt-2 text-2xl font-bold text-emerald-600">94%</div>
          </div>
        </div>
        
        <PerformanceMetrics />
        <TrendingIssues />
      </div>
    </div>
  );
};

export default AnalyticsPanel;