// hooks/useFileUpload.tsx
import { useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { API_URL, UploadResponse, KnowledgeItem } from '../types';

export const useFileUpload = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { 
    selectedCategory,
    setKnowledgeItems, 
    setIsProcessingFile, 
    setProcessingProgress, 
    setError,
    showNotification,
    formatFileSize
  } = useAppContext();
  
  const openFileSelector = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    setIsProcessingFile(true);
    setProcessingProgress(0);
    setError(null);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileName = file.name;
      
      try {
        // Update progress
        setProcessingProgress(((i + 0.5) / files.length) * 100);
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', selectedCategory === 'all' ? 'hrhub' : selectedCategory);
        formData.append('title', fileName);
        
        // Send file to backend
        console.log(`Uploading file to ${API_URL}/upload`);
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Server returned ${response.status}`);
        }
        
        const result: UploadResponse = await response.json();
        console.log('Upload response:', result);
        
        // Determine file type
        const fileType = fileName.toLowerCase().endsWith('.pdf') ? 'pdf' : 
                        (fileName.toLowerCase().endsWith('.doc') || fileName.toLowerCase().endsWith('.docx')) ? 'doc' : 'text';
        
        // Create new knowledge item
        const newItem = {
          id: result.item_id || Date.now().toString() + i,
          title: fileName,
          category: selectedCategory === 'all' ? 'general' : selectedCategory,
          createdAt: new Date(),
          type: fileType,
          fileSize: formatFileSize(file.size),
          fileUrl: result.file_url,
          processing_status: 'completed'
        };
        
        // Add to knowledge items
        setKnowledgeItems((currentItems: any[]) => [...currentItems, newItem]);
        setProcessingProgress(((i + 1) / files.length) * 100);
        
        // Show notification
        showNotification("File uploaded successfully");
      } catch (error) {
        console.error(`Error uploading file ${fileName}:`, error);
        setError(`Failed to upload ${fileName}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
    
    setIsProcessingFile(false);
    setProcessingProgress(0);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return {
    fileInputRef,
    openFileSelector,
    handleFileUpload
  };
};
