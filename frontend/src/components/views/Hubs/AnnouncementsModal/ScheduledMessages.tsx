import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Edit2, Trash2, ChevronDown, Search } from 'lucide-react';
import { demoHubs } from '../../../data/demo-data';

interface ScheduledMessage {
  id: string;
  title: string;
  message: string;
  scheduledFor: string;
  recipients: {
    hubs: string[];
    userCount: number;
  };
  deliveryMethods: {
    whatsapp: boolean;
    email: boolean;
    inApp: boolean;
  };
  hasAttachments: boolean;
}

const demoScheduledMessages: ScheduledMessage[] = [
  {
    id: '1',
    title: 'Quarterly Review Meeting',
    message: 'Please join us for the quarterly review meeting next week.',
    scheduledFor: '2024-03-15T10:00:00',
    recipients: {
      hubs: ['All Hubs'],
      userCount: 150
    },
    deliveryMethods: {
      whatsapp: true,
      email: true,
      inApp: true
    },
    hasAttachments: true
  },
  {
    id: '2',
    title: 'System Update Notification',
    message: 'Important system updates will be rolled out next month.',
    scheduledFor: '2024-03-20T09:00:00',
    recipients: {
      hubs: ['IT Hub', 'Operations Hub'],
      userCount: 75
    },
    deliveryMethods: {
      whatsapp: false,
      email: true,
      inApp: true
    },
    hasAttachments: false
  }
];

const ScheduledMessages = () => {
  const [expandedMessage, setExpandedMessage] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedHub, setSelectedHub] = useState<string>('all');

  const handleEdit = (messageId: string) => {
    console.log('Editing message:', messageId);
  };

  const handleDelete = (messageId: string) => {
    console.log('Deleting message:', messageId);
  };

  const filteredMessages = demoScheduledMessages.filter(message => {
    const matchesSearch = message.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      message.message.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesHub = selectedHub === 'all' || message.recipients.hubs.includes(selectedHub);

    return matchesSearch && matchesHub;
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="p-6"
    >
      {/* Search & Filters */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search scheduled notifications..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>
        <select
          value={selectedHub}
          onChange={(e) => setSelectedHub(e.target.value)}
          className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        >
          <option value="all">All Hubs</option>
          {demoHubs.map(hub => (
            <option key={hub.id} value={hub.name}>{hub.name}</option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        {filteredMessages.map((message) => (
          <motion.div
            key={message.id}
            layout
            className="border rounded-lg overflow-hidden"
          >
            <div className="p-4 bg-white hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{message.title}</h3>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEdit(message.id)}
                        className="p-1.5 text-gray-400 hover:text-emerald-400 hover:bg-emerald-50 rounded-lg"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(message.id)}
                        className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-50 rounded-lg"
                      >
                        <Trash2 size={16} />
                      </button>
                      <button
                        onClick={() => setExpandedMessage(
                          expandedMessage === message.id ? null : message.id
                        )}
                        className="p-1.5 hover:bg-gray-100 rounded-lg"
                      >
                        <ChevronDown
                          size={16}
                          className={`transform transition-transform ${
                            expandedMessage === message.id ? 'rotate-180' : ''
                          }`}
                        />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Calendar size={14} />
                      {new Date(message.scheduledFor).toLocaleDateString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock size={14} />
                      {new Date(message.scheduledFor).toLocaleTimeString()}
                    </div>
                    <span>To {message.recipients.userCount} users</span>
                  </div>
                </div>
              </div>

              {/* Expanded Content */}
              {expandedMessage === message.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-4 pt-4 border-t"
                >
                  <p className="text-gray-600 mb-4">{message.message}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Will be sent to:</span>
                      <div className="flex gap-2">
                        {message.recipients.hubs.map((hub) => (
                          <span
                            key={hub}
                            className="px-2 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs"
                          >
                            {hub}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Delivery methods:</span>
                      <div className="flex gap-2">
                        {message.deliveryMethods.whatsapp && (
                          <span className="px-2 py-1 bg-green-50 text-green-600 rounded-full text-xs">
                            WhatsApp
                          </span>
                        )}
                        {message.deliveryMethods.email && (
                          <span className="px-2 py-1 bg-blue-50 text-blue-600 rounded-full text-xs">
                            Email
                          </span>
                        )}
                        {message.deliveryMethods.inApp && (
                          <span className="px-2 py-1 bg-purple-50 text-purple-600 rounded-full text-xs">
                            In-App
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default ScheduledMessages;