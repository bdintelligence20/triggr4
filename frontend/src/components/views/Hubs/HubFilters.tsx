import React from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';

interface HubFiltersProps {
  onSearch: (query: string) => void;
  onFilter: (status: string) => void;
}

const HubFilters = ({ onSearch, onFilter }: HubFiltersProps) => {
  return (
    <div className="flex flex-wrap gap-4 items-center">
      <div className="flex-1 min-w-[300px]">
        <div className="relative">
          <input
            type="text"
            placeholder="Search hubs..."
            className="w-full pl-12 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            onChange={(e) => onSearch(e.target.value)}
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>
      </div>

      <div className="flex gap-4">
        <select
          onChange={(e) => onFilter(e.target.value)}
          className="px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 min-w-[160px]"
        >
          <option value="all">All Status</option>
          <option value="pending">Has Pending Issues</option>
          <option value="none">No Pending Issues</option>
        </select>

        <button className="p-3 border rounded-lg hover:bg-gray-50">
          <SlidersHorizontal size={20} className="text-gray-500" />
        </button>
      </div>
    </div>
  );
};

export default HubFilters;