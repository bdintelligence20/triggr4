import React from 'react';

const demoTickets = [
  {
    id: 1,
    title: 'Delivery delay for order #12345',
    customer: 'Acme Corp',
    status: 'unassigned',
    time: '2h ago'
  },
  {
    id: 2,
    title: 'Product quality issue',
    customer: 'Global Industries',
    status: 'unassigned',
    time: '3h ago'
  },
  {
    id: 3,
    title: 'Billing discrepancy',
    customer: 'Tech Solutions',
    status: 'in-progress',
    time: '4h ago'
  }
];

const OpenTickets = () => {
  return (
    <div className="bg-white rounded-xl shadow-sm">
      <div className="px-6 py-4 border-b border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900">Open Tickets</h2>
      </div>
      
      <div className="divide-y divide-gray-100">
        {demoTickets.map((ticket) => (
          <div 
            key={ticket.id} 
            className="px-6 py-4 hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900 line-clamp-1">{ticket.title}</h3>
                <span className={`
                  inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full whitespace-nowrap
                  ${ticket.status === 'unassigned' 
                    ? 'bg-amber-100 text-amber-600'
                    : 'bg-blue-100 text-blue-600'}
                `}>
                  {ticket.status === 'unassigned' ? 'Unassigned' : 'In Progress'}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>{ticket.customer}</span>
                <span>{ticket.time}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OpenTickets;