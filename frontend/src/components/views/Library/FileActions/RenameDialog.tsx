import React, { useState, useEffect } from 'react';
import { Edit } from 'lucide-react';
import { KnowledgeItem } from '../../../../types';

interface RenameDialogProps {
  item: KnowledgeItem;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (newName: string) => void;
}

const RenameDialog: React.FC<RenameDialogProps> = ({
  item,
  isOpen,
  onClose,
  onConfirm,
}) => {
  const [newName, setNewName] = useState(item.title);

  // Reset the name when the item changes
  useEffect(() => {
    setNewName(item.title);
  }, [item]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newName.trim() && newName !== item.title) {
      onConfirm(newName.trim());
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-full">
            <Edit className="text-blue-500" size={24} />
          </div>
          <h3 className="text-lg font-medium">Rename Item</h3>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="newName" className="block text-sm font-medium text-gray-700 mb-1">
              New Name
            </label>
            <input
              type="text"
              id="newName"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
              autoFocus
            />
          </div>
          
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              disabled={!newName.trim() || newName === item.title}
            >
              Rename
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RenameDialog;
