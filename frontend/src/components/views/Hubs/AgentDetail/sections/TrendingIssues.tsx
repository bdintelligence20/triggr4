import React from 'react';
import { TrendingUp } from 'lucide-react';

const demoIssues = [
  {
    id: 1,
    issue: 'Delivery Delays',
    reports: 24,
    trend: -8
  },
  {
    id: 2,
    issue: 'Product Quality',
    reports: 18,
    trend: 15
  },
  {
    id: 3,
    issue: 'Billing Questions',
    reports: 12,
    trend: 5
  }
];

const TrendingIssues = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm h-full">
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <TrendingUp size={18} className="text-emerald-400" />
          <h2 className="text-base font-semibold text-gray-900">Trending Issues</h2>
        </div>
      </div>

      <div className="p-5 space-y-3">
        {demoIssues.map(issue => (
          <div 
            key={issue.id} 
            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="min-w-0">
              <div className="font-medium text-gray-900 truncate">{issue.issue}</div>
              <div className="text-sm text-gray-500 mt-0.5">{issue.reports} reported issues</div>
            </div>
            <span className={`
              inline-flex items-center px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ml-4
              ${issue.trend > 0
                ? 'bg-red-50 text-red-600'
                : 'bg-green-50 text-green-600'
              }
            `}>
              {issue.trend > 0 ? '+' : ''}{issue.trend}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendingIssues;