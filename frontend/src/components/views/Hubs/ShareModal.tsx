import React, { useState } from 'react';
import { X, Search, Apple as WhatsApp, Mail, MessageSquare, Users } from 'lucide-react';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ShareModal: React.FC<ShareModalProps> = ({ isOpen, onClose }) => {
  const [whatsappNumber, setWhatsappNumber] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [customRecipient, setCustomRecipient] = useState('');
  const [sendToAll, setSendToAll] = useState(false);

  if (!isOpen) return null;

  const handleGenerateNumber = () => {
    // In a real app, this would make an API call to generate a WhatsApp number
    const generatedNumber = '+1234567890'; // Example number
    setWhatsappNumber(generatedNumber);
  };

  const handleShare = (method: 'whatsapp' | 'email' | 'sms') => {
    if (!whatsappNumber) return;

    const message = `Connect with us on WhatsApp: ${whatsappNumber}`;
    let url = '';

    switch (method) {
      case 'whatsapp':
        url = `https://wa.me/?text=${encodeURIComponent(message)}`;
        break;
      case 'email':
        url = `mailto:?subject=Our WhatsApp Contact&body=${encodeURIComponent(message)}`;
        break;
      case 'sms':
        url = `sms:?body=${encodeURIComponent(message)}`;
        break;
    }

    window.open(url, '_blank');
    onClose();
  };

  if (!whatsappNumber) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg w-full max-w-md mx-4">
          <div className="flex justify-between items-center p-4 border-b">
            <h2 className="text-xl font-semibold">Share WhatsApp Number</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
              <X size={20} />
            </button>
          </div>

          <div className="p-6 space-y-6">
            <div className="flex items-center justify-center">
              <div className="p-4 bg-emerald-50 rounded-full">
                <WhatsApp size={32} className="text-emerald-400" />
              </div>
            </div>

            <div className="text-center">
              <p className="text-gray-600">
                Generate a WhatsApp number to share with hub members.
              </p>
            </div>

            <button
              onClick={handleGenerateNumber}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 transition-colors"
            >
              <WhatsApp size={20} />
              Generate WhatsApp Number
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-md mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Share WhatsApp Number</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* WhatsApp Number Display */}
          <div className="p-4 bg-emerald-50 rounded-lg text-center">
            <p className="text-sm text-emerald-600 font-medium">Your WhatsApp Number</p>
            <p className="text-lg font-bold text-emerald-700 mt-1">{whatsappNumber}</p>
          </div>

          {/* Send to All Members Toggle */}
          <label className="flex items-center justify-between p-4 border rounded-lg cursor-pointer">
            <div className="flex items-center gap-3">
              <Users size={20} className="text-gray-400" />
              <div>
                <div className="font-medium">Send to All Members</div>
                <div className="text-sm text-gray-500">Share with everyone in this hub</div>
              </div>
            </div>
            <input
              type="checkbox"
              checked={sendToAll}
              onChange={(e) => setSendToAll(e.target.checked)}
              className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400"
            />
          </label>

          {!sendToAll && (
            <>
              {/* Search Members */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Search Members</label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by name or email..."
                    className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                  />
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                </div>
              </div>

              {/* Custom Recipient */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Or Enter Email/Phone</label>
                <input
                  type="text"
                  value={customRecipient}
                  onChange={(e) => setCustomRecipient(e.target.value)}
                  placeholder="Enter email or phone number"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                />
              </div>
            </>
          )}

          {/* Share Buttons */}
          <div className="flex items-center justify-center gap-4 pt-4 border-t">
            <button
              onClick={() => handleShare('whatsapp')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#25D366] text-white hover:bg-[#1da851] transition-colors text-sm font-medium shadow-sm hover:shadow"
            >
              <WhatsApp size={16} />
              WhatsApp
            </button>
            <button
              onClick={() => handleShare('email')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-400 text-white hover:bg-emerald-300 transition-colors text-sm font-medium shadow-sm hover:shadow"
            >
              <Mail size={16} />
              Email
            </button>
            <button
              onClick={() => handleShare('sms')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-400 text-white hover:bg-emerald-300 transition-colors text-sm font-medium shadow-sm hover:shadow"
            >
              <MessageSquare size={16} />
              SMS
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShareModal;