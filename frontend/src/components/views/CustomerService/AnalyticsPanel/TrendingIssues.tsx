import React from 'react';
import { TrendingUp } from 'lucide-react';

interface TrendingIssue {
  id: string;
  issue: string;
  count: number;
  trend: number;
}

const demoIssues: TrendingIssue[] = [
  {
    id: '1',
    issue: 'Delivery Delays',
    count: 24,
    trend: 15
  },
  {
    id: '2',
    issue: 'Product Quality',
    count: 18,
    trend: -8
  },
  {
    id: '3',
    issue: 'Billing Questions',
    count: 12,
    trend: 5
  }
];

const TrendingIssues = () => {
  return (
    <div className="space-y-4">
      <h3 className="font-medium flex items-center gap-2">
        <TrendingUp size={20} className="text-emerald-400" />
        Trending Issues
      </h3>
      
      <div className="space-y-3">
        {demoIssues.map((issue) => (
          <div key={issue.id} className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <span className="font-medium">{issue.issue}</span>
              <div className="text-sm text-gray-500">{issue.count} reports</div>
            </div>
            <span className={`px-2 py-1 rounded-full text-sm ${
              issue.trend > 0
                ? 'bg-red-100 text-red-600'
                : 'bg-green-100 text-green-600'
            }`}>
              {issue.trend > 0 ? '+' : ''}{issue.trend}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendingIssues;