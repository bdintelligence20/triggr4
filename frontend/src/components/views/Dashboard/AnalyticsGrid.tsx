import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  BarChart, Bar, Legend, Area, AreaChart
} from 'recharts';
import { Download, Info } from 'lucide-react';
import useRoleStore from '../../../store/roleStore';

const activityData = [
  { name: 'Mon', requests: 40, reports: 24 },
  { name: 'Tue', requests: 30, reports: 13 },
  { name: 'Wed', requests: 20, reports: 98 },
  { name: 'Thu', requests: 27, reports: 39 },
  { name: 'Fri', requests: 18, reports: 48 },
  { name: 'Sat', requests: 23, reports: 38 },
  { name: 'Sun', requests: 34, reports: 43 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-medium text-gray-900 mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{entry.name}:</span>
            <span className="font-medium">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const ChartHeader = ({ title, onDownload }: { title: string; onDownload: () => void }) => (
  <div className="flex items-center justify-between mb-6">
    <div className="flex items-center gap-2">
      <h3 className="text-lg font-semibold">{title}</h3>
      <Info size={16} className="text-gray-400 cursor-help" />
    </div>
    <button
      onClick={onDownload}
      className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
    >
      <Download size={18} />
    </button>
  </div>
);

const AnalyticsGrid = () => {
  const { currentRole } = useRoleStore();
  const isAdmin = currentRole === 'super_admin' || currentRole === 'hub_admin';
  const [activeDataKeys, setActiveDataKeys] = useState<string[]>(['requests', 'reports']);

  const handleDownload = (chartType: string) => {
    console.log(`Downloading ${chartType} chart...`);
  };

  const handleLegendClick = (dataKey: string) => {
    setActiveDataKeys(prev => 
      prev.includes(dataKey)
        ? prev.filter(key => key !== dataKey)
        : [...prev, dataKey]
    );
  };

  const CustomLegend = () => (
    <div className="flex items-center justify-center gap-4 mt-4">
      <button
        onClick={() => handleLegendClick('requests')}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-colors ${
          activeDataKeys.includes('requests')
            ? 'bg-emerald-100 text-emerald-600'
            : 'bg-gray-100 text-gray-500'
        }`}
      >
        <div className="w-2 h-2 rounded-full bg-emerald-400" />
        Requests
      </button>
      {isAdmin && (
        <button
          onClick={() => handleLegendClick('reports')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-colors ${
            activeDataKeys.includes('reports')
              ? 'bg-blue-100 text-blue-600'
              : 'bg-gray-100 text-gray-500'
          }`}
        >
          <div className="w-2 h-2 rounded-full bg-blue-400" />
          Reports
        </button>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Activity Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-sm p-6"
      >
        <ChartHeader 
          title="Activity Trends" 
          onDownload={() => handleDownload('activity')} 
        />
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={activityData}>
              <defs>
                <linearGradient id="requestsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="reportsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#f0f0f0" 
                vertical={false} 
              />
              <XAxis 
                dataKey="name" 
                stroke="#9ca3af"
                axisLine={false}
                tickLine={false}
                dy={10}
              />
              <YAxis 
                stroke="#9ca3af"
                axisLine={false}
                tickLine={false}
                dx={-10}
                domain={[0, 100]}
                ticks={[0, 20, 40, 60, 80, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              {activeDataKeys.includes('requests') && (
                <Area
                  type="monotone"
                  dataKey="requests"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#requestsGradient)"
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
              )}
              {isAdmin && activeDataKeys.includes('reports') && (
                <Area
                  type="monotone"
                  dataKey="reports"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#reportsGradient)"
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
          <CustomLegend />
        </div>
      </motion.div>
    </div>
  );
};

export default AnalyticsGrid;