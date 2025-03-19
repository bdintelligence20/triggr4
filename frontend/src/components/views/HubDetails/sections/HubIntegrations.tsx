import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plug, Check, ExternalLink } from 'lucide-react';

interface HubIntegrationsProps {
  hubId: number;
}

const HubIntegrations: React.FC<HubIntegrationsProps> = ({ hubId }) => {
  const [connectedApps, setConnectedApps] = useState<string[]>([]);

  const getHubIntegrations = () => {
    // In a real app, this would be dynamic based on hub type
    const integrations = {
      1: [ // Customer Service Hub
        { id: 'zendesk', name: 'Zendesk', description: 'Customer support and ticketing' },
        { id: 'intercom', name: 'Intercom', description: 'Customer messaging platform' },
        { id: 'freshdesk', name: 'Freshdesk', description: 'Help desk software' }
      ],
      2: [ // HR Hub
        { id: 'bamboohr', name: 'BambooHR', description: 'HR management software' },
        { id: 'workday', name: 'Workday', description: 'HR and finance platform' },
        { id: 'greenhouse', name: 'Greenhouse', description: 'Recruitment software' }
      ],
      3: [ // Project Management Hub
        { id: 'jira', name: 'Jira', description: 'Project and issue tracking' },
        { id: 'asana', name: 'Asana', description: 'Project management tool' },
        { id: 'trello', name: 'Trello', description: 'Task management platform' }
      ],
      4: [ // QHSE Hub
        { id: 'ehsai', name: 'EHS.ai', description: 'Environmental health and safety' },
        { id: 'enablon', name: 'Enablon', description: 'QHSE management software' },
        { id: 'intelex', name: 'Intelex', description: 'Quality and compliance platform' }
      ]
    };
    return integrations[hubId as keyof typeof integrations] || integrations[1];
  };

  const handleConnect = (appId: string) => {
    if (connectedApps.includes(appId)) {
      setConnectedApps(prev => prev.filter(id => id !== appId));
    } else {
      setConnectedApps(prev => [...prev, appId]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Integrations</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {getHubIntegrations().map((app) => (
          <motion.div
            key={app.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-emerald-50 rounded-lg">
                  <Plug className="text-emerald-400" size={24} />
                </div>
                <div>
                  <h3 className="font-medium">{app.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{app.description}</p>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={() => handleConnect(app.id)}
                className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  connectedApps.includes(app.id)
                    ? 'bg-emerald-100 text-emerald-600'
                    : 'bg-emerald-400 text-white hover:bg-emerald-300'
                }`}
              >
                {connectedApps.includes(app.id) ? (
                  <>
                    <Check size={20} />
                    Connected
                  </>
                ) : (
                  <>
                    <ExternalLink size={20} />
                    Connect
                  </>
                )}
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default HubIntegrations;