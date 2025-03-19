import React from 'react';
import { MessageSquare, Mail } from 'lucide-react';

interface Message {
  id: string;
  type: 'message' | 'email';
  sender: string;
  content: string;
  timestamp: string;
  status: 'sent' | 'delivered' | 'read';
}

const demoMessages: Message[] = [
  {
    id: '1',
    type: 'message',
    sender: 'Acme Corporation',
    content: 'When can we expect the delivery of our latest order?',
    timestamp: '2024-02-10T14:30:00',
    status: 'read'
  },
  {
    id: '2',
    type: 'email',
    sender: 'Global Supplies Ltd',
    content: 'Updated price list for Q1 2024',
    timestamp: '2024-02-10T13:45:00',
    status: 'delivered'
  }
];

const MessageList = () => {
  return (
    <div className="space-y-3">
      {demoMessages.map((message) => (
        <div key={message.id} className="p-3 border rounded-lg hover:bg-gray-50">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${
              message.type === 'message' ? 'bg-emerald-100' : 'bg-blue-100'
            }`}>
              {message.type === 'message' ? (
                <MessageSquare size={20} className="text-emerald-600" />
              ) : (
                <Mail size={20} className="text-blue-600" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-medium">{message.sender}</span>
                <span className="text-sm text-gray-500">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{message.content}</p>
              <span className={`inline-block px-2 py-0.5 text-xs rounded-full mt-2 ${
                message.status === 'read' 
                  ? 'bg-green-100 text-green-600'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {message.status}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;