import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { FileText, Download, Info, Search } from 'lucide-react';

// Dummy data for document usage
const topDocumentsData = [
  { id: 1, name: "Employee Handbook", category: "HR", accessCount: 245, type: "pdf" },
  { id: 2, name: "Product Specifications", category: "Product", accessCount: 187, type: "docx" },
  { id: 3, name: "Customer Service Guidelines", category: "Support", accessCount: 156, type: "pdf" },
  { id: 4, name: "System Troubleshooting Guide", category: "IT", accessCount: 132, type: "pdf" },
  { id: 5, name: "Onboarding Checklist", category: "HR", accessCount: 118, type: "xlsx" }
];

// Dummy data for document type distribution
const documentTypeData = [
  { name: 'PDF', value: 58, color: '#ef4444' },
  { name: 'Word', value: 22, color: '#3b82f6' },
  { name: 'Excel', value: 12, color: '#10b981' },
  { name: 'PowerPoint', value: 8, color: '#f59e0b' }
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-medium text-gray-900 mb-1">{payload[0].name}</p>
        <div className="flex items-center gap-2 text-sm">
          <div 
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: payload[0].payload.color }}
          />
          <span className="text-gray-600">Count:</span>
          <span className="font-medium">{payload[0].value}%</span>
        </div>
      </div>
    );
  }
  return null;
};

const ChartHeader = ({ title, onDownload }: { title: string; onDownload: () => void }) => (
  <div className="flex items-center justify-between mb-6">
    <div className="flex items-center gap-2">
      <FileText size={18} className="text-purple-500" />
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

const DocumentUsage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  const handleDownload = () => {
    console.log('Downloading document usage data...');
  };

  const filteredDocuments = topDocumentsData.filter(doc => 
    doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <div className="p-1 rounded bg-red-100 text-red-600">PDF</div>;
      case 'docx':
        return <div className="p-1 rounded bg-blue-100 text-blue-600">DOC</div>;
      case 'xlsx':
        return <div className="p-1 rounded bg-green-100 text-green-600">XLS</div>;
      case 'pptx':
        return <div className="p-1 rounded bg-amber-100 text-amber-600">PPT</div>;
      default:
        return <div className="p-1 rounded bg-gray-100 text-gray-600">FILE</div>;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <ChartHeader 
        title="Most Queried Documents" 
        onDownload={handleDownload} 
      />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Document Type Distribution */}
        <div className="flex justify-center items-center">
          <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={documentTypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {documentTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Top Documents Table */}
        <div className="md:col-span-2">
          <div className="mb-4 relative">
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          </div>
          
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Access Count
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                      {doc.name}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                      {doc.category}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                      {getDocumentTypeIcon(doc.type)}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                      <span className="font-medium text-purple-500">{doc.accessCount}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-gray-500 italic">
        Based on document access data from the last 30 days
      </div>
    </motion.div>
  );
};

export default DocumentUsage;
