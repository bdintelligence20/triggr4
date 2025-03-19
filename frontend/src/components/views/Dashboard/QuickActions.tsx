import React from 'react';
import { motion } from 'framer-motion';
import { Plus, AlertTriangle, MessageSquare, Bell } from 'lucide-react';
import useRoleStore from '../../../store/roleStore';

const QuickActions = () => {
  const { currentRole } = useRoleStore();
  const isAdmin = currentRole === 'super_admin' || currentRole === 'hub_admin';

  const actions = [
    {
      icon: Plus,
      label: 'Add Hub',
      color: 'emerald',
      roles: ['super_admin']
    },
    {
      icon: AlertTriangle,
      label: 'Report Issue',
      color: 'red',
      roles: ['super_admin', 'hub_admin', 'user']
    },
    {
      icon: MessageSquare,
      label: 'Send Message',
      color: 'blue',
      roles: ['super_admin', 'hub_admin', 'user']
    },
    {
      icon: Bell,
      label: 'Announcement',
      color: 'purple',
      roles: ['super_admin', 'hub_admin']
    }
  ].filter(action => action.roles.includes(currentRole || 'user'));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-6"
    >
      <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
      <div className="grid grid-cols-2 gap-3">
        {actions.map(({ icon: Icon, label, color }) => (
          <button
            key={label}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl transition-colors
              bg-${color}-50 hover:bg-${color}-100 text-${color}-600`}
          >
            <Icon size={24} />
            <span className="text-sm font-medium">{label}</span>
          </button>
        ))}
      </div>
    </motion.div>
  );
};

export default QuickActions;