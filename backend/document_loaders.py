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
            'csv': lambda file_path: CSVLoader(
                file_path=file_path,
                csv_args={
                    'delimiter': ',',
                    'quotechar': '"',
                    'fieldnames': None,  # Auto-detect headers
                    'encoding': 'utf-8-sig'  # Handle BOM and common encoding issues
                }
            ),
            
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
        file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        loader = DocumentLoaderFactory.get_loader(file_path)
        
        try:
            # Special handling for CSV files
            if file_ext == 'csv':
                try:
                    import pandas as pd
                    # Try to read with pandas first to validate CSV structure
                    df = pd.read_csv(file_path, encoding='utf-8-sig', on_bad_lines='warn')
                    logger.info(f"CSV validation: {file_path} has {len(df)} rows and {len(df.columns)} columns")
                except Exception as csv_e:
                    logger.warning(f"CSV validation failed: {str(csv_e)}. Will attempt with LangChain loader anyway.")
            
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            
            # For CSV files, provide more detailed error information
            if file_ext == 'csv':
                try:
                    import pandas as pd
                    # Try different encodings and delimiters as fallback
                    for encoding in ['utf-8', 'latin1', 'cp1252']:
                        for delimiter in [',', ';', '\t', '|']:
                            try:
                                df = pd.read_csv(file_path, encoding=encoding, sep=delimiter)
                                content = df.to_string(index=False)
                                logger.info(f"CSV recovery successful with encoding={encoding}, delimiter={delimiter}")
                                return [Document(
                                    page_content=content,
                                    metadata={"source": file_path, "recovered": True, 
                                             "encoding": encoding, "delimiter": delimiter}
                                )]
                            except:
                                pass
                except Exception as recovery_e:
                    logger.error(f"CSV recovery attempts failed: {str(recovery_e)}")
            
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
