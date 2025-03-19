import React, { useState } from 'react';
import { Paperclip, Mic, Send } from 'lucide-react';
import { demoHubs } from '../../../data/demo-data';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  placeholder?: string;
  selectedHub: number | null;
  onHubSelect: (hubId: number | null) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  placeholder,
  selectedHub,
  onHubSelect
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        {/* Hub Pills */}
        <div className="flex flex-wrap gap-2 mb-3">
          <button
            type="button"
            onClick={() => onHubSelect(null)}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              selectedHub === null
                ? 'bg-emerald-100 text-emerald-600'
                : 'bg-gray-100 text-gray-600 hover:bg-emerald-50 hover:text-emerald-600'
            }`}
          >
            General
          </button>
          {demoHubs.map(hub => (
            <button
              key={hub.id}
              type="button"
              onClick={() => onHubSelect(hub.id)}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                selectedHub === hub.id
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-gray-100 text-gray-600 hover:bg-emerald-50 hover:text-emerald-600'
              }`}
            >
              {hub.name}
            </button>
          ))}
        </div>

        {/* Message Input */}
        <div className="relative flex items-center gap-2">
          <div className="flex-1 relative">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={placeholder || "Type your message..."}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 resize-none pr-24"
              rows={1}
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <button type="button" className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
                <Paperclip size={20} />
              </button>
              <button type="button" className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
                <Mic size={20} />
              </button>
              <button
                type="submit"
                className="p-1.5 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ChatInput;