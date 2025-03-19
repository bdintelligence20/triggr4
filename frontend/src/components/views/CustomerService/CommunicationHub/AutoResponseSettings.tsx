import React, { useState } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';

interface AutoResponse {
  id: string;
  trigger: string;
  response: string;
  isActive: boolean;
}

const demoResponses: AutoResponse[] = [
  {
    id: '1',
    trigger: 'New Request',
    response: 'Thank you for your request. We will get back to you within 24 hours.',
    isActive: true
  },
  {
    id: '2',
    trigger: 'Support Ticket',
    response: 'Your support ticket has been received. Our team will review it shortly.',
    isActive: true
  }
];

const AutoResponseSettings = () => {
  const [responses, setResponses] = useState(demoResponses);
  const [isEditing, setIsEditing] = useState<string | null>(null);

  const toggleResponse = (id: string) => {
    setResponses(prev => prev.map(response =>
      response.id === id ? { ...response, isActive: !response.isActive } : response
    ));
  };

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium">Auto-Response Settings</h3>
        <button className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300">
          <Plus size={16} />
          Add Response
        </button>
      </div>
      
      <div className="space-y-3">
        {responses.map((response) => (
          <div key={response.id} className="p-3 border rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-4">
                <span className="font-medium">{response.trigger}</span>
                <div className="flex items-center gap-2">
                  <button className="p-1 text-gray-400 hover:text-emerald-400">
                    <Edit2 size={14} />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-red-400">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={response.isActive}
                  onChange={() => toggleResponse(response.id)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
              </label>
            </div>
            <p className="text-sm text-gray-600">{response.response}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AutoResponseSettings;