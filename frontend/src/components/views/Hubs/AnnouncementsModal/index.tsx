import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Bell } from 'lucide-react';
import { Button } from '../../../ui/button';
import NewAnnouncement from './NewAnnouncement';
import BroadcastHistory from './BroadcastHistory';
import ScheduledMessages from './ScheduledMessages';
import useRoleStore from '../../../../store/roleStore';

interface AnnouncementsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'new' | 'history' | 'scheduled';

const AnnouncementsModal: React.FC<AnnouncementsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('new');
  const { currentRole } = useRoleStore();
  const isAdmin = currentRole === 'super_admin' || currentRole === 'hub_admin';

  if (!isAdmin) return null;

  return (
    <AnimatePresence>
      {isOpen && (
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
              {/* Header */}
              <div className="p-6 border-b">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-50 rounded-lg">
                      <Bell className="text-emerald-500" size={24} />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">Announcements</h2>
                      <p className="text-sm text-gray-500 mt-1">
                        {currentRole === 'super_admin' 
                          ? 'Manage announcements across all hubs'
                          : 'Manage announcements for your hub'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Tabs */}
                <div className="flex gap-4">
                  <button
                    onClick={() => setActiveTab('new')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === 'new'
                        ? 'bg-emerald-50 text-emerald-600'
                        : 'text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    New Announcement
                  </button>
                  <button
                    onClick={() => setActiveTab('history')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === 'history'
                        ? 'bg-emerald-50 text-emerald-600'
                        : 'text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    Broadcast History
                  </button>
                  <button
                    onClick={() => setActiveTab('scheduled')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === 'scheduled'
                        ? 'bg-emerald-50 text-emerald-600'
                        : 'text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    Scheduled Messages
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto">
                <AnimatePresence mode="wait">
                  {activeTab === 'new' && <NewAnnouncement />}
                  {activeTab === 'history' && <BroadcastHistory />}
                  {activeTab === 'scheduled' && <ScheduledMessages />}
                </AnimatePresence>
              </div>

              {/* Footer */}
              <div className="p-4 border-t bg-gray-50">
                <div className="flex justify-end">
                  <Button
                    variant="outline"
                    onClick={onClose}
                  >
                    Close
                  </Button>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AnnouncementsModal;