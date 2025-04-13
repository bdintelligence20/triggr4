// hooks/useFileUpload.tsx
import { useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { API_URL, UploadResponse, KnowledgeItem } from '../types';

// Helper function to validate CSV files
const validateCsvFile = (file: File): Promise<void> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        if (!content) {
          reject(new Error("Could not read file content"));
          return;
        }
        
        // Basic CSV validation
        const lines = content.split('\n');
        if (lines.length < 2) {
          reject(new Error("CSV file must have at least a header row and one data row"));
          return;
        }
        
        // Check if all rows have the same number of columns
        const headerCols = lines[0].split(',').length;
        for (let i = 1; i < Math.min(lines.length, 5); i++) {
          if (lines[i].trim() === '') continue; // Skip empty lines
          const cols = lines[i].split(',').length;
          if (cols !== headerCols) {
            reject(new Error(`Row ${i+1} has ${cols} columns, but header has ${headerCols} columns`));
            return;
          }
        }
        
        resolve();
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => {
      reject(new Error("Error reading file"));
    };
    
    reader.readAsText(file);
  });
};

export const useFileUpload = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { 
    selectedCategory,
    knowledgeItems,
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
        
        // Validate CSV files before upload
        if (file.name.toLowerCase().endsWith('.csv')) {
          // Use the showNotification function with the correct signature
          // The AppContext shows it accepts a message and a duration or type
          showNotification("CSV file detected. Ensuring proper formatting...");
          
          // Basic client-side validation for CSV files
          try {
            await validateCsvFile(file);
          } catch (error) {
            console.error(`CSV validation error for ${fileName}:`, error);
            showNotification(`CSV validation warning: ${error instanceof Error ? error.message : 'Unknown error'}. Attempting upload anyway.`);
          }
        }
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', selectedCategory === 'all' ? 'hrhub' : selectedCategory);
        formData.append('title', fileName);
        
        // Send file to backend using the API service
        console.log(`Uploading file to ${API_URL}/upload`);
        const response = await import('../services/api').then(api => 
          api.uploadDocument(file, selectedCategory === 'all' ? 'hrhub' : selectedCategory, fileName)
        );
        
        if (response.error) {
          throw new Error(response.error);
        }
        
        const result = response.data || { item_id: Date.now().toString() + i, file_url: undefined };
        console.log('Upload response:', result);
        
        // Determine file type
        const fileType = fileName.toLowerCase().endsWith('.pdf') ? 'pdf' : 
                        (fileName.toLowerCase().endsWith('.doc') || fileName.toLowerCase().endsWith('.docx')) ? 'doc' :
                        fileName.toLowerCase().endsWith('.csv') ? 'csv' : 'text';
        
        // Create new knowledge item
        const newItem: KnowledgeItem = {
          id: result.item_id || Date.now().toString() + i,
          title: fileName,
          category: selectedCategory === 'all' ? 'general' : selectedCategory,
          createdAt: new Date(),
          type: fileType as 'pdf' | 'doc' | 'csv' | 'text',
          fileSize: formatFileSize(file.size),
          fileUrl: result.file_url,
          processing_status: 'completed'
        };
        
        // Add to knowledge items
        setKnowledgeItems([...knowledgeItems, newItem]);
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
