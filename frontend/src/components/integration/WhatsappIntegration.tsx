// components/integration/WhatsAppIntegration.tsx
import React from 'react';
import { Copy, Mail, Phone, Share2 } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import WhatsAppIcon from '../icons/WhatsAppIcon';

const WhatsAppIntegration: React.FC = () => {
  const { 
    whatsappNumber,
    setWhatsappNumber,
    showShareOptions,
    setShowShareOptions,
    chatCategory,
    categories,
    setCategories,
    showNotification
  } = useAppContext();

  // Generate a WhatsApp number
  const generateWhatsappNumber = () => {
    // Use the fixed WhatsApp number since that's the only working one
    const number = "+15055787929";
    setWhatsappNumber(number);
    setShowShareOptions(true);
  
    // Update categories with the WhatsApp number if a category is selected
    if (chatCategory && chatCategory !== 'all') {
      setCategories(categories.map(category => 
        category.id === chatCategory 
          ? { ...category, whatsappNumber: number } 
          : category
      ));
    }
    
    // Show notification
    showNotification("WhatsApp number generated");
  };

  // Copy WhatsApp number to clipboard
  const copyToClipboard = () => {
    if (whatsappNumber) {
      navigator.clipboard.writeText(whatsappNumber);
      showNotification("Number copied to clipboard");
    }
  };

  // Share number via different methods
  const shareVia = (method: string) => {
    if (!whatsappNumber) return;
    
    let shareUrl = '';
    // Prepend the sandbox code "join wife-universe - " to the message
    const message = `join wife-universe - Here's the WhatsApp number for the HR HUB: ${whatsappNumber}`;
    
    switch (method) {
      case 'whatsapp':
        shareUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
        break;
      case 'email':
        shareUrl = `mailto:?subject=Knowledge%20Base%20WhatsApp%20Number&body=${encodeURIComponent(message)}`;
        break;
      case 'sms':
        shareUrl = `sms:?body=${encodeURIComponent(message)}`;
        break;
      default:
        return;
    }
    
    window.open(shareUrl, '_blank');
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <div className="bg-emerald-50 dark:bg-emerald-900/20 p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="font-medium text-gray-900 dark:text-white text-lg flex items-center">
          <WhatsAppIcon className="mr-2" size={20} />
          WhatsApp Integration
        </h3>
      </div>
      
      <div className="p-6">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Generate a WhatsApp number to connect with your knowledge base and share it with your team or customers.
        </p>
        
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6 text-sm">
          <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">New: Enhanced WhatsApp Integration</h4>
          <p className="text-gray-600 dark:text-gray-400 mb-2">
            We've upgraded our WhatsApp integration with two key improvements:
          </p>
          
          <h5 className="font-medium text-blue-600 dark:text-blue-400 mt-3 mb-1">1. SMS Verification</h5>
          <p className="text-gray-600 dark:text-gray-400 mb-2">
            Members now verify their accounts via SMS for improved reliability:
          </p>
          <ul className="list-disc pl-5 text-gray-600 dark:text-gray-400 mb-2">
            <li>Higher verification success rate</li>
            <li>Simplified user experience</li>
            <li>Members receive a verification code via SMS</li>
            <li>They send the code to the WhatsApp number to complete verification</li>
          </ul>
          
          <h5 className="font-medium text-blue-600 dark:text-blue-400 mt-3 mb-1">2. Conversations API</h5>
          <p className="text-gray-600 dark:text-gray-400 mb-2">
            We now use Twilio Conversations API for improved messaging:
          </p>
          <ul className="list-disc pl-5 text-gray-600 dark:text-gray-400 mb-2">
            <li>More reliable message delivery</li>
            <li>Better handling of markdown and special characters</li>
            <li>Improved conversation history</li>
          </ul>
          
          <p className="text-gray-600 dark:text-gray-400 mt-3 mb-2">
            <strong>Setup Instructions:</strong> Configure your Twilio account to use the correct webhook:
          </p>
          <ol className="list-decimal pl-5 text-gray-600 dark:text-gray-400">
            <li>Go to Twilio Console &gt; Messaging &gt; Settings &gt; WhatsApp Sandbox</li>
            <li>Set the webhook URL to: <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">https://triggr4bg.onrender.com/webhook</code></li>
            <li>Ensure "When a message comes in" is set to this URL</li>
          </ol>
        </div>
        
        {whatsappNumber ? (
          <div className="mb-6">
            <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-lg mb-4">
              <span className="font-medium text-gray-900 dark:text-white">{whatsappNumber}</span>
              <button 
                onClick={copyToClipboard}
                className="text-emerald-500 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300"
              >
                <Copy size={18} />
              </button>
            </div>
            
            {showShareOptions && (
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">Share via:</p>
                <div className="flex space-x-4">
                  <button 
                    onClick={() => shareVia('whatsapp')}
                    className="flex flex-col items-center justify-center text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400"
                  >
                    <WhatsAppIcon size={24} className="mb-1" />
                    <span className="text-xs">WhatsApp</span>
                  </button>
                  
                  <button 
                    onClick={() => shareVia('email')}
                    className="flex flex-col items-center justify-center text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400"
                  >
                    <Mail size={24} className="mb-1" />
                    <span className="text-xs">Email</span>
                  </button>
                  
                  <button 
                    onClick={() => shareVia('sms')}
                    className="flex flex-col items-center justify-center text-gray-700 dark:text-gray-300 hover:text-emerald-500 dark:hover:text-emerald-400"
                  >
                    <Phone size={24} className="mb-1" />
                    <span className="text-xs">Text</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <button 
            onClick={generateWhatsappNumber}
            className="w-full flex items-center justify-center px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors"
          >
            <WhatsAppIcon size={18} className="mr-2" />
            <span>Generate WhatsApp Number</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default WhatsAppIntegration;
