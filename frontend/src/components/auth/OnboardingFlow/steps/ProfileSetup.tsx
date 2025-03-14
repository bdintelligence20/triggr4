import React, { useState } from 'react';
import { Camera, User } from 'lucide-react';

const defaultAvatars = [
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Max',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Lucy',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah'
];

interface ProfileSetupProps {
  onComplete: (data: { photoUrl: string }) => void;
}

const ProfileSetup: React.FC<ProfileSetupProps> = ({ onComplete }) => {
  const [selectedAvatar, setSelectedAvatar] = useState<string | null>(null);
  const [customPhoto, setCustomPhoto] = useState<string | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setCustomPhoto(reader.result as string);
        setSelectedAvatar(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleContinue = () => {
    if (customPhoto || selectedAvatar) {
      onComplete({ photoUrl: customPhoto || selectedAvatar || '' });
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Add a Profile Photo</h1>
        <p className="text-gray-600">
          Choose an avatar or upload your own photo
        </p>
      </div>

      <div className="space-y-8">
        {/* Custom Photo Upload */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center">
              {customPhoto ? (
                <img 
                  src={customPhoto} 
                  alt="Profile" 
                  className="w-full h-full object-cover"
                />
              ) : selectedAvatar ? (
                <img 
                  src={selectedAvatar} 
                  alt="Selected Avatar" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <User size={48} className="text-gray-400" />
              )}
            </div>
            <label className="absolute bottom-0 right-0 p-2 bg-emerald-400 rounded-full text-white cursor-pointer hover:bg-emerald-300 transition-colors">
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handleFileUpload}
              />
              <Camera size={16} />
            </label>
          </div>
        </div>

        {/* Avatar Selection */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-4">Or choose an avatar</h3>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-4">
            {defaultAvatars.map((avatar, index) => (
              <button
                key={index}
                onClick={() => {
                  setSelectedAvatar(avatar);
                  setCustomPhoto(null);
                }}
                className={`relative rounded-full overflow-hidden aspect-square ${
                  selectedAvatar === avatar ? 'ring-2 ring-emerald-400' : ''
                }`}
              >
                <img 
                  src={avatar} 
                  alt={`Avatar ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleContinue}
          disabled={!customPhoto && !selectedAvatar}
          className="w-full py-2 px-4 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue
        </button>
      </div>
    </div>
  );
};

export default ProfileSetup;