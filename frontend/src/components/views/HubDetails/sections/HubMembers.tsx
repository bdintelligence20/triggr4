import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { UserPlus, Search, Mail, Edit2, Trash2 } from 'lucide-react';

interface HubMembersProps {
  hubId: number;
}

interface Member {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'pending';
  joinedDate: string;
}

const demoMembers: Member[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    email: 'sarah.chen@company.com',
    role: 'Hub Admin',
    status: 'active',
    joinedDate: '2024-01-15'
  },
  {
    id: '2',
    name: 'Michael Rodriguez',
    email: 'michael.r@company.com',
    role: 'Member',
    status: 'active',
    joinedDate: '2024-01-20'
  },
  {
    id: '3',
    name: 'Emma Williams',
    email: 'emma.w@company.com',
    role: 'Member',
    status: 'pending',
    joinedDate: '2024-02-01'
  }
];

const HubMembers: React.FC<HubMembersProps> = ({ hubId }) => {
  const [members] = useState<Member[]>(demoMembers);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredMembers = members.filter(member =>
    member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Hub Members</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300">
          <UserPlus size={20} />
          Add Member
        </button>
      </div>

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
          {filteredMembers.map((member) => (
            <motion.div
              key={member.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 hover:bg-gray-50"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                    <span className="text-emerald-600 font-medium">
                      {member.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-medium">{member.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Mail size={14} className="text-gray-400" />
                      <span className="text-sm text-gray-500">{member.email}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      member.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {member.status}
                    </span>
                    <p className="text-sm text-gray-500 mt-1">
                      Joined {new Date(member.joinedDate).toLocaleDateString()}
                    </p>
                  </div>
                  <select
                    value={member.role}
                    onChange={() => {}}
                    className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
                  >
                    <option value="admin">Hub Admin</option>
                    <option value="member">Member</option>
                  </select>
                  <div className="flex items-center gap-2">
                    <button className="p-2 text-gray-400 hover:text-emerald-400 hover:bg-emerald-50 rounded-lg">
                      <Edit2 size={16} />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-50 rounded-lg">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HubMembers;