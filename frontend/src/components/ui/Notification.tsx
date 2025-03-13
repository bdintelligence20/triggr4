// components/ui/Notification.tsx
import React from 'react';
import { useAppContext } from '../../contexts/AppContext';

const Notification: React.FC = () => {
  const { notification } = useAppContext();

  if (!notification) return null;

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded-md shadow-lg z-50 animate-fade-in-out">
      {notification}
    </div>
  );
};

export default Notification;