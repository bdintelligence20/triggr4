// Demo data for development and testing

export interface Hub {
  id: number;
  name: string;
  description: string;
  members: number;
  documents: number;
  createdAt: string;
  updatedAt: string;
}

export const demoHubs: Hub[] = [
  {
    id: 1,
    name: 'Customer Service Hub',
    description: 'Knowledge base for customer service representatives',
    members: 15,
    documents: 120,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-03-10T14:45:00Z'
  },
  {
    id: 2,
    name: 'HR Hub',
    description: 'Human resources policies and procedures',
    members: 8,
    documents: 75,
    createdAt: '2024-02-01T09:15:00Z',
    updatedAt: '2024-03-05T11:20:00Z'
  },
  {
    id: 3,
    name: 'Marketing Hub',
    description: 'Marketing materials and brand guidelines',
    members: 12,
    documents: 95,
    createdAt: '2024-01-20T13:45:00Z',
    updatedAt: '2024-03-12T16:30:00Z'
  },
  {
    id: 4,
    name: 'Product Hub',
    description: 'Product documentation and specifications',
    members: 20,
    documents: 150,
    createdAt: '2023-12-10T08:00:00Z',
    updatedAt: '2024-03-15T10:15:00Z'
  }
];

export interface LibraryItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  fileType?: string;
  size?: string;
  owner: string;
  lastModified: string;
  items?: number;
}

export const libraryItems: LibraryItem[] = [
  {
    id: '1',
    name: 'Customer Service Handbook',
    type: 'file',
    fileType: 'pdf',
    size: '2.5 MB',
    owner: 'John Smith',
    lastModified: '2024-03-10T14:30:00Z'
  },
  {
    id: '2',
    name: 'Product Documentation',
    type: 'folder',
    owner: 'Sarah Johnson',
    lastModified: '2024-03-05T09:15:00Z',
    items: 15
  },
  {
    id: '3',
    name: 'Onboarding Materials',
    type: 'folder',
    owner: 'Michael Brown',
    lastModified: '2024-02-28T11:45:00Z',
    items: 8
  },
  {
    id: '4',
    name: 'Company Policies',
    type: 'file',
    fileType: 'docx',
    size: '1.2 MB',
    owner: 'Emily Davis',
    lastModified: '2024-03-12T16:20:00Z'
  },
  {
    id: '5',
    name: 'Training Videos',
    type: 'folder',
    owner: 'David Wilson',
    lastModified: '2024-03-01T13:10:00Z',
    items: 6
  }
];
