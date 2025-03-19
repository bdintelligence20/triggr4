import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { KnowledgeItem } from '../../../../types';

interface DeleteConfirmationDialogProps {
  item: KnowledgeItem;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

const DeleteConfirmationDialog: React.FC<DeleteConfirmationDialogProps> = ({
  item,
  isOpen,
  onClose,
  onConfirm,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-red-100 rounded-full">
            <AlertTriangle className="text-red-500" size={24} />
          </div>
          <h3 className="text-lg font-medium">Delete Item</h3>
        </div>
        
        <p className="text-gray-600 mb-2">
          Are you sure you want to delete <span className="font-medium">{item.title}</span>?
        </p>
        <p className="text-gray-600 mb-6">
          This action cannot be undone.
        </p>
        
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationDialog;
