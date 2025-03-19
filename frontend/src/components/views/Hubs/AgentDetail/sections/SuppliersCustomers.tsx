import React, { useState } from 'react';
import { Plus } from 'lucide-react';

interface Entity {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
  lastContact: string;
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
      status: 'active',
      lastContact: '2024-02-10'
    },
    {
      id: 's2',
      name: 'Tech Components Inc',
      email: 'info@techcomponents.com',
      status: 'active',
      lastContact: '2024-02-09'
    }
  ],
  customers: [
    {
      id: 'c1',
      name: 'Acme Corporation',
      email: 'support@acme.com',
      status: 'active',
      lastContact: '2024-02-10'
    },
    {
      id: 'c2',
      name: 'Stellar Industries',
      email: 'contact@stellar.com',
      status: 'inactive',
      lastContact: '2024-02-08'
    }
  ]
};

const SuppliersCustomers = () => {
  const [activeTab, setActiveTab] = useState<'suppliers' | 'customers'>('suppliers');

  const renderList = (items: Entity[]) => (
    <div className="divide-y divide-gray-100">
      {items.map(item => (
        <div key={item.id} className="p-4 hover:bg-gray-50">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">{item.name}</div>
              <div className="text-sm text-gray-500">{item.email}</div>
              <div className="flex items-center gap-4 mt-1">
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  item.status === 'active'
                    ? 'bg-green-100 text-green-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {item.status}
                </span>
                <span className="text-xs text-gray-500">
                  Last contact: {new Date(item.lastContact).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('suppliers')}
          className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'suppliers'
              ? 'border-emerald-400 text-emerald-400'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Suppliers
        </button>
        <button
          onClick={() => setActiveTab('customers')}
          className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'customers'
              ? 'border-emerald-400 text-emerald-400'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Customers
        </button>
      </div>

      {/* Header with Add Button */}
      <div className="p-4 border-b border-gray-100 flex justify-between items-center">
        <h2 className="text-lg font-semibold">
          {activeTab === 'suppliers' ? 'Suppliers' : 'Customers'}
        </h2>
        <button className="flex items-center gap-2 px-4 py-2 text-emerald-400 hover:bg-emerald-50 rounded-lg transition-colors">
          <Plus size={20} />
          <span>Add New</span>
        </button>
      </div>

      {/* Content */}
      <div className="max-h-[400px] overflow-y-auto">
        {activeTab === 'suppliers' ? renderList(demoData.suppliers) : renderList(demoData.customers)}
      </div>
    </div>
  );
};

export default SuppliersCustomers;