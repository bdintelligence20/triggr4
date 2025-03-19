import React from 'react';
import { Users, Calendar, FileText } from 'lucide-react';

const HRPanel = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold mb-6">HR Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <Users className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Employee Directory</h3>
          <p className="text-gray-500 mt-2">Access and manage employee information</p>
        </button>

        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <Calendar className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Leave Management</h3>
          <p className="text-gray-500 mt-2">Handle time-off requests and approvals</p>
        </button>

        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <FileText className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">HR Policies</h3>
          <p className="text-gray-500 mt-2">View and update company policies</p>
        </button>
      </div>
    </div>
  );
};

export default HRPanel;