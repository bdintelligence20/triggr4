import React from 'react';
import { CheckCircle, Clock } from 'lucide-react';

const TicketStats = () => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 space-y-6">
      <div className="flex items-center gap-3 p-4 bg-emerald-50 rounded-lg">
        <div className="p-2 bg-emerald-100 rounded-lg">
          <CheckCircle size={24} className="text-emerald-600" />
        </div>
        <div>
          <div className="text-sm font-medium text-gray-600">Closed Tickets</div>
          <div className="text-2xl font-bold text-emerald-600">17</div>
        </div>
      </div>
      
      <div className="flex items-center gap-3 p-4 bg-emerald-50 rounded-lg">
        <div className="p-2 bg-emerald-100 rounded-lg">
          <Clock size={24} className="text-emerald-600" />
        </div>
        <div>
          <div className="text-sm font-medium text-gray-600">Total Today</div>
          <div className="text-2xl font-bold text-emerald-600">20</div>
        </div>
      </div>
    </div>
  );
};

export default TicketStats;