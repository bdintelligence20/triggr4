import React, { useState } from 'react';
import { ArrowLeft, Plus, Search, Upload, Download } from 'lucide-react';
import ClientList from './ClientList';
import AddClientModal from './AddClientModal';

interface ClientsSuppliersProps {
  type: 'clients' | 'suppliers';
  onBack: () => void;
}

const ClientsSuppliers: React.FC<ClientsSuppliersProps> = ({ type, onBack }) => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h2 className="text-2xl font-semibold">
              {type === 'clients' ? 'Clients' : 'Suppliers'}
            </h2>
            <p className="text-gray-500 mt-1">
              Manage your {type === 'clients' ? 'client' : 'supplier'} relationships
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
            <Search size={20} className="text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={`Search ${type}...`}
              className="bg-transparent border-none focus:outline-none"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-2 text-emerald-400 hover:bg-emerald-50 rounded-lg">
              <Upload size={20} />
              Import
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-emerald-400 hover:bg-emerald-50 rounded-lg">
              <Download size={20} />
              Export
            </button>
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
            >
              <Plus size={20} />
              Add {type === 'clients' ? 'Client' : 'Supplier'}
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm">
        <ClientList type={type} searchQuery={searchQuery} />
      </div>

      <AddClientModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        type={type}
      />
    </div>
  );
};

export default ClientsSuppliers;