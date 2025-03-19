import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ProfileHeader from './sections/ProfileHeader';
import ProfileDetails from './sections/ProfileDetails';
import NotificationPreferences from './sections/NotificationPreferences';
import SecuritySettings from './sections/SecuritySettings';
import UIPreferences from './sections/UIPreferences';
import HubMemberships from './sections/HubMemberships';

type TabType = 'details' | 'notifications' | 'security' | 'preferences' | 'memberships';

interface TabInfo {
  id: TabType;
  label: string;
}

const tabs: TabInfo[] = [
  { id: 'details', label: 'Profile Details' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'security', label: 'Security' },
  { id: 'preferences', label: 'Preferences' },
  { id: 'memberships', label: 'Hub Memberships' }
];

const Profile = () => {
  const [activeTab, setActiveTab] = useState<TabType>('details');
  const [profile, setProfile] = useState({
    name: 'John Doe',
    email: 'john.doe@company.com',
    phone: '+1 (555) 123-4567',
    role: 'Manager',
    avatar: undefined as string | undefined,
    linkedAccounts: {
      google: false,
      microsoft: false,
      whatsapp: false
    },
    notifications: {
      email: true,
      whatsapp: false,
      inApp: true,
      categories: {
        announcements: true,
        ticketUpdates: true,
        messages: true,
        reminders: true
      }
    },
    security: {
      twoFactorEnabled: false,
      lastLogin: new Date().toISOString(),
      loginHistory: []
    },
    preferences: {
      darkMode: false,
      fontSize: 'normal',
      language: 'en'
    }
  });

  const handleProfileUpdate = (updates: Partial<typeof profile>) => {
    setProfile(prev => ({ ...prev, ...updates }));
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'details':
        return <ProfileDetails profile={profile} onUpdate={handleProfileUpdate} />;
      case 'notifications':
        return <NotificationPreferences preferences={profile.notifications} onUpdate={handleProfileUpdate} />;
      case 'security':
        return <SecuritySettings security={profile.security} onUpdate={handleProfileUpdate} />;
      case 'preferences':
        return <UIPreferences preferences={profile.preferences} onUpdate={handleProfileUpdate} />;
      case 'memberships':
        return <HubMemberships />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <ProfileHeader
        name={profile.name}
        role={profile.role}
        avatar={profile.avatar}
        onAvatarChange={(file) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            handleProfileUpdate({ avatar: reader.result as string });
          };
          reader.readAsDataURL(file);
        }}
      />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-4 border-b mb-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-emerald-400 text-emerald-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {renderContent()}
        </motion.div>
      </div>
    </div>
  );
};

export default Profile;