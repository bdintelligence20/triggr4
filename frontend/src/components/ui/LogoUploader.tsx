// components/ui/LogoUploader.tsx
import React, { useRef, useState } from 'react';
import { Upload } from 'lucide-react';
import { useAppContext } from '../../contexts/AppContext';
import { API_URL } from '../../types';

interface LogoUploaderProps {
  currentLogo?: string;
  onLogoChange?: (logoUrl: string | null) => void;
}

const LogoUploader: React.FC<LogoUploaderProps> = ({ currentLogo, onLogoChange }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [logo, setLogo] = useState<string | null>(currentLogo || null);
  const [isUploading, setIsUploading] = useState(false);
  
  const { showNotification, setError } = useAppContext();
  
  const openFileSelector = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  const handleLogoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'];
    if (!validImageTypes.includes(file.type)) {
      showNotification("Please upload a valid image file (JPEG, PNG, GIF, SVG)");
      return;
    }
    
    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      showNotification("Logo image must be less than 2MB");
      return;
    }
    
    setIsUploading(true);
    
    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', 'logo');
      formData.append('title', 'Organization Logo');
      
      // Send file to backend
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
      
      const result = await response.json();
      
      // Update logo state with the file URL
      if (result.status === 'success' && result.item_id) {
        // Use the file URL from the response
        const logoUrl = result.file_url || `${API_URL}/documents/${result.item_id}`;
        setLogo(logoUrl);
        
        // Call the callback if provided
        if (onLogoChange) {
          onLogoChange(logoUrl);
        }
        
        showNotification("Logo uploaded successfully");
      }
    } catch (error) {
      console.error('Error uploading logo:', error);
      setError(`Failed to upload logo: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  return (
    <div className="relative group">
      <div 
        className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center p-3 cursor-pointer overflow-hidden"
        onClick={openFileSelector}
      >
        {logo ? (
          <img 
            src={logo} 
            alt="Organization Logo" 
            className="w-full h-full object-contain"
          />
        ) : (
          <span className="text-sm font-bold text-emerald-400">Logo</span>
        )}
        
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-lg">
          <Upload size={16} className="text-white" />
        </div>
      </div>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleLogoUpload}
        accept="image/jpeg,image/png,image/gif,image/svg+xml"
        className="hidden"
      />
      
      {isUploading && (
        <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-emerald-100 bg-opacity-75 rounded-lg">
          <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
    </div>
  );
};

export default LogoUploader;
