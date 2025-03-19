import React from 'react';
import { Users, UserPlus, Mail, Share2 } from 'lucide-react';

const Teams: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-medium">Team Collaboration</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300">
          <UserPlus size={18} />
          <span>Invite Team</span>
        </button>
      </div>
      
      <div className="mb-8">
        <h3 className="text-sm font-medium text-gray-500 mb-3">Active Team Members</h3>
        <div className="space-y-3">
          {/* Team Member Row */}
          <div className="flex items-center justify-between p-3 border border-gray-100 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                <span className="text-emerald-600 font-medium">JS</span>
              </div>
              <div>
                <p className="font-medium">John Smith</p>
                <p className="text-sm text-gray-500">john.smith@example.com</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-emerald-100 text-emerald-600 text-xs rounded-full">Admin</span>
              <button className="p-2 text-gray-400 hover:text-emerald-500">
                <Mail size={18} />
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-3 border border-gray-100 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-medium">SD</span>
              </div>
              <div>
                <p className="font-medium">Sarah Davis</p>
                <p className="text-sm text-gray-500">sarah.davis@example.com</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">Member</span>
              <button className="p-2 text-gray-400 hover:text-emerald-500">
                <Mail size={18} />
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-3 border border-gray-100 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-medium">MJ</span>
              </div>
              <div>
                <p className="font-medium">Michael Johnson</p>
                <p className="text-sm text-gray-500">michael.j@example.com</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">Member</span>
              <button className="p-2 text-gray-400 hover:text-emerald-500">
                <Mail size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mb-8">
        <h3 className="text-sm font-medium text-gray-500 mb-3">Pending Invitations</h3>
        <div className="p-4 border border-dashed border-gray-200 rounded-lg text-center">
          <p className="text-gray-500">No pending invitations</p>
        </div>
      </div>
      
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div className="flex items-center gap-3 mb-3">
          <Share2 className="text-emerald-500" size={20} />
          <h3 className="font-medium">Share Knowledge Base</h3>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Invite others to collaborate on your knowledge base. They'll be able to view, add, and edit content.
        </p>
        <div className="flex gap-2">
          <input
            type="email"
            placeholder="Enter email address"
            className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          />
          <button className="px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300">
            Invite
          </button>
        </div>
      </div>
    </div>
  );
};

export default Teams;
