import React, { useState } from 'react';
import { X, Search, Bot, ArrowRight } from 'lucide-react';

interface NewHubModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const availableHubs = [
  {
    id: 'finance',
    name: 'Finance Hub',
    description: 'Manage financial operations and reporting',
    price: 49.99,
    features: [
      'Financial reporting and analysis',
      'Budget management',
      'Expense tracking',
      'Invoice processing'
    ]
  },
  {
    id: 'marketing',
    name: 'Marketing Hub',
    description: 'Optimize marketing campaigns and analytics',
    price: 39.99,
    features: [
      'Campaign management',
      'Social media analytics',
      'Content optimization',
      'Performance tracking'
    ]
  },
  {
    id: 'legal',
    name: 'Legal Hub',
    description: 'Handle legal documentation and compliance',
    price: 59.99,
    features: [
      'Contract management',
      'Legal document review',
      'Compliance monitoring',
      'Risk assessment'
    ]
  }
];

const NewHubModal: React.FC<NewHubModalProps> = ({ isOpen, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedHub, setSelectedHub] = useState<typeof availableHubs[0] | null>(null);

  if (!isOpen) return null;

  const filteredHubs = availableHubs.filter(hub =>
    hub.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    hub.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-3xl mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Add New Hub</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={20} />
          </button>
        </div>

        <div className="p-6">
          <div className="relative mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search available hubs..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          </div>

          <div className="grid grid-cols-1 gap-4 max-h-[400px] overflow-y-auto">
            {filteredHubs.map((hub) => (
              <div
                key={hub.id}
                className={`p-6 border rounded-lg hover:border-emerald-400 transition-colors cursor-pointer ${
                  selectedHub?.id === hub.id ? 'border-emerald-400 bg-emerald-50' : ''
                }`}
                onClick={() => setSelectedHub(hub)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-emerald-100 rounded-lg">
                      <Bot size={24} className="text-emerald-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{hub.name}</h3>
                      <p className="text-gray-600 mt-1">{hub.description}</p>
                      <ul className="mt-4 space-y-2">
                        {hub.features.map((feature, index) => (
                          <li key={index} className="flex items-center gap-2 text-sm text-gray-600">
                            <ArrowRight size={16} className="text-emerald-400" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="text-lg font-bold text-emerald-600">
                    ${hub.price}
                    <span className="text-sm text-gray-500">/mo</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-4 p-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              // Handle purchase flow
              console.log('Purchasing hub:', selectedHub);
              onClose();
            }}
            disabled={!selectedHub}
            className="px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Purchase Hub
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewHubModal;