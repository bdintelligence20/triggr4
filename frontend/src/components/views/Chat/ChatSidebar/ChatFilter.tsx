import React, { useState } from 'react';
import { Filter, ChevronDown } from 'lucide-react';

interface ChatFilterProps {
  selectedSource: 'all' | 'ai' | 'employee';
  selectedType: 'all' | 'requests' | 'reports';
  onSourceChange: (source: 'all' | 'ai' | 'employee') => void;
  onTypeChange: (type: 'all' | 'requests' | 'reports') => void;
}

const ChatFilter: React.FC<ChatFilterProps> = ({
  selectedSource,
  selectedType,
  onSourceChange,
  onTypeChange
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="px-4 py-2 border-b">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
      >
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-gray-400" />
          <span>Filters</span>
        </div>
        <ChevronDown
          size={16}
          className={`text-gray-400 transition-transform duration-200 ${
            isExpanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      <div
        className={`space-y-2 overflow-hidden transition-all duration-200 ${
          isExpanded ? 'max-h-40 opacity-100 mt-2' : 'max-h-0 opacity-0'
        }`}
      >
        <select
          value={selectedSource}
          onChange={(e) => onSourceChange(e.target.value as 'all' | 'ai' | 'employee')}
          className="w-full px-2 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        >
          <option value="all">All Sources</option>
          <option value="ai">AI Chats</option>
          <option value="employee">Employee Chats</option>
        </select>
        <select
          value={selectedType}
          onChange={(e) => onTypeChange(e.target.value as 'all' | 'requests' | 'reports')}
          className="w-full px-2 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        >
          <option value="all">All Types</option>
          <option value="requests">Requests</option>
          <option value="reports">Reports</option>
        </select>
      </div>
    </div>
  );
}

export default ChatFilter;