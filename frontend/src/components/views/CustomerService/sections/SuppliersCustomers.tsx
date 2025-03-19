import React, { useState } from 'react';
import { Plus, Search, Mail, Clock } from 'lucide-react';

interface Entity {
  id: string;
  name: string;
  email: string;
  activity: string;
  time: string;
  type: 'request' | 'report' | 'inquiry';
}

const demoData: {
  suppliers: Entity[];
  customers: Entity[];
} = {
  suppliers: [
    {
      id: 's1',
      name: 'Global Supplies Ltd',
      email: 'contact@globalsupplies.com',
      activity: 'Submitted inventory report',
      time: '2 hours ago',
      type: 'report'
    },
    {
      id: 's2',
      name: 'Tech Components Inc',
      email: 'info@techcomponents.com',
      activity: 'Updated delivery schedule',
      time: '3 hours ago',
      type: 'request'
    },
    {
      id: 's3',
      name: 'Quality Materials Co',
      email: 'support@qualitymaterials.com',
      activity: 'Requested price quote',
      time: '4 hours ago',
      type: 'inquiry'
    },
    {
      id: 's4',
      name: 'Industrial Solutions',
      email: 'contact@industrialsolutions.com',
      activity: 'Submitted quality report',
      time: '5 hours ago',
      type: 'report'
    },
    {
      id: 's5',
      name: 'Precision Parts Ltd',
      email: 'info@precisionparts.com',
      activity: 'Updated stock levels',
      time: '6 hours ago',
      type: 'report'
    }
  ],
  customers: [
    {
      id: 'c1',
      name: 'Acme Corporation',
      email: 'support@acme.com',
      activity: 'Submitted support ticket',
      time: '1 hour ago',
      type: 'request'
    },
    {
      id: 'c2',
      name: 'Stellar Industries',
      email: 'contact@stellar.com',
      activity: 'Product inquiry',
      time: '2 hours ago',
      type: 'inquiry'
    },
    {
      id: 'c3',
      name: 'Dynamic Systems',
      email: 'info@dynamic.com',
      activity: 'Requested quote',
      time: '3 hours ago',
      type: 'inquiry'
    },
    {
      id: 'c4',
      name: 'Innovative Tech',
      email: 'support@innovativetech.com',
      activity: 'Filed complaint',
      time: '4 hours ago',
      type: 'report'
    },
    {
      id: 'c5',
      name: 'Global Solutions',
      email: 'help@globalsolutions.com',
      activity: 'Support request',
      time: '5 hours ago',
      type: 'request'
    }
  ]
};

const SuppliersCustomers = () => {
  const [activeTab, setActiveTab] = useState<'suppliers' | 'customers'>('suppliers');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = demoData[activeTab].filter(entity =>
    entity.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entity.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getTypeStyles = (type: Entity['type']) => {
    switch (type) {
      case 'report':
        return 'bg-blue-50 text-blue-600';
      case 'request':
        return 'bg-purple-50 text-purple-600';
      case 'inquiry':
        return 'bg-emerald-50 text-emerald-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  return (
    <div>
      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('suppliers')}
          className={`flex-1 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'suppliers'
              ? 'border-emerald-400 text-emerald-400'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Today's Suppliers
        </button>
        <button
          onClick={() => setActiveTab('customers')}
          className={`flex-1 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'customers'
              ? 'border-emerald-400 text-emerald-400'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Today's Customers
        </button>
      </div>

      {/* Search and Add Button */}
      <div className="p-4 flex items-center justify-between gap-4 border-b">
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            placeholder={`Search ${activeTab}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>
        <button
          className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 transition-colors"
        >
          <Plus size={20} />
          Add {activeTab === 'suppliers' ? 'Supplier' : 'Customer'}
        </button>
      </div>

      {/* List */}
      <div className="divide-y">
        {filteredData.map((entity) => (
          <div key={entity.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="min-w-0">
                <h3 className="font-medium truncate">{entity.name}</h3>
                <div className="flex items-center gap-4 mt-1">
                  <div className="flex items-center gap-2 text-gray-500 text-sm">
                    <Mail size={16} />
                    <span>{entity.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 text-sm">
                    <Clock size={16} />
                    <span>{entity.time}</span>
                  </div>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs ${getTypeStyles(entity.type)}`}>
                {entity.activity}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuppliersCustomers;