import React from 'react';
import { CheckCircle, Clock } from 'lucide-react';

const TicketStats = () => {
  return (
    <div className="space-y-4">
      {/* Closed Tickets */}
      <div className="p-4 bg-white rounded-lg shadow-sm">
        <div className="flex items-center gap-2 text-gray-600 mb-2">
          <CheckCircle size={20} className="text-emerald-400" />
          <span className="font-medium">Closed Tickets</span>
        </div>
        <div className="text-3xl font-bold">17</div>
      </div>
      
      {/* Total Tickets Today */}
      <div className="p-4 bg-white rounded-lg shadow-sm">
        <div className="flex items-center gap-2 text-gray-600 mb-2">
          <Clock size={20} className="text-emerald-400" />
          <span className="font-medium">Total Today</span>
        </div>
        <div className="text-3xl font-bold">20</div>
      </div>
    </div>
  );
};

export default TicketStats;