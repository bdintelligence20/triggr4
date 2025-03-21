import React, { useState, useEffect } from 'react';
import { X, Search, Mail, Plus, Trash2, Phone, Briefcase, User } from 'lucide-react';
import { useAuth } from '../../../contexts/AuthContext';
import { useAppContext } from '../../../contexts/AppContext';
import * as api from '../../../services/api';

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

interface ManageMembersModalProps {
  isOpen: boolean;
  onClose: () => void;
  hubName: string;
}

const ManageMembersModal: React.FC<ManageMembersModalProps> = ({ isOpen, onClose, hubName }) => {
  const { user } = useAuth();
  const { showNotification } = useAppContext() as { 
    showNotification: (message: string, type?: 'success' | 'error' | 'info') => void 
  };
  const [members, setMembers] = useState<Member[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [emailInput, setEmailInput] = useState('');
  const [nameInput, setNameInput] = useState('');
  const [phoneInput, setPhoneInput] = useState('');
  const [positionInput, setPositionInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Log user information for debugging
    console.log('User object:', user);
    console.log('User organizationId:', user?.organizationId);
    
    // Check if auth token is present in localStorage
    const token = localStorage.getItem('auth_token');
    console.log('Auth token in localStorage:', token ? 'Present' : 'Not present');
    
    if (isOpen) {
      if (user?.organizationId) {
        // Check API health first
        checkApiHealth();
        fetchMembers();
      } else {
        console.error('User does not have an organizationId:', user);
        setError('User does not belong to an organization. Please contact support.');
      }
    }
  }, [isOpen, user?.organizationId]);

  const checkApiHealth = async () => {
    try {
      console.log('Checking API health...');
      const response = await api.checkHealth();
      console.log('API health check response:', response);
      
      if (response.error) {
        console.error('API health check failed:', response.error);
        setError(`API connection issue: ${response.error}`);
      } else {
        console.log('API health check successful:', response.data);
      }
    } catch (err) {
      console.error('Error checking API health:', err);
      setError('Failed to connect to the API. Please try again later.');
    }
  };

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

  if (!isOpen) return null;

  // Helper function to validate phone number format
  const isValidPhoneNumber = (phone: string): boolean => {
    // Check if the phone number starts with + and has at least 8 digits
    const phoneRegex = /^\+\d{1,3}\d{6,14}$/;
    return phoneRegex.test(phone);
  };

  const handleAddMember = async () => {
    console.log('Add Member button clicked');
    
    if (!user?.organizationId) {
      showNotification('Organization ID is required to add members', 'error');
      console.log('No organization ID found');
      return;
    }
    
    if (!emailInput) {
      showNotification('Email is required', 'error');
      console.log('Email is required');
      return;
    }
    
    if (!phoneInput) {
      showNotification('Phone number is required', 'error');
      console.log('Phone number is required');
      return;
    }
    
    // Validate phone number format
    if (!isValidPhoneNumber(phoneInput)) {
      showNotification('Phone number must be in international format with + prefix (e.g., +27123456789)', 'error');
      console.log('Invalid phone number format');
      return;
    }
    
    if (members.find(m => m.email === emailInput)) {
      showNotification('A member with this email already exists', 'error');
      console.log('Email already exists');
      return;
    }
    
    if (members.find(m => m.phone === phoneInput)) {
      showNotification('A member with this phone number already exists', 'error');
      console.log('Phone number already exists');
      return;
    }
    
    setIsLoading(true);
    console.log('Sending API request with data:', {
      name: nameInput,
      email: emailInput,
      phone: phoneInput,
      position: positionInput,
      role: 'viewer'
    });
    
    try {
      console.log('About to call API with data:', {
        name: nameInput,
        email: emailInput,
        phone: phoneInput,
        position: positionInput,
        role: 'viewer'
      });
      
      // Call the API to add a member
      const response = await api.addMember({
        name: nameInput,
        email: emailInput,
        phone: phoneInput,
        position: positionInput,
        role: 'viewer'
      });
      
      console.log('API response:', response);
      console.log('API response data:', response.data);
      console.log('API response status:', response.status);
      
      if (response.error) {
        console.error('API error:', response.error);
        throw new Error(response.error);
      }
      
      if (response.data) {
        // Add the new member to the local state
        // The response.data contains both memberId and member properties
        if (response.data.member) {
          setMembers([...members, response.data.member]);
          
          // Reset form inputs
          setNameInput('');
          setEmailInput('');
          setPhoneInput('');
          setPositionInput('');
          
          showNotification('Member added successfully', 'success');
          console.log('Member added successfully');
        } else {
          console.log('No member data in response:', response.data);
          // If for some reason the member property is missing, try to fetch members again
          fetchMembers();
        }
      } else {
        console.log('No data in response');
      }
    } catch (err) {
      showNotification(err instanceof Error ? err.message : 'Failed to add member', 'error');
      console.error('Error adding member:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (confirm('Are you sure you want to remove this member?')) {
      setIsLoading(true);
      
      try {
        // Call the API to delete a member
        const response = await api.deleteMember(memberId);
        
        if (response.error) {
          throw new Error(response.error);
        }
        
        // Remove the member from the local state
        setMembers(members.filter(m => m.id !== memberId));
        showNotification('Member removed successfully', 'success');
      } catch (err) {
        showNotification(err instanceof Error ? err.message : 'Failed to remove member', 'error');
        console.error('Error removing member:', err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleRoleChange = async (memberId: string, newRole: string) => {
    setIsLoading(true);
    
    try {
      // Call the API to update a member's role
      const response = await api.updateMember(memberId, { role: newRole });
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      // Update the member in the local state
      setMembers(members.map(m => 
        m.id === memberId ? { ...m, role: newRole } : m
      ));
      showNotification('Member role updated successfully', 'success');
    } catch (err) {
      showNotification(err instanceof Error ? err.message : 'Failed to update member role', 'error');
      console.error('Error updating member role:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyWhatsApp = async (memberId: string) => {
    setIsLoading(true);
    
    try {
      // Call the API to send a WhatsApp verification message
      const response = await api.sendWhatsAppVerification(memberId);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      showNotification('WhatsApp verification message sent', 'success');
    } catch (err) {
      showNotification(err instanceof Error ? err.message : 'Failed to send verification message', 'error');
      console.error('Error sending verification message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredMembers = members.filter(member => 
    member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.phone.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.position.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Manage Members - {hubName}</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Search Section */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search members..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          </div>

          {/* Add Member Form */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium mb-3">Add New Member</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="relative">
                <input
                  type="text"
                  value={nameInput}
                  onChange={(e) => setNameInput(e.target.value)}
                  placeholder="Full Name"
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                />
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              </div>
              <div className="relative">
                <input
                  type="email"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  placeholder="Email Address *"
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                  required
                />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              </div>
              <div className="relative">
                <input
                  type="tel"
                  value={phoneInput}
                  onChange={(e) => setPhoneInput(e.target.value)}
                  placeholder="Phone Number (with country code) *"
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                  required
                />
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <p className="text-xs text-gray-500 mt-1">Format: +[country code][number] (e.g., +27123456789)</p>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={positionInput}
                  onChange={(e) => setPositionInput(e.target.value)}
                  placeholder="Position/Title"
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                />
                <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              </div>
            </div>
            <button
              onClick={async (e) => {
                e.preventDefault();
                console.log('Add Member button clicked - event handler');
                alert('Add Member button clicked - This alert confirms the button is working');
                
                // Check if user has organizationId
                if (!user?.organizationId) {
                  console.error('No organization ID found in user object:', user);
                  showNotification('Organization ID is required to add members', 'error');
                  return;
                }
                
                // Check required fields
                if (!emailInput) {
                  console.error('Email is required');
                  showNotification('Email is required', 'error');
                  return;
                }
                
                if (!phoneInput) {
                  console.error('Phone number is required');
                  showNotification('Phone number is required', 'error');
                  return;
                }
                
                // Directly make the API call here to bypass any potential issues in handleAddMember
                try {
                  console.log('Making direct API call with data:', {
                    name: nameInput,
                    email: emailInput,
                    phone: phoneInput,
                    position: positionInput,
                    role: 'viewer'
                  });
                  
                  setIsLoading(true);
                  
                  // Call the API directly
                  const response = await api.addMember({
                    name: nameInput,
                    email: emailInput,
                    phone: phoneInput,
                    position: positionInput,
                    role: 'viewer'
                  });
                  
                  console.log('Direct API call response:', response);
                  
                  if (response.error) {
                    console.error('API error:', response.error);
                    showNotification(response.error, 'error');
                  } else if (response.data) {
                    console.log('API success, data:', response.data);
                    
                    if (response.data.member) {
                      // Add the new member to the local state
                      setMembers([...members, response.data.member]);
                      
                      // Reset form inputs
                      setNameInput('');
                      setEmailInput('');
                      setPhoneInput('');
                      setPositionInput('');
                      
                      showNotification('Member added successfully', 'success');
                      
                      // Refresh the members list
                      fetchMembers();
                    } else {
                      console.warn('No member data in response:', response.data);
                      // Refresh the members list anyway
                      fetchMembers();
                    }
                  }
                } catch (err) {
                  console.error('Error in direct API call:', err);
                  showNotification(err instanceof Error ? err.message : 'Failed to add member', 'error');
                } finally {
                  setIsLoading(false);
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600"
            >
              <Plus size={20} />
              Add Member
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Loading State */}
          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-emerald-500 border-t-transparent"></div>
              <p className="mt-2 text-gray-600">Loading members...</p>
            </div>
          ) : (
            /* Members List */
            <div className="border rounded-lg divide-y max-h-[400px] overflow-y-auto">
              {filteredMembers.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No members found. Add your first member above.
                </div>
              ) : (
                filteredMembers.map((member) => (
                  <div key={member.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between">
                    <div className="mb-3 sm:mb-0">
                      <div className="font-medium">{member.name}</div>
                      <div className="text-sm text-gray-500">{member.email}</div>
                      <div className="text-sm text-gray-500">{member.phone} • {member.position}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`inline-block px-2 py-0.5 text-xs rounded-full
                          ${member.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'}`}
                        >
                          {member.status}
                        </span>
                        <span className={`inline-block px-2 py-0.5 text-xs rounded-full
                          ${member.whatsappVerified ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'}`}
                        >
                          {member.whatsappVerified ? 'WhatsApp Verified' : 'WhatsApp Pending'}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      {!member.whatsappVerified && (
                        <button
                          onClick={() => handleVerifyWhatsApp(member.id)}
                          className="px-3 py-1 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                        >
                          Verify WhatsApp
                        </button>
                      )}
                      <select
                        value={member.role}
                        onChange={(e) => handleRoleChange(member.id, e.target.value)}
                        className="px-3 py-1.5 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="contributor">Contributor</option>
                        <option value="manager">Manager</option>
                      </select>
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="p-2 text-gray-400 hover:text-red-500"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-4 p-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ManageMembersModal;
