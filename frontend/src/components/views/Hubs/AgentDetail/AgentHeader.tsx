import React from 'react';
import { ArrowLeft, MessageSquare, Mail, Bell, Settings } from 'lucide-react';

interface AgentHeaderProps {
  agentId: number;
  onBack: () => void;
}

const AgentHeader: React.FC<AgentHeaderProps> = ({ agentId, onBack }) => {
  const getAgentInfo = () => {
    const agents = {
      1: {
        name: 'Customer Service Hub',
        description: 'Manage client relationships and support',
        image: 'https://images.unsplash.com/photo-1664575602276-acd073f104c1?q=80&w=2070&auto=format&fit=crop'
      },
      2: {
        name: 'HR Hub',
        description: 'Handle employee management and HR processes',
        image: 'https://images.unsplash.com/photo-1542744094-24638eff58bb?q=80&w=2070&auto=format&fit=crop'
      },
      3: {
        name: 'Project Management Hub',
        description: 'Oversee project planning and execution',
        image: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=2070&auto=format&fit=crop'
      },
      4: {
        name: 'QHSE Hub',
        description: 'Monitor quality, health, safety, and environmental compliance',
        image: 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?q=80&w=2070&auto=format&fit=crop'
      }
    };
    return agents[agentId as keyof typeof agents] || agents[1];
  };

  const agent = getAgentInfo();

  return (
    <div className="relative mb-8">
      <div className="absolute inset-0 h-48">
        <img 
          src={agent.image}
          alt={agent.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 to-transparent" />
      </div>
      
      <div className="relative pt-8 pb-4">
        <div className="max-w-7xl mx-auto px-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <button
                  onClick={onBack}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <ArrowLeft size={20} />
                </button>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{agent.name}</h1>
                  <p className="text-sm text-gray-500 mt-1.5">{agent.description}</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                  <MessageSquare size={18} />
                  <span className="hidden sm:inline font-medium">Send Message</span>
                </button>
                
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                  <Mail size={18} />
                  <span className="hidden sm:inline font-medium">Send Email</span>
                </button>
                
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                  <Bell size={18} />
                  <span className="hidden sm:inline font-medium">Send Notification</span>
                </button>

                <div className="w-px h-8 bg-gray-200 mx-1 hidden sm:block"></div>

                <button 
                  className="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                  aria-label="Hub Settings"
                >
                  <Settings size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentHeader;