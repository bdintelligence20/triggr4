// components/ui/Loading.tsx
import React from 'react';
import { useAppContext } from '../../contexts/AppContext';

const Loading: React.FC = () => {
  const { isLoading } = useAppContext();

  if (!isLoading) return null;

  return (
    <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-6">
      <p className="font-medium">Loading...</p>
      <p>Please wait while we process your request.</p>
    </div>
  );
};

export default Loading;