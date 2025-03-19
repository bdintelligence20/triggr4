import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, ArrowUp, ArrowDown, Filter, Calendar, AlertCircle } from 'lucide-react';
import { Button } from '../../ui/button';

interface Trend {
  id: string;
  title: string;
  department: string;
  reportCount: number;
  trend: number;
  timeframe: string;
  commonCauses?: string[];
  preventiveMeasures?: string[];
  lastOccurrence?: string;
}

interface ViewTrendsModalProps {
  isOpen: boolean;
  onClose: () => void;
  trends: Trend[];
}

const ViewTrendsModal: React.FC<ViewTrendsModalProps> = ({
  isOpen,
  onClose,
  trends
}) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'7d' | '30d' | '90d'>('7d');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [expandedTrend, setExpandedTrend] = useState<string | null>(null);

  if (!isOpen) return null;

  const filteredTrends = trends.filter(trend => 
    selectedDepartment === 'all' || trend.department === selectedDepartment
  );

  const getDepartmentColor = (department: string) => {
    switch (department) {
      case 'HR':
        return 'bg-purple-50 text-purple-600';
      case 'IT':
        return 'bg-blue-50 text-blue-600';
      case 'Operations':
        return 'bg-emerald-50 text-emerald-600';
      case 'Safety':
        return 'bg-red-50 text-red-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 overflow-y-auto"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="fixed inset-0 bg-black/50" />
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="relative bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="p-6 border-b">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-50 rounded-lg">
                  <TrendingUp className="text-emerald-500" size={24} />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">View Trends</h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Analyze and track recurring issues across departments
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-4 mt-6">
              <div className="flex items-center gap-2">
                <Filter size={16} className="text-gray-400" />
                <span className="text-sm font-medium text-gray-700">Filters:</span>
              </div>

              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value as '7d' | '30d' | '90d')}
                className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last quarter</option>
              </select>

              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              >
                <option value="all">All Departments</option>
                <option value="HR">HR</option>
                <option value="IT">IT</option>
                <option value="Operations">Operations</option>
                <option value="Safety">Safety</option>
              </select>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6 space-y-4">
              {filteredTrends.map((trend) => (
                <motion.div
                  key={trend.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="border rounded-lg overflow-hidden"
                >
                  <div
                    onClick={() => setExpandedTrend(expandedTrend === trend.id ? null : trend.id)}
                    className="p-4 bg-white hover:bg-gray-50 cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gray-50 rounded-lg">
                          <AlertCircle size={20} className="text-gray-400" />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{trend.title}</h3>
                          <div className="flex items-center gap-3 mt-1">
                            <span className={`px-2 py-1 rounded-full text-xs ${getDepartmentColor(trend.department)}`}>
                              {trend.department}
                            </span>
                            <span className="text-sm text-gray-500">
                              {trend.reportCount} reports in {trend.timeframe}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm ${
                        trend.trend > 0 
                          ? 'bg-red-50 text-red-600' 
                          : 'bg-green-50 text-green-600'
                      }`}>
                        {trend.trend > 0 ? (
                          <ArrowUp size={16} />
                        ) : (
                          <ArrowDown size={16} />
                        )}
                        <span>{Math.abs(trend.trend)}%</span>
                      </div>
                    </div>
                  </div>

                  <AnimatePresence>
                    {expandedTrend === trend.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t bg-gray-50"
                      >
                        <div className="p-4 space-y-4">
                          {trend.commonCauses && (
                            <div>
                              <h4 className="text-sm font-medium text-gray-900 mb-2">Common Causes</h4>
                              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                                {trend.commonCauses.map((cause, index) => (
                                  <li key={index}>{cause}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {trend.preventiveMeasures && (
                            <div>
                              <h4 className="text-sm font-medium text-gray-900 mb-2">Preventive Measures</h4>
                              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                                {trend.preventiveMeasures.map((measure, index) => (
                                  <li key={index}>{measure}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {trend.lastOccurrence && (
                            <div className="text-sm text-gray-500">
                              Last occurrence: {new Date(trend.lastOccurrence).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t bg-gray-50">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Calendar size={16} />
                <span>Last updated: {new Date().toLocaleString()}</span>
              </div>
              <Button
                variant="outline"
                onClick={onClose}
              >
                Close
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ViewTrendsModal;