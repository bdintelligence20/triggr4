// components/ui/Error.tsx
import React from 'react';
import { AlertCircle } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';

const Error: React.FC = () => {
  const { error } = useAppContext();

  if (!error) return null;

  return (
    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start">
      <AlertCircle size={20} className="mr-2 mt-0.5 flex-shrink-0" />
      <div>
        <p className="font-medium">Error</p>
        <p>{error}</p>
      </div>
    </div>
  );
};

export default Error;