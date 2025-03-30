import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { HelpCircle, Download, Info, Filter } from 'lucide-react';

// Dummy data for common questions
const commonQuestionsData = [
  { 
    id: 1, 
    question: "How do I reset my password?", 
    category: "IT Support", 
    count: 87,
    trend: 5,
    relatedQuestions: [
      "Where do I find the password reset option?",
      "What are the password requirements?"
    ]
  },
  { 
    id: 2, 
    question: "When will my benefits start?", 
    category: "HR", 
    count: 64,
    trend: -2,
    relatedQuestions: [
      "How do I enroll in benefits?",
      "What benefits am I eligible for?"
    ]
  },
  { 
    id: 3, 
    question: "How do I submit an expense report?", 
    category: "Finance", 
    count: 58,
    trend: 12,
    relatedQuestions: [
      "What expenses are reimbursable?",
      "How long does expense approval take?"
    ]
  },
  { 
    id: 4, 
    question: "Where can I find the company policies?", 
    category: "HR", 
    count: 52,
    trend: 3,
    relatedQuestions: [
      "Is there a dress code policy?",
      "What is the time off policy?"
    ]
  },
  { 
    id: 5, 
    question: "How do I connect to the VPN?", 
    category: "IT Support", 
    count: 45,
    trend: -8,
    relatedQuestions: [
      "Which VPN client should I use?",
      "Why can't I connect to the VPN?"
    ]
  }
];

// Question categories for filtering
const categories = [
  { id: 'all', name: 'All Categories' },
  { id: 'IT Support', name: 'IT Support' },
  { id: 'HR', name: 'HR' },
  { id: 'Finance', name: 'Finance' },
  { id: 'Operations', name: 'Operations' },
  { id: 'Sales', name: 'Sales' }
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-medium text-gray-900 mb-1">{data.question}</p>
        <div className="flex items-center gap-2 text-sm">
          <div className="w-2 h-2 rounded-full bg-purple-500" />
          <span className="text-gray-600">Count:</span>
          <span className="font-medium">{data.count}</span>
        </div>
        <div className="flex items-center gap-2 text-sm mt-1">
          <div className="w-2 h-2 rounded-full bg-amber-400" />
          <span className="text-gray-600">Category:</span>
          <span className="font-medium">{data.category}</span>
        </div>
        <div className="flex items-center gap-2 text-sm mt-1">
          <div className="w-2 h-2 rounded-full bg-emerald-400" />
          <span className="text-gray-600">Trend:</span>
          <span className={`font-medium ${data.trend > 0 ? 'text-red-500' : 'text-green-500'}`}>
            {data.trend > 0 ? '+' : ''}{data.trend}%
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
      <HelpCircle size={18} className="text-purple-500" />
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

const CommonQuestions = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);
  
  const handleDownload = () => {
    console.log('Downloading common questions data...');
  };

  const filteredQuestions = selectedCategory === 'all'
    ? commonQuestionsData
    : commonQuestionsData.filter(q => q.category === selectedCategory);

  const getBarColor = (index: number) => {
    const colors = ['#8b5cf6', '#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95'];
    return colors[index % colors.length];
  };

  const toggleQuestion = (id: number) => {
    setExpandedQuestion(expandedQuestion === id ? null : id);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <ChartHeader 
        title="Most Common Questions" 
        onDownload={handleDownload} 
      />
      
      <div className="mb-6 flex items-center gap-2">
        <Filter size={16} className="text-gray-400" />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
        >
          {categories.map(category => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>
      
      <div className="h-[300px] mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={filteredQuestions}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
            <XAxis type="number" domain={[0, 'dataMax + 10']} />
            <YAxis 
              type="category" 
              dataKey="question" 
              width={200}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" barSize={20}>
              {filteredQuestions.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(index)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-700">Question Details</h4>
        {filteredQuestions.map((question) => (
          <div 
            key={question.id}
            className="border rounded-lg overflow-hidden"
          >
            <div 
              className="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50"
              onClick={() => toggleQuestion(question.id)}
            >
              <div>
                <div className="font-medium">{question.question}</div>
                <div className="text-sm text-gray-500 mt-1">
                  {question.category} • {question.count} occurrences
                </div>
              </div>
              <div className={`transform transition-transform ${expandedQuestion === question.id ? 'rotate-180' : ''}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
            </div>
            
            {expandedQuestion === question.id && (
              <div className="p-4 bg-gray-50 border-t">
                <h5 className="text-sm font-medium text-gray-700 mb-2">Related Questions:</h5>
                <ul className="space-y-1">
                  {question.relatedQuestions.map((relatedQ, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                      <div className="p-1 bg-purple-50 rounded-full mt-0.5">
                        <div className="w-1.5 h-1.5 bg-purple-500 rounded-full" />
                      </div>
                      {relatedQ}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-xs text-gray-500 italic">
        Based on questions asked in the last 30 days
      </div>
    </motion.div>
  );
};

export default CommonQuestions;
