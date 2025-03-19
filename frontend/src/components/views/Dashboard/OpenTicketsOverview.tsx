import React from 'react';
import { motion } from 'framer-motion';
import { Bell, MessageSquare, FileText, Calendar } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import useNotificationStore from '../../../store/notificationStore';
import useRoleStore from '../../../store/roleStore';

// Demo data for chat distribution
const chatDistributionData = [
  { name: 'Support', value: 35, color: '#10B981' }, // emerald-400
  { name: 'Technical', value: 25, color: '#3B82F6' }, // blue-500
  { name: 'Feedback', value: 20, color: '#8B5CF6' }, // purple-500
  { name: 'General', value: 15, color: '#F59E0B' }, // amber-500
  { name: 'Urgent', value: 5, color: '#EF4444' }  // red-500
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-2 border rounded-lg shadow-lg">
        <p className="text-sm font-medium">{payload[0].name}</p>
        <p className="text-sm text-gray-500">{payload[0].value}%</p>
      </div>
    );
  }
  return null;
};

const OpenTicketsOverview = () => {
  const { currentRole } = useRoleStore();
  const { notifications } = useNotificationStore();

  // Filter notifications based on role and sort by timestamp
  const recentNotifications = notifications
    .filter(n => n.allowedRoles.includes(currentRole || 'user'))
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 5); // Only show 5 most recent notifications

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'issue':
        return <MessageSquare className="text-emerald-400" size={20} />;
      case 'report':
        return <FileText className="text-emerald-400" size={20} />;
      default:
        return <Bell className="text-emerald-400" size={20} />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'issue':
        return 'bg-red-100 text-red-600';
      case 'report':
        return 'bg-blue-100 text-blue-600';
      case 'announcement':
        return 'bg-purple-100 text-purple-600';
      default:
        return 'bg-emerald-100 text-emerald-600';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6 space-y-6"
    >
      {/* Notifications Section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <Bell className="text-emerald-500" size={20} />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Recent Notifications</h2>
              <p className="text-sm text-gray-500 mt-1">
                Latest updates and activities
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {recentNotifications.map((notification) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.01 }}
              className="flex items-center justify-between p-4 border rounded-xl hover:border-emerald-200 transition-colors cursor-pointer"
            >
              <div className="flex items-start gap-3 flex-1">
                <div className="p-2 bg-emerald-50 rounded-lg">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="min-w-0">
                  <h3 className="font-medium truncate">{notification.title}</h3>
                  <p className="text-sm text-gray-500 line-clamp-2 mt-1">
                    {notification.message}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4 ml-4">
                <span className={`px-2 py-1 rounded-full text-xs ${getNotificationColor(notification.type)}`}>
                  {notification.type}
                </span>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar size={14} />
                  {new Date(notification.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Chat Distribution Chart */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-medium mb-4">Chat Categories</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chatDistributionData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chatDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="middle" 
                align="right"
                layout="vertical"
                wrapperStyle={{
                  paddingLeft: '20px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
};

export default OpenTicketsOverview;