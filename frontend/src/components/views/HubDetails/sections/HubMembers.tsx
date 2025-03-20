import React, { useState, useEffect } from 'react';
import { UserPlus, Search, Mail, Edit2, Trash2, Phone, Briefcase } from 'lucide-react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useAppContext } from '../../../../contexts/AppContext';
import ManageMembersModal from '../ManageMembersModal';
import * as api from '../../../../services/api';

interface HubMembersProps {
  hubId: number;
}

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
  createdAt?: any;
}

const HubMembers: React.FC<HubMembersProps> = ({ hubId }) => {
  const { user } = useAuth();
  const { showNotification } = useAppContext() as { 
    showNotification: (message: string, type?: 'success' | 'error' | 'info') => void 
  };
  const [members, setMembers] = useState<Member[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isManageMembersModalOpen, setIsManageMembersModalOpen] = useState(false);

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
      showNotification('Failed to fetch members', 'error');
    } finally {
      setIsLoading(false);
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

  const handleDeleteMember = async (memberId: string) => {
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
    member.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.phone?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.position?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (timestamp: any) => {
    if (!timestamp) return 'N/A';
    
    try {
      // If it's a Firestore timestamp
      if (timestamp.toDate) {
        return timestamp.toDate().toLocaleDateString();
      }
      
      // If it's a string or number
      return new Date(timestamp).toLocaleDateString();
    } catch (err) {
      return 'N/A';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Hub Members</h2>
        <button 
          onClick={() => setIsManageMembersModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600"
        >
          <UserPlus size={20} />
          Add Member
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-emerald-500 border-t-transparent"></div>
          <p className="mt-2 text-gray-600">Loading members...</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {/* Search Bar */}
          <div className="p-4 border-b">
            <div className="relative">
              <input
                type="text"
                placeholder="Search members..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            </div>
          </div>

          {/* Members List */}
          <div className="divide-y">
            {filteredMembers.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No members found. Add your first member using the "Add Member" button.
              </div>
            ) : (
              filteredMembers.map((member) => (
                <div
                  key={member.id}
                  className="p-4 hover:bg-gray-50"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between">
                    <div className="flex items-center gap-4 mb-3 sm:mb-0">
                      <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                        <span className="text-emerald-600 font-medium">
                          {member.name?.split(' ').map(n => n?.[0] || '').join('') || '?'}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-medium">{member.name}</h3>
                        <div className="flex flex-col xs:flex-row xs:items-center gap-2 mt-1">
                          <div className="flex items-center gap-1">
                            <Mail size={14} className="text-gray-400" />
                            <span className="text-sm text-gray-500">{member.email}</span>
                          </div>
                          {member.phone && (
                            <div className="flex items-center gap-1 ml-0 xs:ml-3">
                              <Phone size={14} className="text-gray-400" />
                              <span className="text-sm text-gray-500">{member.phone}</span>
                            </div>
                          )}
                        </div>
                        {member.position && (
                          <div className="flex items-center gap-1 mt-1">
                            <Briefcase size={14} className="text-gray-400" />
                            <span className="text-sm text-gray-500">{member.position}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                      <div>
                        <div className="flex flex-wrap gap-1">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            member.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {member.status}
                          </span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            member.whatsappVerified
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {member.whatsappVerified ? 'WhatsApp Verified' : 'WhatsApp Pending'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Joined {formatDate(member.createdAt)}
                        </p>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        {!member.whatsappVerified && (
                          <button
                            onClick={() => handleVerifyWhatsApp(member.id)}
                            className="px-2 py-1 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                          >
                            Verify WhatsApp
                          </button>
                        )}
                        <select
                          value={member.role}
                          onChange={(e) => handleRoleChange(member.id, e.target.value)}
                          className="px-2 py-1 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                        >
                          <option value="viewer">Viewer</option>
                          <option value="contributor">Contributor</option>
                          <option value="manager">Manager</option>
                        </select>
                        <button
                          onClick={() => handleDeleteMember(member.id)}
                          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <ManageMembersModal
        isOpen={isManageMembersModalOpen}
        onClose={() => {
          setIsManageMembersModalOpen(false);
          fetchMembers(); // Refresh the members list after closing the modal
        }}
        hubName={user?.organizationName || 'Knowledge Hub'}
      />
    </div>
  );
};

export default HubMembers;
