import React, { useState } from 'react';
import { File, Folder, Download, Trash } from 'lucide-react';
import { KnowledgeItem } from '../../../types';
import { useKnowledgeBase } from '../../../hooks/useKnowledgeBase';
import FileActionsMenu from './FileActions/FileActionsMenu';
import DeleteConfirmationDialog from './FileActions/DeleteConfirmationDialog';
import RenameDialog from './FileActions/RenameDialog';

interface FileListProps {
  items: KnowledgeItem[];
}

const FileList = ({ items }: FileListProps) => {
  const { deleteKnowledgeItem } = useKnowledgeBase();
  const [itemToDelete, setItemToDelete] = useState<KnowledgeItem | null>(null);
  const [itemToRename, setItemToRename] = useState<KnowledgeItem | null>(null);

  const handleDelete = (item: KnowledgeItem) => {
    setItemToDelete(item);
  };

  const handleRename = (item: KnowledgeItem) => {
    setItemToRename(item);
  };

  const confirmDelete = () => {
    if (itemToDelete) {
      deleteKnowledgeItem(itemToDelete.id);
      setItemToDelete(null);
    }
  };

  const confirmRename = (newName: string) => {
    if (itemToRename) {
      // Implement rename logic here - would need a backend endpoint
      console.log('Renaming:', itemToRename.title, 'to:', newName);
      setItemToRename(null);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-3 border-b border-gray-200 flex justify-between items-center">
        <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500 flex-1">
          <div className="col-span-6 lg:col-span-6">Name</div>
          <div className="hidden md:block col-span-2">Category</div>
          <div className="hidden md:block col-span-2">Created</div>
          <div className="hidden md:block col-span-2">Size</div>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              console.log('Downloading files...');
            }}
            className="flex items-center gap-1 text-emerald-400 hover:text-emerald-500 transition-colors px-4"
          >
            <Download size={16} />
            <span className="text-sm">Download</span>
          </a>
        </div>
      </div>
      
      {items.map((item) => (
        <div 
          key={item.id}
          className="grid grid-cols-12 gap-4 p-3 hover:bg-gray-50 items-center text-sm border-b border-gray-100 last:border-none"
        >
          <div className="col-span-12 md:col-span-6 flex items-center gap-3">
            <div className="p-2 bg-emerald-50 rounded-lg flex-shrink-0">
              <File className="text-emerald-400" size={20} />
            </div>
            <div className="min-w-0">
              <p className="font-medium truncate">{item.title}</p>
              {item.word_count && (
                <p className="text-xs text-gray-500">{item.word_count} words</p>
              )}
            </div>
          </div>
          <div className="hidden md:block col-span-2 text-gray-600">{item.category}</div>
          <div className="hidden md:block col-span-2 text-gray-600">
            {new Date(item.createdAt).toLocaleDateString()}
          </div>
          <div className="hidden md:block col-span-1 text-gray-600">{item.fileSize}</div>
          <div className="hidden md:block col-span-1 text-right">
            <FileActionsMenu
              item={item}
              onRename={handleRename}
              onDelete={handleDelete}
            />
          </div>
        </div>
      ))}

      {items.length === 0 && (
        <div className="p-6 text-center text-gray-500">
          No knowledge items found. Upload some files to get started.
        </div>
      )}

      {/* Dialogs */}
      {itemToDelete && (
        <DeleteConfirmationDialog
          item={itemToDelete}
          isOpen={true}
          onClose={() => setItemToDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
      
      {itemToRename && (
        <RenameDialog
          item={itemToRename}
          isOpen={true}
          onClose={() => setItemToRename(null)}
          onConfirm={confirmRename}
        />
      )}
    </div>
  );
};

export default FileList;
