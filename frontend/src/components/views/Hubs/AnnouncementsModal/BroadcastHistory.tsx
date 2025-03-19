import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Calendar, ChevronDown, Paperclip, Download } from 'lucide-react';

interface Broadcast {
  id: string;
  title: string;
  message: string;
  sentAt: string;
  sender: {
    name: string;
    role: string;
  };
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

const demoBroadcasts: Broadcast[] = [
  {
    id: '1',
    title: 'System Maintenance Notice',
    message: 'Scheduled maintenance will be performed on all systems this weekend.',
    sentAt: '2024-02-10T14:30:00',
    sender: {
      name: 'John Doe',
      role: 'System Administrator'
    },
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
    title: 'New Safety Protocol Update',
    message: 'Important updates to safety protocols have been implemented.',
    sentAt: '2024-02-09T10:15:00',
    sender: {
      name: 'Sarah Chen',
      role: 'Safety Manager'
    },
    recipients: {
      hubs: ['Operations Hub', 'Manufacturing Hub'],
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

const BroadcastHistory = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedMessage, setExpandedMessage] = useState<string | null>(null);

  const filteredBroadcasts = demoBroadcasts.filter(broadcast =>
    broadcast.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    broadcast.message.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
            placeholder="Search announcements..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        </div>
        <select className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400">
          <option value="all">All Hubs</option>
          <option value="operations">Operations Hub</option>
          <option value="manufacturing">Manufacturing Hub</option>
        </select>
      </div>

      {/* Broadcast List */}
      <div className="space-y-4">
        {filteredBroadcasts.map((broadcast) => (
          <motion.div
            key={broadcast.id}
            layout
            className="border rounded-lg overflow-hidden"
          >
            <div className="p-4 bg-white hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{broadcast.title}</h3>
                    <button
                      onClick={() => setExpandedMessage(
                        expandedMessage === broadcast.id ? null : broadcast.id
                      )}
                      className="p-1 hover:bg-gray-100 rounded-lg"
                    >
                      <ChevronDown
                        size={16}
                        className={`transform transition-transform ${
                          expandedMessage === broadcast.id ? 'rotate-180' : ''
                        }`}
                      />
                    </button>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Calendar size={14} />
                      {new Date(broadcast.sentAt).toLocaleString()}
                    </div>
                    <span>By {broadcast.sender.name}</span>
                    <span>To {broadcast.recipients.userCount} users</span>
                    {broadcast.hasAttachments && (
                      <Paperclip size={14} className="text-emerald-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Expanded Content */}
              {expandedMessage === broadcast.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-4 pt-4 border-t"
                >
                  <p className="text-gray-600 mb-4">{broadcast.message}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Sent to:</span>
                      <div className="flex gap-2">
                        {broadcast.recipients.hubs.map((hub) => (
                          <span
                            key={hub}
                            className="px-2 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs"
                          >
                            {hub}
                          </span>
                        ))}
                      </div>
                    </div>
                    {broadcast.hasAttachments && (
                      <button className="flex items-center gap-2 text-emerald-400 hover:text-emerald-500">
                        <Download size={16} />
                        <span className="text-sm">Download Attachments</span>
                      </button>
                    )}
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

export default BroadcastHistory;