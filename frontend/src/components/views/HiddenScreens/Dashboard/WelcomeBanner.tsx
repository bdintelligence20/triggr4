import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, ChevronDown } from 'lucide-react';
import useRoleStore from '../../../../store/roleStore';
import useHubStore from '../../../../store/hubStore';
import { demoHubs } from '../../../data/demo-data';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import * as Tooltip from '@radix-ui/react-tooltip';

const WelcomeBanner = () => {
  const { currentRole } = useRoleStore();
  const { selectedHubId, setSelectedHub } = useHubStore();
  
  const today = new Date().toLocaleDateString('en-US', { 
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const getRoleTitle = () => {
    switch (currentRole) {
      case 'super_admin':
        return 'Super Administrator';
      case 'hub_admin':
        return 'Hub Administrator';
      case 'user':
        return 'General User';
      default:
        return 'Welcome';
    }
  };

  const getAvailableHubs = () => {
    if (currentRole === 'super_admin') {
      return demoHubs;
    } else if (currentRole === 'hub_admin') {
      // In a real app, this would filter based on the admin's assigned hubs
      return demoHubs.filter(hub => ['Customer Service Hub', 'HR Hub'].includes(hub.name));
    }
    return [];
  };

  const selectedHub = demoHubs.find(hub => hub.id === selectedHubId);
  const availableHubs = getAvailableHubs();
  const showHubSelector = currentRole === 'super_admin' || currentRole === 'hub_admin';

  return (
    <div className="bg-white border-b">
      <div className="max-w-[1920px] mx-auto px-6 py-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex-1 min-w-0"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center p-3">
                <span className="text-sm font-bold text-emerald-400">Logo</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 leading-tight truncate">
                  Welcome, {getRoleTitle()}
                </h1>
                <div className="flex items-center gap-4 text-gray-500 mt-2">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} />
                    <span>{today}</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {showHubSelector && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Tooltip.Provider>
                <DropdownMenu.Root>
                  <Tooltip.Root>
                    <Tooltip.Trigger asChild>
                      <DropdownMenu.Trigger asChild>
                        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                          <span className="text-sm font-medium">
                            {selectedHub ? selectedHub.name : 'All Hubs'}
                          </span>
                          <ChevronDown size={16} />
                        </button>
                      </DropdownMenu.Trigger>
                    </Tooltip.Trigger>
                    <Tooltip.Portal>
                      <Tooltip.Content
                        className="bg-gray-900 text-white px-3 py-1.5 rounded text-sm"
                        sideOffset={5}
                      >
                        Switch Hub View
                      </Tooltip.Content>
                    </Tooltip.Portal>
                  </Tooltip.Root>

                  <DropdownMenu.Portal>
                    <DropdownMenu.Content
                      className="min-w-[220px] bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50"
                      sideOffset={5}
                    >
                      <DropdownMenu.Item
                        className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer outline-none"
                        onSelect={() => setSelectedHub(null)}
                      >
                        All Hubs
                      </DropdownMenu.Item>
                      <DropdownMenu.Separator className="h-px bg-gray-200 my-1" />
                      {availableHubs.map(hub => (
                        <DropdownMenu.Item
                          key={hub.id}
                          className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer outline-none"
                          onSelect={() => setSelectedHub(hub.id)}
                        >
                          {hub.name}
                        </DropdownMenu.Item>
                      ))}
                    </DropdownMenu.Content>
                  </DropdownMenu.Portal>
                </DropdownMenu.Root>
              </Tooltip.Provider>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WelcomeBanner;