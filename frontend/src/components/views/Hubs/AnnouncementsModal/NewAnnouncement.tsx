import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bold, Italic, List, Link as LinkIcon, Paperclip, Calendar, Apple as WhatsApp, Mail, Bell, Upload, X, Loader } from 'lucide-react';
import { Button } from '../../../ui/Button';
import useRoleStore from '../../../../store/roleStore';
import { demoHubs } from '../../../data/demo-data';
import * as api from '../../../../services/api';
import { useAuth } from '../../../../contexts/AuthContext';
import { useAppContext } from '../../../../contexts/AppContext';

interface Member {
  id: string;
  name: string;
  email: string;
  phone: string;
  position: string;
  role: string;
  status: 'active' | 'pending';
  organizationId: string;
  whatsappVerified: boolean;
}

const NewAnnouncement = () => {
  const { currentRole } = useRoleStore();
  const { user } = useAuth();
  const { showNotification } = useAppContext();
  const [members, setMembers] = useState<Member[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    selectedHubs: [] as string[],
    deliveryMethods: {
      whatsapp: true,
      email: true,
      inApp: true
    },
    scheduledDate: '',
    attachments: [] as File[]
  });

  const handleAttachmentUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData(prev => ({
        ...prev,
        attachments: [...prev.attachments, ...Array.from(e.target.files!)]
      }));
    }
  };

  const removeAttachment = (index: number) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  const toggleDeliveryMethod = (method: keyof typeof formData.deliveryMethods) => {
    setFormData(prev => ({
      ...prev,
      deliveryMethods: {
        ...prev.deliveryMethods,
        [method]: !prev.deliveryMethods[method]
      }
    }));
  };

  useEffect(() => {
    fetchMembers();
  }, []);

  const fetchMembers = async () => {
    if (!user?.organizationId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Call the API to fetch members
      const response = await api.getMembers();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      if (response.data && response.data.members) {
        setMembers(response.data.members);
      } else {
        setMembers([]);
      }
    } catch (err) {
      setError('Failed to fetch members. Please try again.');
      console.error('Error fetching members:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.message.trim()) {
      showNotification('Please enter a message', 'error');
      return;
    }
    
    setIsSending(true);
    setError(null);
    
    try {
      // Get selected member IDs
      const selectedMemberIds = members
        .filter(member => 
          member.whatsappVerified && 
          (formData.selectedHubs.length === 0 || 
           formData.selectedHubs.includes(member.id))
        )
        .map(member => member.id);
      
      if (selectedMemberIds.length === 0) {
        showNotification('No verified WhatsApp members found to send to', 'error');
        setIsSending(false);
        return;
      }
      
      // Call the API to send the bulk message
      const response = await api.sendBulkWhatsAppMessage({
        title: formData.title,
        message: formData.message,
        memberIds: selectedMemberIds,
        sendEmail: formData.deliveryMethods.email,
        sendInApp: formData.deliveryMethods.inApp,
        scheduledFor: formData.scheduledDate || undefined
      });
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      // Show success notification
      showNotification(`Message sent to ${response.data?.successCount || 0} members`);
      
      // Reset form
      setFormData({
        title: '',
        message: '',
        selectedHubs: [],
        deliveryMethods: {
          whatsapp: true,
          email: true,
          inApp: true
        },
        scheduledDate: '',
        attachments: []
      });
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      showNotification('Failed to send message', 'error');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="p-6"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Announcement Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            placeholder="Enter announcement title..."
            required
          />
        </div>

        {/* Rich Text Editor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Message
          </label>
          <div className="border rounded-lg overflow-hidden">
            <div className="flex items-center gap-2 p-2 border-b bg-gray-50">
              <button
                type="button"
                className="p-1.5 hover:bg-gray-200 rounded"
                title="Bold"
              >
                <Bold size={16} />
              </button>
              <button
                type="button"
                className="p-1.5 hover:bg-gray-200 rounded"
                title="Italic"
              >
                <Italic size={16} />
              </button>
              <button
                type="button"
                className="p-1.5 hover:bg-gray-200 rounded"
                title="Bullet List"
              >
                <List size={16} />
              </button>
              <button
                type="button"
                className="p-1.5 hover:bg-gray-200 rounded"
                title="Add Link"
              >
                <LinkIcon size={16} />
              </button>
            </div>
            <textarea
              value={formData.message}
              onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
              className="w-full px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
              rows={6}
              placeholder="Type your announcement message..."
              required
            />
          </div>
        </div>

          {/* Member Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recipients
            </label>
            <div className="border rounded-lg p-4 max-h-60 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader className="animate-spin text-emerald-500 mr-2" size={20} />
                  <span className="text-gray-500">Loading members...</span>
                </div>
              ) : members.length === 0 ? (
                <div className="text-center py-4 text-gray-500">
                  No members found
                </div>
              ) : (
                <div className="space-y-2">
                  <label className="flex items-center gap-2 pb-2 border-b border-gray-200">
                    <input
                      type="checkbox"
                      checked={formData.selectedHubs.length === 0}
                      onChange={() => {
                        setFormData(prev => ({ 
                          ...prev, 
                          selectedHubs: prev.selectedHubs.length > 0 ? [] : members.map(m => m.id)
                        }));
                      }}
                      className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400"
                    />
                    <span className="text-sm font-medium text-gray-700">All Members</span>
                    <span className="text-xs text-gray-500 ml-2">
                      ({members.filter(m => m.whatsappVerified).length} WhatsApp verified)
                    </span>
                  </label>
                  
                  {members.map(member => (
                    <label key={member.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.selectedHubs.length === 0 || formData.selectedHubs.includes(member.id)}
                        onChange={(e) => {
                          const memberId = member.id;
                          const newHubs = e.target.checked
                            ? [...formData.selectedHubs, memberId]
                            : formData.selectedHubs.filter(id => id !== memberId);
                          setFormData(prev => ({ ...prev, selectedHubs: newHubs }));
                        }}
                        disabled={!member.whatsappVerified}
                        className="w-4 h-4 text-emerald-400 border-gray-300 rounded focus:ring-emerald-400 disabled:opacity-50"
                      />
                      <span className={`text-sm ${!member.whatsappVerified ? 'text-gray-400' : 'text-gray-700'}`}>
                        {member.name}
                      </span>
                      {!member.whatsappVerified && (
                        <span className="text-xs text-red-500 ml-2">(Not WhatsApp verified)</span>
                      )}
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

        {/* Delivery Methods */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Delivery Methods
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => toggleDeliveryMethod('whatsapp')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                formData.deliveryMethods.whatsapp
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              <WhatsApp size={18} />
              WhatsApp
            </button>
            <button
              type="button"
              onClick={() => toggleDeliveryMethod('email')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                formData.deliveryMethods.email
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              <Mail size={18} />
              Email
            </button>
            <button
              type="button"
              onClick={() => toggleDeliveryMethod('inApp')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                formData.deliveryMethods.inApp
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              <Bell size={18} />
              In-App
            </button>
          </div>
        </div>

        {/* Attachments */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attachments
          </label>
          <div className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-4">
              <input
                type="file"
                multiple
                onChange={handleAttachmentUpload}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="flex flex-col items-center gap-2 cursor-pointer"
              >
                <Upload className="text-gray-400" size={24} />
                <span className="text-sm text-gray-500">
                  Click to upload or drag and drop
                </span>
              </label>
            </div>
            {formData.attachments.length > 0 && (
              <div className="space-y-2">
                {formData.attachments.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      <Paperclip size={16} className="text-gray-400" />
                      <span className="text-sm">{file.name}</span>
                      <span className="text-xs text-gray-500">
                        ({(file.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeAttachment(index)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-50 text-red-600 rounded-lg">
            {error}
          </div>
        )}

        {/* Schedule */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Schedule Delivery
          </label>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <input
                type="datetime-local"
                value={formData.scheduledDate}
                onChange={(e) => setFormData(prev => ({ ...prev, scheduledDate: e.target.value }))}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            </div>
            <span className="text-sm text-gray-500">or</span>
            <Button
              type="submit"
              className="flex-shrink-0"
              disabled={isSending}
            >
              {isSending ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Sending...
                </>
              ) : (
                'Send Now'
              )}
            </Button>
          </div>
        </div>
      </form>
    </motion.div>
  );
};

export default NewAnnouncement;
