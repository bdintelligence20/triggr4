import React from 'react';
import { BarChart3 } from 'lucide-react';

const metrics = [
  {
    label: 'Response Time',
    value: 85,
    target: 90,
    color: 'emerald'
  },
  {
    label: 'Customer Satisfaction',
    value: 92,
    target: 95,
    color: 'emerald'
  },
  {
    label: 'Issue Resolution',
    value: 78,
    target: 85,
    color: 'emerald'
  }
];

const PerformanceMetrics = () => {
  return (
    <div className="space-y-4">
      <h3 className="font-medium flex items-center gap-2">
        <BarChart3 size={20} className="text-emerald-400" />
        Performance Metrics
      </h3>
      
      <div className="space-y-4">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <div className="flex justify-between text-sm mb-1">
              <span>{metric.label}</span>
              <div className="flex items-center gap-2">
                <span className={`text-${metric.color}-400`}>{metric.value}%</span>
                <span className="text-gray-400 text-xs">Target: {metric.target}%</span>
              </div>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full bg-${metric.color}-400 rounded-full transition-all duration-500`} 
                style={{ width: `${metric.value}%` }} 
              />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="p-4 bg-emerald-50 rounded-lg">
          <div className="text-2xl font-bold text-emerald-600">2.5h</div>
          <div className="text-sm text-emerald-600">Avg. Response Time</div>
        </div>
        <div className="p-4 bg-emerald-50 rounded-lg">
          <div className="text-2xl font-bold text-emerald-600">94%</div>
          <div className="text-sm text-emerald-600">Resolution Rate</div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;