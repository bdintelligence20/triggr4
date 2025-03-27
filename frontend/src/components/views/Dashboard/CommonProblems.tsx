import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, Download, Info } from 'lucide-react';

// Dummy data for common problems
const commonProblemsData = [
  { problem: "System Access Issues", count: 78, category: "IT", trend: 5 },
  { problem: "Password Reset Requests", count: 65, category: "IT", trend: -2 },
  { problem: "Document Upload Errors", count: 52, category: "Operations", trend: 12 },
  { problem: "Report Generation Failures", count: 43, category: "Operations", trend: 8 },
  { problem: "Permission Denied Errors", count: 37, category: "IT", trend: -4 }
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-medium text-gray-900 mb-1">{payload[0].payload.problem}</p>
        <div className="flex items-center gap-2 text-sm">
          <div className="w-2 h-2 rounded-full bg-emerald-400" />
          <span className="text-gray-600">Count:</span>
          <span className="font-medium">{payload[0].value}</span>
        </div>
        <div className="flex items-center gap-2 text-sm mt-1">
          <div className="w-2 h-2 rounded-full bg-blue-400" />
          <span className="text-gray-600">Category:</span>
          <span className="font-medium">{payload[0].payload.category}</span>
        </div>
        <div className="flex items-center gap-2 text-sm mt-1">
          <div className="w-2 h-2 rounded-full bg-amber-400" />
          <span className="text-gray-600">Trend:</span>
          <span className={`font-medium ${payload[0].payload.trend > 0 ? 'text-red-500' : 'text-green-500'}`}>
            {payload[0].payload.trend > 0 ? '+' : ''}{payload[0].payload.trend}%
          </span>
        </div>
      </div>
    );
  }
  return null;
};

const ChartHeader = ({ title, onDownload }: { title: string; onDownload: () => void }) => (
  <div className="flex items-center justify-between mb-6">
    <div className="flex items-center gap-2">
      <AlertTriangle size={18} className="text-amber-500" />
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

const CommonProblems = () => {
  const handleDownload = () => {
    console.log('Downloading common problems chart...');
  };

  const getBarColor = (index: number) => {
    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];
    return colors[index % colors.length];
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <ChartHeader 
        title="Most Common Problems Reported" 
        onDownload={handleDownload} 
      />
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={commonProblemsData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
            <XAxis type="number" domain={[0, 'dataMax + 10']} />
            <YAxis 
              type="category" 
              dataKey="problem" 
              width={150}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" barSize={20}>
              {commonProblemsData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(index)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 text-xs text-gray-500 italic">
        Based on reported issues in the last 30 days
      </div>
    </motion.div>
  );
};

export default CommonProblems;
