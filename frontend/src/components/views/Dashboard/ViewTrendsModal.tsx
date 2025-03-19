import React from 'react';
import { X, ArrowUp, ArrowDown, AlertTriangle, CheckCircle, Info } from 'lucide-react';

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

interface ViewTrendsModalProps {
  isOpen: boolean;
  onClose: () => void;
  issue: TrendingIssue;
}

const ViewTrendsModal: React.FC<ViewTrendsModalProps> = ({
  isOpen,
  onClose,
  issue
}) => {
  if (!isOpen) return null;

  const getTrendColor = (trend: number) => {
    if (trend > 20) return 'text-red-600';
    if (trend > 0) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertTriangle className="text-red-500" size={18} />;
      case 'medium':
        return <Info className="text-yellow-500" size={18} />;
      case 'low':
        return <CheckCircle className="text-green-500" size={18} />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            {getPriorityIcon(issue.priority)}
            <h2 className="text-xl font-semibold">{issue.title}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto flex-1">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Department</p>
              <p className="font-medium">{issue.department}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Requests</p>
              <p className="font-medium">{issue.requests} in {issue.timeframe}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Trend</p>
              <div className="flex items-center gap-1">
                {issue.trend > 0 ? (
                  <ArrowUp size={16} className={getTrendColor(issue.trend)} />
                ) : (
                  <ArrowDown size={16} className={getTrendColor(issue.trend)} />
                )}
                <span className={`font-medium ${getTrendColor(issue.trend)}`}>
                  {Math.abs(issue.trend)}%
                </span>
              </div>
            </div>
          </div>
          
          {issue.commonCauses && (
            <div className="mb-8">
              <h3 className="text-lg font-medium mb-4">Common Causes</h3>
              <ul className="space-y-2">
                {issue.commonCauses.map((cause, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="p-1 bg-blue-50 rounded-full mt-0.5">
                      <div className="w-2 h-2 bg-blue-400 rounded-full" />
                    </div>
                    <span>{cause}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {issue.preventiveMeasures && (
            <div className="mb-8">
              <h3 className="text-lg font-medium mb-4">Preventive Measures</h3>
              <ul className="space-y-2">
                {issue.preventiveMeasures.map((measure, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <div className="p-1 bg-emerald-50 rounded-full mt-0.5">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                    </div>
                    <span>{measure}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {issue.relatedIssues && issue.relatedIssues.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-4">Related Issues</h3>
              <div className="space-y-3">
                {issue.relatedIssues.map((relatedIssue) => (
                  <div 
                    key={relatedIssue.id}
                    className="p-4 border rounded-lg hover:border-emerald-200 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getPriorityIcon(relatedIssue.priority)}
                        <h4 className="font-medium">{relatedIssue.title}</h4>
                      </div>
                      <div className="flex items-center gap-1">
                        {relatedIssue.trend > 0 ? (
                          <ArrowUp size={14} className={getTrendColor(relatedIssue.trend)} />
                        ) : (
                          <ArrowDown size={14} className={getTrendColor(relatedIssue.trend)} />
                        )}
                        <span className={`text-sm font-medium ${getTrendColor(relatedIssue.trend)}`}>
                          {Math.abs(relatedIssue.trend)}%
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                      <span>{relatedIssue.department}</span>
                      <span>•</span>
                      <span>{relatedIssue.requests} requests</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className="p-6 border-t bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ViewTrendsModal;
