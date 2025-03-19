import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import ClientList from './ClientList';
import AddClientModal from './AddClientModal';

interface ClientsPanelProps {
  type: 'clients' | 'suppliers';
}

const ClientsPanel: React.FC<ClientsPanelProps> = ({ type }) => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  return (
    <div>
      <div className="p-4 flex justify-between items-center">
        <h2 className="text-lg font-semibold">
          {type === 'clients' ? 'Client List' : 'Supplier List'}
        </h2>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
        >
          <Plus size={20} />
          Add {type === 'clients' ? 'Client' : 'Supplier'}
        </button>
      </div>
      
      <ClientList type={type} />
      
      <AddClientModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        type={type}
      />
    </div>
  );
};

export default ClientsPanel;