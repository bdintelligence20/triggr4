import os
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_community.document_loaders import (
    PyPDFLoader, 
    Docx2txtLoader, 
    TextLoader, 
    CSVLoader, 
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader, 
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredImageLoader,
    UnstructuredEmailLoader,
    DirectoryLoader,
    UnstructuredFileLoader
)
import logging

logger = logging.getLogger(__name__)

class DocumentLoaderFactory:
    """Factory for creating document loaders based on file type."""
    
    @staticmethod
    def get_loader(file_path: str):
        """Get the appropriate loader for a file."""
        file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        
        # Map file extensions to loaders
        loaders = {
            # Text documents
            'pdf': PyPDFLoader,
            'txt': TextLoader,
            'md': UnstructuredMarkdownLoader,
            'html': UnstructuredHTMLLoader,
            'htm': UnstructuredHTMLLoader,
            
            # Office documents
            'docx': Docx2txtLoader,
            'doc': Docx2txtLoader,
            'pptx': UnstructuredPowerPointLoader,
            'ppt': UnstructuredPowerPointLoader,
            'xlsx': UnstructuredExcelLoader,
            'xls': UnstructuredExcelLoader,
            'csv': CSVLoader,
            
            # Email
            'eml': UnstructuredEmailLoader,
            'msg': UnstructuredEmailLoader,
            
            # Images
            'jpg': UnstructuredImageLoader,
            'jpeg': UnstructuredImageLoader,
            'png': UnstructuredImageLoader,
            'gif': UnstructuredImageLoader,
        }
        
        # Get the appropriate loader class
        loader_class = loaders.get(file_ext)
        
        if loader_class:
            try:
                return loader_class(file_path)
            except Exception as e:
                logger.error(f"Error creating loader for {file_path}: {str(e)}")
                # Fallback to unstructured loader
                return UnstructuredFileLoader(file_path)
        else:
            # Default to unstructured loader for unknown types
            logger.info(f"No specific loader for {file_ext}, using UnstructuredFileLoader")
            return UnstructuredFileLoader(file_path)
    
    @staticmethod
    def load_document(file_path: str) -> List[Document]:
        """Load a document using the appropriate loader."""
        loader = DocumentLoaderFactory.get_loader(file_path)
        try:
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            # Return empty document with error info
            return [Document(
                page_content=f"Error loading document: {str(e)}",
                metadata={"source": file_path, "error": str(e)}
            )]
    
    @staticmethod
    def extract_text_and_metadata(file_path: str) -> tuple:
        """Extract text and metadata from a document."""
        documents = DocumentLoaderFactory.load_document(file_path)
        
        # Combine text from all pages/sections
        text = "\n\n".join([doc.page_content for doc in documents])
        
        # Combine metadata
        metadata = {}
        for doc in documents:
            metadata.update(doc.metadata)
        
        return text, metadata, documents
