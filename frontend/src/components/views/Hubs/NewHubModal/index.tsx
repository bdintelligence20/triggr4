import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Search, Bot, ArrowRight, Users, Check } from 'lucide-react';

interface NewHubModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const availableHubs = [
  {
    id: 'finance',
    name: 'Finance Hub',
    description: 'Manage financial operations and reporting',
    pricePerUser: 7,
    features: [
      'Financial reporting and analysis',
      'Budget management',
      'Expense tracking',
      'Invoice processing',
      'Automated reconciliation',
      'Financial forecasting'
    ]
  },
  {
    id: 'marketing',
    name: 'Marketing Hub',
    description: 'Optimize marketing campaigns and analytics',
    pricePerUser: 7,
    features: [
      'Campaign management',
      'Social media analytics',
      'Content optimization',
      'Performance tracking',
      'A/B testing tools',
      'Marketing automation'
    ]
  },
  {
    id: 'legal',
    name: 'Legal Hub',
    description: 'Handle legal documentation and compliance',
    pricePerUser: 7,
    features: [
      'Contract management',
      'Legal document review',
      'Compliance monitoring',
      'Risk assessment',
      'Case management',
      'Legal workflow automation'
    ]
  },
  {
    id: 'procurement',
    name: 'Procurement Hub',
    description: 'Streamline purchasing and vendor management',
    pricePerUser: 7,
    features: [
      'Vendor management',
      'Purchase order processing',
      'Inventory tracking',
      'Supplier evaluation',
      'Cost analysis',
      'Contract negotiation'
    ]
  }
];

const NewHubModal: React.FC<NewHubModalProps> = ({ isOpen, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedHub, setSelectedHub] = useState<typeof availableHubs[0] | null>(null);
  const [userCount, setUserCount] = useState(5);

  if (!isOpen) return null;

  const filteredHubs = availableHubs.filter(hub =>
    hub.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    hub.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const calculateMonthlyPrice = (pricePerUser: number) => {
    return (pricePerUser * userCount).toFixed(2);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 overflow-y-auto"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="fixed inset-0 bg-black/50" />
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="relative bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
        >
          <div className="flex justify-between items-center p-6 border-b">
            <div>
              <h2 className="text-2xl font-semibold">Add New Hub</h2>
              <p className="text-gray-500 mt-1">Select a hub to enhance your operations</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          <div className="p-6 flex-1 overflow-auto">
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
                <motion.div
                  key={hub.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
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
                    <div className="text-right">
                      <div className="text-lg font-bold text-emerald-600">
                        ${hub.pricePerUser}
                        <span className="text-sm text-gray-500">/user/mo</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {selectedHub && (
            <div className="p-6 border-t bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Users size={20} className="text-gray-400" />
                    <span className="text-sm text-gray-600">Number of Users:</span>
                  </div>
                  <input
                    type="number"
                    min="1"
                    value={userCount}
                    onChange={(e) => setUserCount(Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-20 px-3 py-1.5 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                  />
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Monthly Total</div>
                    <div className="text-2xl font-bold text-emerald-600">
                      ${calculateMonthlyPrice(selectedHub.pricePerUser)}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      // Handle purchase flow
                      console.log('Purchasing hub:', selectedHub.id, 'for', userCount, 'users');
                      onClose();
                    }}
                    className="flex items-center gap-2 px-6 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
                  >
                    <Check size={20} />
                    Subscribe
                  </button>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default NewHubModal;