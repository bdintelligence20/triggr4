import React from 'react';

const CSATMetrics = () => {
  return (
    <>
      {/* CSAT Today */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-base font-semibold text-gray-900">CSAT Today</h3>
        </div>
        <div className="p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-500">Score</span>
            <span className="text-2xl font-bold text-emerald-400">78%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-emerald-400 rounded-full transition-all duration-500"
              style={{ width: '78%' }}
            />
          </div>
        </div>
      </div>

      {/* CSAT Average */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-base font-semibold text-gray-900">CSAT Average</h3>
        </div>
        <div className="p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-500">Score</span>
            <span className="text-2xl font-bold text-emerald-400">68%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-emerald-400 rounded-full transition-all duration-500"
              style={{ width: '68%' }}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default CSATMetrics;