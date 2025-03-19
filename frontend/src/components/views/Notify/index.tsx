import React, { useState } from 'react';
import { motion } from 'framer-motion';
import NewAnnouncement from '../Hubs/AnnouncementsModal/NewAnnouncement';
import BroadcastHistory from '../Hubs/AnnouncementsModal/BroadcastHistory';
import ScheduledMessages from '../Hubs/AnnouncementsModal/ScheduledMessages';

type TabType = 'new' | 'scheduled' | 'history';

const Notify = () => {
  const [activeTab, setActiveTab] = useState<TabType>('new');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-8">
        <div className="max-w-[1920px] mx-auto space-y-8">
          {/* Header */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Notifications</h2>
            <p className="text-gray-500 mt-2">Manage and send notifications across your organization</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 border-b">
            <button
              onClick={() => setActiveTab('new')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'new'
                  ? 'border-emerald-400 text-emerald-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              New Notification
            </button>
            <button
              onClick={() => setActiveTab('scheduled')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'scheduled'
                  ? 'border-emerald-400 text-emerald-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Scheduled Notifications
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'history'
                  ? 'border-emerald-400 text-emerald-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Notification History
            </button>
          </div>

          {/* Content */}
          <div className="bg-white rounded-lg shadow-sm">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'new' && <NewAnnouncement />}
              {activeTab === 'scheduled' && <ScheduledMessages />}
              {activeTab === 'history' && <BroadcastHistory />}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Notify;