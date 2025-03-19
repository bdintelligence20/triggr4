import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, Globe, Check } from 'lucide-react';

interface ProfileDetailsProps {
  profile: {
    name: string;
    email: string;
    phone: string;
    linkedAccounts: {
      google: boolean;
      microsoft: boolean;
      whatsapp: boolean;
    };
  };
  onUpdate: (updates: any) => void;
}

const ProfileDetails: React.FC<ProfileDetailsProps> = ({ profile, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: profile.name,
    phone: profile.phone
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(formData);
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-lg font-semibold">Personal Information</h2>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="px-4 py-2 text-emerald-400 hover:bg-emerald-50 rounded-lg"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {isEditing ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={e => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={e => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
              >
                Save Changes
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Mail className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="text-sm text-gray-500">Email</div>
                <div className="font-medium">{profile.email}</div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Phone className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="text-sm text-gray-500">Phone</div>
                <div className="font-medium">{profile.phone}</div>
              </div>
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
        <h2 className="text-lg font-semibold mb-6">Linked Accounts</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-50 rounded-lg">
                <Globe className="text-red-400" size={20} />
              </div>
              <div>
                <div className="font-medium">Google Account</div>
                <div className="text-sm text-gray-500">Connect your Google account</div>
              </div>
            </div>
            <button
              onClick={() => onUpdate({
                linkedAccounts: {
                  ...profile.linkedAccounts,
                  google: !profile.linkedAccounts.google
                }
              })}
              className={`px-4 py-2 rounded-lg ${
                profile.linkedAccounts.google
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-emerald-400 text-white hover:bg-emerald-300'
              }`}
            >
              {profile.linkedAccounts.google ? (
                <span className="flex items-center gap-2">
                  <Check size={16} />
                  Connected
                </span>
              ) : (
                'Connect'
              )}
            </button>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Globe className="text-blue-400" size={20} />
              </div>
              <div>
                <div className="font-medium">Microsoft Account</div>
                <div className="text-sm text-gray-500">Connect your Microsoft account</div>
              </div>
            </div>
            <button
              onClick={() => onUpdate({
                linkedAccounts: {
                  ...profile.linkedAccounts,
                  microsoft: !profile.linkedAccounts.microsoft
                }
              })}
              className={`px-4 py-2 rounded-lg ${
                profile.linkedAccounts.microsoft
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-emerald-400 text-white hover:bg-emerald-300'
              }`}
            >
              {profile.linkedAccounts.microsoft ? (
                <span className="flex items-center gap-2">
                  <Check size={16} />
                  Connected
                </span>
              ) : (
                'Connect'
              )}
            </button>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-50 rounded-lg">
                <Globe className="text-green-400" size={20} />
              </div>
              <div>
                <div className="font-medium">WhatsApp Business</div>
                <div className="text-sm text-gray-500">Connect your WhatsApp Business account</div>
              </div>
            </div>
            <button
              onClick={() => onUpdate({
                linkedAccounts: {
                  ...profile.linkedAccounts,
                  whatsapp: !profile.linkedAccounts.whatsapp
                }
              })}
              className={`px-4 py-2 rounded-lg ${
                profile.linkedAccounts.whatsapp
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-emerald-400 text-white hover:bg-emerald-300'
              }`}
            >
              {profile.linkedAccounts.whatsapp ? (
                <span className="flex items-center gap-2">
                  <Check size={16} />
                  Connected
                </span>
              ) : (
                'Connect'
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ProfileDetails;