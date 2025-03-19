import React from 'react';
import { motion } from 'framer-motion';
import { Bell, User, FileText } from 'lucide-react';
import useRoleStore from '../../../store/roleStore';

const notifications = [
  {
    id: 1,
    type: 'user',
    message: 'New user registered in HR Hub',
    time: '2 hours ago',
    roles: ['super_admin', 'hub_admin']
  },
  {
    id: 2,
    type: 'report',
    message: 'Monthly safety report is ready',
    time: '3 hours ago',
    roles: ['super_admin', 'hub_admin', 'user']
  },
  {
    id: 3,
    type: 'alert',
    message: 'System maintenance scheduled',
    time: '5 hours ago',
    roles: ['super_admin', 'hub_admin', 'user']
  }
];

const NotificationsPanel = () => {
  const { currentRole } = useRoleStore();
  
  const filteredNotifications = notifications.filter(
    notification => notification.roles.includes(currentRole || 'user')
  );

  const getIcon = (type: string) => {
    switch (type) {
      case 'user':
        return <User size={16} className="text-blue-400" />;
      case 'report':
        return <FileText size={16} className="text-emerald-400" />;
      default:
        return <Bell size={16} className="text-amber-400" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Recent Notifications</h2>
        <span className="px-2 py-1 bg-emerald-100 text-emerald-600 text-xs font-medium rounded-full">
          {filteredNotifications.length} new
        </span>
      </div>

      <div className="space-y-4">
        {filteredNotifications.map(notification => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            <div className="p-2 bg-gray-100 rounded-lg">
              {getIcon(notification.type)}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {notification.message}
              </p>
              <span className="text-xs text-gray-500">
                {notification.time}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default NotificationsPanel;