import React from 'react';
import { Edit2, Trash2, MessageSquare } from 'lucide-react';

interface Client {
  id: string;
  name: string;
  email: string;
  type: 'client' | 'supplier';
  status: 'active' | 'inactive';
  lastContact: string;
}

interface ClientListProps {
  type: 'clients' | 'suppliers';
}

const demoClients: Client[] = [
  {
    id: '1',
    name: 'Acme Corporation',
    email: 'contact@acme.com',
    type: 'client',
    status: 'active',
    lastContact: '2024-02-10'
  },
  {
    id: '2',
    name: 'Global Supplies Ltd',
    email: 'info@globalsupplies.com',
    type: 'supplier',
    status: 'active',
    lastContact: '2024-02-09'
  }
];

const ClientList: React.FC<ClientListProps> = ({ type }) => {
  const filteredClients = demoClients.filter(client => 
    type === 'clients' ? client.type === 'client' : client.type === 'supplier'
  );

  return (
    <div className="divide-y">
      {filteredClients.map((client) => (
        <div key={client.id} className="p-4 hover:bg-gray-50">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">{client.name}</div>
              <div className="text-sm text-gray-500">{client.email}</div>
              <div className="flex items-center gap-4 mt-1">
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  client.status === 'active'
                    ? 'bg-green-100 text-green-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {client.status}
                </span>
                <span className="text-xs text-gray-500">
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