import React from 'react';
import { motion } from 'framer-motion';
import { Camera } from 'lucide-react';

interface ProfileHeaderProps {
  name: string;
  role: string;
  avatar?: string;
  onAvatarChange: (file: File) => void;
}

const ProfileHeader: React.FC<ProfileHeaderProps> = ({
  name,
  role,
  avatar,
  onAvatarChange
}) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onAvatarChange(file);
    }
  };

  return (
    <div className="relative">
      {/* Reduced height banner */}
      <div className="h-32 bg-gradient-to-r from-emerald-400 to-emerald-500" />
      
      {/* Profile content container */}
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col items-center -mt-16">
          {/* Avatar */}
          <div className="relative mb-4">
            <div className="w-32 h-32 bg-white rounded-full p-1">
              {avatar ? (
                <img
                  src={avatar}
                  alt={name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-emerald-100 rounded-full flex items-center justify-center">
                  <span className="text-4xl font-bold text-emerald-400">
                    {name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
              )}
            </div>
            <label className="absolute bottom-0 right-0 p-2 bg-emerald-400 rounded-full text-white hover:bg-emerald-300 cursor-pointer">
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handleFileChange}
              />
              <Camera size={16} />
            </label>
          </div>
          
          {/* Name and role below avatar */}
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">{name}</h1>
            <div className="mt-2">
              <span className="px-2 py-1 bg-emerald-100 text-emerald-600 rounded-full text-sm">
                {role}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileHeader;