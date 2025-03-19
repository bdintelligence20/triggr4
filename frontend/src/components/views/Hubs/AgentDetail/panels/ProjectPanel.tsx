import React from 'react';
import { Trello, Clock, Users } from 'lucide-react';

const ProjectPanel = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold mb-6">Project Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <Trello className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Task Board</h3>
          <p className="text-gray-500 mt-2">View and manage project tasks</p>
        </button>

        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <Clock className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Timeline</h3>
          <p className="text-gray-500 mt-2">Track project milestones and deadlines</p>
        </button>

        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <Users className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Team</h3>
          <p className="text-gray-500 mt-2">Manage team members and assignments</p>
        </button>
      </div>
    </div>
  );
};

export default ProjectPanel;