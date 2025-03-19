import { create } from 'zustand';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'issue' | 'report' | 'announcement' | 'general';
  timestamp: string;
  read: boolean;
  allowedRoles: string[];
}

interface NotificationStore {
  notifications: Notification[];
  addNotification: (notification: Notification) => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

// Demo notifications
const demoNotifications: Notification[] = [
  {
    id: '1',
    title: 'New Support Ticket',
    message: 'A new support ticket has been created for the Customer Service Hub.',
    type: 'issue',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
    read: false,
    allowedRoles: ['super_admin', 'hub_admin', 'user']
  },
  {
    id: '2',
    title: 'Monthly Report Available',
    message: 'The monthly usage report for March is now available for download.',
    type: 'report',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    read: false,
    allowedRoles: ['super_admin', 'hub_admin']
  },
  {
    id: '3',
    title: 'System Maintenance',
    message: 'Scheduled maintenance will occur on Sunday at 2:00 AM. The system may be unavailable for up to 2 hours.',
    type: 'announcement',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // 5 hours ago
    read: true,
    allowedRoles: ['super_admin', 'hub_admin', 'user']
  },
  {
    id: '4',
    title: 'New Feature Released',
    message: 'We\'ve added a new AI-powered search feature to help you find information faster.',
    type: 'announcement',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
    read: false,
    allowedRoles: ['super_admin', 'hub_admin', 'user']
  },
  {
    id: '5',
    title: 'User Access Request',
    message: 'John Smith has requested access to the HR Hub. Please review and approve.',
    type: 'issue',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(), // 1.5 days ago
    read: false,
    allowedRoles: ['super_admin', 'hub_admin']
  },
  {
    id: '6',
    title: 'Document Upload Complete',
    message: 'Your batch upload of 15 documents has completed successfully.',
    type: 'general',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(), // 2 days ago
    read: true,
    allowedRoles: ['super_admin', 'hub_admin', 'user']
  }
];

const useNotificationStore = create<NotificationStore>((set: any) => ({
  notifications: demoNotifications,
  addNotification: (notification: Notification) => 
    set((state: NotificationStore) => ({ 
      notifications: [notification, ...state.notifications] 
    })),
  markAsRead: (id: string) => 
    set((state: NotificationStore) => ({
      notifications: state.notifications.map((notification: Notification) => 
        notification.id === id 
          ? { ...notification, read: true } 
          : notification
      )
    })),
  clearAll: () => set({ notifications: [] })
}));

export default useNotificationStore;
