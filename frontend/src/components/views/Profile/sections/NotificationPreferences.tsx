import React from 'react';
import { motion } from 'framer-motion';
import { Bell, Mail, MessageSquare } from 'lucide-react';

interface NotificationPreferencesProps {
  preferences: {
    email: boolean;
    whatsapp: boolean;
    inApp: boolean;
    categories: {
      announcements: boolean;
      ticketUpdates: boolean;
      messages: boolean;
      reminders: boolean;
    };
  };
  onUpdate: (updates: any) => void;
}

const NotificationPreferences: React.FC<NotificationPreferencesProps> = ({
  preferences,
  onUpdate
}) => {
  const handleChannelToggle = (channel: 'email' | 'whatsapp' | 'inApp') => {
    onUpdate({
      notifications: {
        ...preferences,
        [channel]: !preferences[channel]
      }
    });
  };

  const handleCategoryToggle = (category: keyof typeof preferences.categories) => {
    onUpdate({
      notifications: {
        ...preferences,
        categories: {
          ...preferences.categories,
          [category]: !preferences.categories[category]
        }
      }
    });
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Notification Channels</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Bell className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="font-medium">In-App Notifications</div>
                <div className="text-sm text-gray-500">Receive notifications within the platform</div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.inApp}
                onChange={() => handleChannelToggle('inApp')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Mail className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="font-medium">Email Notifications</div>
                <div className="text-sm text-gray-500">Receive notifications via email</div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.email}
                onChange={() => handleChannelToggle('email')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <MessageSquare className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="font-medium">WhatsApp Notifications</div>
                <div className="text-sm text-gray-500">Receive notifications via WhatsApp</div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.whatsapp}
                onChange={() => handleChannelToggle('whatsapp')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
            </label>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Notification Categories</h2>
        <div className="space-y-4">
          {Object.entries(preferences.categories).map(([category, enabled]) => (
            <div key={category} className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <div className="font-medium">
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </div>
                <div className="text-sm text-gray-500">
                  Receive notifications about {category}
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={() => handleCategoryToggle(category as keyof typeof preferences.categories)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
              </label>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default NotificationPreferences;