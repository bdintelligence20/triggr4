import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area } from 'recharts';
import { Clock, Download, Info } from 'lucide-react';

// Dummy data for response time analytics
const responseTimeData = [
  { day: 'Mon', avgTime: 3.2, peakTime: 5.8, offHours: 2.1 },
  { day: 'Tue', avgTime: 2.8, peakTime: 4.5, offHours: 1.9 },
  { day: 'Wed', avgTime: 4.1, peakTime: 6.2, offHours: 2.5 },
  { day: 'Thu', avgTime: 3.5, peakTime: 5.1, offHours: 2.3 },
  { day: 'Fri', avgTime: 2.9, peakTime: 4.8, offHours: 1.8 },
  { day: 'Sat', avgTime: 1.8, peakTime: 2.5, offHours: 1.5 },
  { day: 'Sun', avgTime: 1.5, peakTime: 2.2, offHours: 1.2 }
];

// Dummy data for response time by department
const departmentResponseData = [
  { name: 'IT Support', avgTime: 2.8 },
  { name: 'HR', avgTime: 3.5 },
  { name: 'Finance', avgTime: 4.2 },
  { name: 'Operations', avgTime: 2.5 },
  { name: 'Sales', avgTime: 3.1 }
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
            <span className="font-medium">{entry.value} hours</span>
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
      <Clock size={18} className="text-emerald-400" />
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

const ResponseTimeAnalytics = () => {
  const handleDownload = () => {
    console.log('Downloading response time analytics...');
  };

  // Calculate overall average response time
  const overallAvgTime = responseTimeData.reduce((sum, item) => sum + item.avgTime, 0) / responseTimeData.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <ChartHeader 
        title="Response Time Analytics" 
        onDownload={handleDownload} 
      />
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">Overall Avg. Response</p>
          <p className="text-2xl font-bold text-emerald-400">{overallAvgTime.toFixed(1)} hrs</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">Peak Hours Avg.</p>
          <p className="text-2xl font-bold text-amber-500">
            {(responseTimeData.reduce((sum, item) => sum + item.peakTime, 0) / responseTimeData.length).toFixed(1)} hrs
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">Off Hours Avg.</p>
          <p className="text-2xl font-bold text-emerald-400">
            {(responseTimeData.reduce((sum, item) => sum + item.offHours, 0) / responseTimeData.length).toFixed(1)} hrs
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">Fastest Department</p>
          <p className="text-2xl font-bold text-blue-500">
            {departmentResponseData.sort((a, b) => a.avgTime - b.avgTime)[0].name}
          </p>
        </div>
      </div>
      
      <div className="h-[300px] mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={responseTimeData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorAvgTime" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorPeakTime" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorOffHours" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="avgTime" 
              name="Average Time"
              stroke="#10b981" 
              fillOpacity={1} 
              fill="url(#colorAvgTime)" 
            />
            <Area 
              type="monotone" 
              dataKey="peakTime" 
              name="Peak Hours"
              stroke="#f59e0b" 
              fillOpacity={1} 
              fill="url(#colorPeakTime)" 
            />
            <Area 
              type="monotone" 
              dataKey="offHours" 
              name="Off Hours"
              stroke="#10b981" 
              fillOpacity={1} 
              fill="url(#colorOffHours)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 text-xs text-gray-500 italic">
        Based on response time data from the last 7 days
      </div>
    </motion.div>
  );
};

export default ResponseTimeAnalytics;
