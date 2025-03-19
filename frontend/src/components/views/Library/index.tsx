import React, { useState } from 'react';
import LibraryHeader from './LibraryHeader';
import FileList from './FileList';
import UploadModal from './UploadModal';
import CloudStorageIntegration from './CloudStorage';
import Teams from './Teams';
import { useKnowledgeBase } from '../../../hooks/useKnowledgeBase';
import { useAppContext } from '../../../contexts/AppContext';

const Library = () => {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'files' | 'cloud' | 'teams'>('files');
  const { loadDocuments } = useKnowledgeBase();
  const { knowledgeItems } = useAppContext();

  // Note: Document loading is now handled by the useKnowledgeBase hook

  return (
    <div className="p-6">
      <LibraryHeader 
        onAddContent={() => setIsUploadModalOpen(true)}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      {activeTab === 'files' && <FileList items={knowledgeItems} />}
      {activeTab === 'cloud' && <CloudStorageIntegration />}
      {activeTab === 'teams' && <Teams />}

      <UploadModal 
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
      />
    </div>
  );
};

export default Library;
