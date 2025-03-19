import React from 'react';
import { Edit2, Trash2, MessageSquare, Phone, Mail, MapPin } from 'lucide-react';

interface Client {
  id: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  type: 'client' | 'supplier';
  status: 'active' | 'inactive';
  lastContact: string;
}

interface ClientListProps {
  type: 'clients' | 'suppliers';
  searchQuery: string;
}

const demoClients: Client[] = [
  {
    id: '1',
    name: 'Acme Corporation',
    email: 'contact@acme.com',
    phone: '+1 (555) 123-4567',
    address: '123 Business Ave, Suite 100, New York, NY 10001',
    type: 'client',
    status: 'active',
    lastContact: '2024-02-10'
  },
  {
    id: '2',
    name: 'Global Supplies Ltd',
    email: 'info@globalsupplies.com',
    phone: '+1 (555) 987-6543',
    address: '456 Industry Blvd, Chicago, IL 60601',
    type: 'supplier',
    status: 'active',
    lastContact: '2024-02-09'
  }
];

const ClientList: React.FC<ClientListProps> = ({ type, searchQuery }) => {
  const filteredClients = demoClients.filter(client => 
    (type === 'clients' ? client.type === 'client' : client.type === 'supplier') &&
    (client.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     client.email.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="divide-y">
      {filteredClients.map((client) => (
        <div key={client.id} className="p-6 hover:bg-gray-50">
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <div>
                <div className="font-medium text-lg">{client.name}</div>
                <div className="flex items-center gap-6 mt-2 text-gray-500">
                  <div className="flex items-center gap-2">
                    <Mail size={16} />
                    <span>{client.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone size={16} />
                    <span>{client.phone}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-gray-500">
                <MapPin size={16} />
                <span>{client.address}</span>
              </div>

              <div className="flex items-center gap-4">
                <span className={`px-2 py-1 rounded-full text-xs ${
                  client.status === 'active'
                    ? 'bg-green-100 text-green-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {client.status}
                </span>
                <span className="text-sm text-gray-500">
                  Last contact: {new Date(client.lastContact).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button className="p-2 text-gray-400 hover:text-emerald-400 hover:bg-emerald-50 rounded-lg">
                <MessageSquare size={18} />
              </button>
              <button className="p-2 text-gray-400 hover:text-emerald-400 hover:bg-emerald-50 rounded-lg">
                <Edit2 size={18} />
              </button>
              <button className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-50 rounded-lg">
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ClientList;