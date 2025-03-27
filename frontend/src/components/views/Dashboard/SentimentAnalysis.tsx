import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { SmilePlus, Download, Info } from 'lucide-react';

// Dummy data for sentiment analysis
const sentimentData = [
  { month: 'Jan', overall: 72, support: 68, engineering: 75, marketing: 80 },
  { month: 'Feb', overall: 68, support: 65, engineering: 70, marketing: 78 },
  { month: 'Mar', overall: 74, support: 72, engineering: 73, marketing: 82 },
  { month: 'Apr', overall: 78, support: 75, engineering: 76, marketing: 85 },
  { month: 'May', overall: 76, support: 73, engineering: 78, marketing: 83 },
  { month: 'Jun', overall: 80, support: 78, engineering: 82, marketing: 86 }
];

// Dummy data for department sentiment
const departmentSentiment = [
  { department: 'Customer Support', sentiment: 75, responses: 120 },
  { department: 'Engineering', sentiment: 78, responses: 85 },
  { department: 'Marketing', sentiment: 84, responses: 42 },
  { department: 'Sales', sentiment: 72, responses: 63 },
  { department: 'HR', sentiment: 81, responses: 28 }
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
            <span className="font-medium">{entry.value}%</span>
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
      <SmilePlus size={18} className="text-blue-500" />
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

const SentimentGauge = ({ value }: { value: number }) => {
  // Calculate color based on sentiment value
  const getColor = () => {
    if (value >= 80) return '#10b981'; // green
    if (value >= 70) return '#3b82f6'; // blue
    if (value >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        {/* Background circle */}
        <svg className="w-full h-full" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="10"
          />
          {/* Foreground circle - the gauge */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={getColor()}
            strokeWidth="10"
            strokeDasharray={`${value * 2.83} 283`} // 283 is approx 2*PI*45
            strokeDashoffset="0"
            transform="rotate(-90 50 50)"
          />
        </svg>
        {/* Value text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold">{value}%</span>
        </div>
      </div>
      <p className="mt-2 text-sm font-medium">Overall Sentiment</p>
    </div>
  );
};

const SentimentAnalysis = () => {
  const handleDownload = () => {
    console.log('Downloading sentiment analysis chart...');
  };

  // Calculate current overall sentiment (average of last month)
  const currentSentiment = sentimentData[sentimentData.length - 1].overall;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <ChartHeader 
        title="Staff Sentiment Analysis" 
        onDownload={handleDownload} 
      />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="flex justify-center items-center">
          <SentimentGauge value={currentSentiment} />
        </div>
        
        <div className="md:col-span-2">
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={sentimentData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[50, 100]} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="overall" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="support" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="engineering" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="marketing" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-gray-500 italic">
        Based on staff feedback and interaction analysis over the last 6 months
      </div>
    </motion.div>
  );
};

export default SentimentAnalysis;
