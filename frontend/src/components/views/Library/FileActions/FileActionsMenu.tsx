import React, { useState } from 'react';
import { MoreVertical, Edit, Trash, Download, Share2 } from 'lucide-react';
import { KnowledgeItem } from '../../../../types';

interface FileActionsMenuProps {
  item: KnowledgeItem;
  onRename: (item: KnowledgeItem) => void;
  onDelete: (item: KnowledgeItem) => void;
}

const FileActionsMenu: React.FC<FileActionsMenuProps> = ({ 
  item, 
  onRename, 
  onDelete 
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleRename = () => {
    onRename(item);
    setIsOpen(false);
  };

  const handleDelete = () => {
    onDelete(item);
    setIsOpen(false);
  };

  const handleDownload = () => {
    if (item.fileUrl) {
      window.open(item.fileUrl, '_blank');
    }
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={toggleMenu}
        className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
      >
        <MoreVertical size={16} />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg z-20 py-1">
            <button
              onClick={handleRename}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
            >
              <Edit size={16} />
              <span>Rename</span>
            </button>
            <button
              onClick={handleDownload}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              disabled={!item.fileUrl}
            >
              <Download size={16} />
              <span>Download</span>
            </button>
            <button
              onClick={handleDelete}
              className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
            >
              <Trash size={16} />
              <span>Delete</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default FileActionsMenu;
