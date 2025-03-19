import React from 'react';
import { motion } from 'framer-motion';
import { Bell, Mail, Phone, Volume2 } from 'lucide-react';
import useNotificationStore from '../../../../store/notificationStore';
import { NotificationType } from '../../../../store/notificationStore';

const notificationTypes: { type: NotificationType; label: string }[] = [
  { type: 'system', label: 'System Updates' },
  { type: 'issue', label: 'Issues & Problems' },
  { type: 'announcement', label: 'Announcements' },
  { type: 'request', label: 'Requests' },
  { type: 'escalation', label: 'Escalations' },
  { type: 'hub', label: 'Hub Updates' },
  { type: 'user', label: 'User Activities' }
];

const NotificationSettings = () => {
  const { preferences, updatePreferences } = useNotificationStore();

  const toggleChannel = (channel: keyof typeof preferences) => {
    updatePreferences({ [channel]: !preferences[channel] });
  };

  const toggleNotificationType = (type: NotificationType) => {
    const mutedTypes = preferences.mutedTypes;
    const newMutedTypes = mutedTypes.includes(type)
      ? mutedTypes.filter(t => t !== type)
      : [...mutedTypes, type];
    updatePreferences({ mutedTypes: newMutedTypes });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Notification Settings</h2>

      <div className="bg-white rounded-lg shadow-sm p-6 space-y-8">
        {/* Notification Channels */}
        <div>
          <h3 className="text-lg font-medium mb-4">Notification Channels</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 border rounded-lg"
            >
              <label className="flex items-center justify-between cursor-pointer">
                <div className="flex items-center gap-3">
                  <Bell className="text-emerald-400" size={20} />
                  <span>In-App Notifications</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.inApp}
                  onChange={() => toggleChannel('inApp')}
                  className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400"
                />
              </label>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 border rounded-lg"
            >
              <label className="flex items-center justify-between cursor-pointer">
                <div className="flex items-center gap-3">
                  <Mail className="text-emerald-400" size={20} />
                  <span>Email Notifications</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.email}
                  onChange={() => toggleChannel('email')}
                  className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400"
                />
              </label>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 border rounded-lg"
            >
              <label className="flex items-center justify-between cursor-pointer">
                <div className="flex items-center gap-3">
                  <Phone className="text-emerald-400" size={20} />
                  <span>WhatsApp Notifications</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.whatsapp}
                  onChange={() => toggleChannel('whatsapp')}
                  className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400"
                />
              </label>
            </motion.div>
          </div>
        </div>

        {/* Notification Types */}
        <div>
          <h3 className="text-lg font-medium mb-4">Notification Types</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {notificationTypes.map(({ type, label }) => (
              <motion.div
                key={type}
                whileHover={{ scale: 1.02 }}
                className="p-4 border rounded-lg"
              >
                <label className="flex items-center justify-between cursor-pointer">
                  <span>{label}</span>
                  <input
                    type="checkbox"
                    checked={!preferences.mutedTypes.includes(type)}
                    onChange={() => toggleNotificationType(type)}
                    className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400"
                  />
                </label>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Sound Settings */}
        <div>
          <h3 className="text-lg font-medium mb-4">Sound Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <Volume2 className="text-emerald-400" size={20} />
                <span>Notification Sounds</span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={!preferences.silentMode}
                  onChange={() => updatePreferences({ silentMode: !preferences.silentMode })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings;