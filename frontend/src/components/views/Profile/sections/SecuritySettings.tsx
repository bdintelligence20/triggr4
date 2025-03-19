import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Key, History } from 'lucide-react';

interface SecuritySettingsProps {
  security: {
    twoFactorEnabled: boolean;
    lastLogin: string;
    loginHistory: Array<{
      timestamp: string;
      ip: string;
      device: string;
    }>;
  };
  onUpdate: (updates: any) => void;
}

const SecuritySettings: React.FC<SecuritySettingsProps> = ({
  security,
  onUpdate
}) => {
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle password change
    console.log('Changing password:', passwordForm);
    setIsChangingPassword(false);
    setPasswordForm({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Password & Authentication</h2>
        
        {isChangingPassword ? (
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Password
              </label>
              <input
                type="password"
                value={passwordForm.currentPassword}
                onChange={e => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                type="password"
                value={passwordForm.newPassword}
                onChange={e => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                value={passwordForm.confirmPassword}
                onChange={e => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
            </div>

            <div className="flex justify-end gap-4">
              <button
                type="button"
                onClick={() => setIsChangingPassword(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
              >
                Update Password
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <button
              onClick={() => setIsChangingPassword(true)}
              className="px-4 py-2 text-emerald-400 hover:bg-emerald-50 rounded-lg"
            >
              Change Password
            </button>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-50 rounded-lg">
                  <Shield className="text-emerald-400" size={20} />
                </div>
                <div>
                  <div className="font-medium">Two-Factor Authentication</div>
                  <div className="text-sm text-gray-500">Add an extra layer of security</div>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={security.twoFactorEnabled}
                  onChange={() => onUpdate({
                    security: {
                      ...security,
                      twoFactorEnabled: !security.twoFactorEnabled
                    }
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
              </label>
            </div>
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Login History</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <History className="text-emerald-400" size={20} />
            </div>
            <div>
              <div className="text-sm text-gray-500">Last Login</div>
              <div className="font-medium">
                {new Date(security.lastLogin).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default SecuritySettings;