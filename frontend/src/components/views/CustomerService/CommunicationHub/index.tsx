import React from 'react';
import { MessageSquare, Mail, Bell } from 'lucide-react';
import AutoResponseSettings from './AutoResponseSettings';
import MessageList from './MessageList';

const CommunicationHub = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold mb-4">Communication Hub</h2>
        <div className="flex gap-4">
          <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100">
            <MessageSquare size={20} />
            Send Message
          </button>
          <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100">
            <Mail size={20} />
            Send Email
          </button>
          <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100">
            <Bell size={20} />
            Send Notification
          </button>
        </div>
      </div>
      
      <div className="p-4">
        <AutoResponseSettings />
        <MessageList />
      </div>
    </div>
  );
};

export default CommunicationHub;