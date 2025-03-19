import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, ArrowUp, ArrowDown } from 'lucide-react';
import useRoleStore from '../../../store/roleStore';
import ViewTrendsModal from './ViewTrendsModal';

interface TrendingIssue {
  id: string;
  title: string;
  department: string;
  trend: number;
  requests: number;
  timeframe: string;
  priority: 'high' | 'medium' | 'low';
  relatedIssues?: TrendingIssue[];
  commonCauses?: string[];
  preventiveMeasures?: string[];
}

const demoIssues: TrendingIssue[] = [
  {
    id: '1',
    title: 'System Access Problems',
    department: 'IT',
    trend: 45,
    requests: 28,
    timeframe: '7 days',
    priority: 'high',
    commonCauses: [
      'Network connectivity issues',
      'Server overload',
      'Authentication errors'
    ],
    preventiveMeasures: [
      'Regular system maintenance',
      'Load balancing implementation',
      'Backup authentication system'
    ],
    relatedIssues: [
      {
        id: '1-1',
        title: 'VPN Connection Issues',
        department: 'IT',
        trend: 15,
        requests: 12,
        timeframe: '7 days',
        priority: 'medium'
      },
      {
        id: '1-2',
        title: 'Database Performance',
        department: 'IT',
        trend: 25,
        requests: 18,
        timeframe: '7 days',
        priority: 'high'
      }
    ]
  },
  {
    id: '2',
    title: 'Equipment Maintenance Delays',
    department: 'Operations',
    trend: -12,
    requests: 15,
    timeframe: '7 days',
    priority: 'medium',
    commonCauses: [
      'Parts shortage',
      'Technician availability',
      'Scheduling conflicts'
    ],
    preventiveMeasures: [
      'Inventory management system',
      'Preventive maintenance schedule',
      'On-call technician rotation'
    ],
    relatedIssues: [
      {
        id: '2-1',
        title: 'Equipment Downtime',
        department: 'Operations',
        trend: -8,
        requests: 10,
        timeframe: '7 days',
        priority: 'medium'
      }
    ]
  },
  {
    id: '3',
    title: 'Safety Protocol Violations',
    department: 'Safety',
    trend: 23,
    requests: 22,
    timeframe: '7 days',
    priority: 'high',
    commonCauses: [
      'Lack of training',
      'Unclear procedures',
      'Time pressure'
    ],
    preventiveMeasures: [
      'Regular safety training',
      'Updated safety documentation',
      'Safety audits'
    ],
    relatedIssues: [
      {
        id: '3-1',
        title: 'PPE Compliance',
        department: 'Safety',
        trend: 18,
        requests: 15,
        timeframe: '7 days',
        priority: 'high'
      }
    ]
  }
];

const TrendingIssues = () => {
  const { currentRole } = useRoleStore();
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('7d');
  const [selectedIssue, setSelectedIssue] = useState<TrendingIssue | null>(null);

  const isAdmin = currentRole === 'super_admin' || currentRole === 'hub_admin';
  if (!isAdmin) return null;

  const getFilteredIssues = () => {
    let filtered = [...demoIssues];

    if (selectedDepartment !== 'all') {
      filtered = filtered.filter(issue => 
        issue.department === selectedDepartment
      );
    }

    return filtered;
  };

  const getTrendColor = (trend: number) => {
    if (trend > 20) return 'bg-red-100 text-red-600';
    if (trend > 0) return 'bg-yellow-100 text-yellow-600';
    return 'bg-green-100 text-green-600';
  };

  const getDepartmentColor = (department: string) => {
    switch (department) {
      case 'IT':
        return 'bg-blue-50 text-blue-600 font-medium';
      case 'Operations':
        return 'bg-emerald-50 text-emerald-600 font-medium';
      case 'Safety':
        return 'bg-red-50 text-red-600 font-medium';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <TrendingUp size={20} className="text-emerald-400" />
          <h2 className="text-lg font-semibold">Trending Issues</h2>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          >
            <option value="all">All Departments</option>
            <option value="IT">IT</option>
            <option value="Operations">Operations</option>
            <option value="Safety">Safety</option>
            <option value="HR">HR</option>
          </select>
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last quarter</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {getFilteredIssues().map((issue) => (
          <motion.div
            key={issue.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            whileHover={{ scale: 1.01 }}
            onClick={() => setSelectedIssue(issue)}
            className="flex items-center justify-between p-4 border rounded-xl hover:border-emerald-200 transition-colors cursor-pointer"
          >
            <div className="flex items-start gap-3 flex-1">
              <div className={`p-2 rounded-lg ${
                issue.priority === 'high' ? 'bg-red-50' :
                issue.priority === 'medium' ? 'bg-yellow-50' :
                'bg-green-50'
              }`}>
                <TrendingUp size={20} className={
                  issue.priority === 'high' ? 'text-red-500' :
                  issue.priority === 'medium' ? 'text-yellow-500' :
                  'text-green-500'
                } />
              </div>
              <div className="min-w-0">
                <h3 className="font-medium truncate">{issue.title}</h3>
                <div className="flex items-center gap-3 mt-1">
                  <span className={`px-2 py-1 rounded-full text-xs ${getDepartmentColor(issue.department)}`}>
                    {issue.department}
                  </span>
                  <span className="text-sm text-gray-500">
                    {issue.requests} requests in {issue.timeframe}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${getTrendColor(issue.trend)}`}>
                {issue.trend > 0 ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                {Math.abs(issue.trend)}%
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {selectedIssue && (
        <ViewTrendsModal
          isOpen={true}
          onClose={() => setSelectedIssue(null)}
          issue={selectedIssue}
        />
      )}
    </motion.div>
  );
};

export default TrendingIssues;
