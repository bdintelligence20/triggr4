from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedTextSplitter:
    """Enhanced text splitter with multiple strategies."""
    
    @staticmethod
    def create_semantic_chunks(text: str, chunk_size: int = 1500, chunk_overlap: int = 100) -> List[str]:
        """Split text into semantic chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
            keep_separator=True
        )
        return splitter.split_text(text)
    
    @staticmethod
    def create_document_chunks(documents: List[Document], chunk_size: int = 1500, chunk_overlap: int = 100) -> List[Document]:
        """Split documents into chunks while preserving metadata."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
            keep_separator=True
        )
        return splitter.split_documents(documents)
    
    @staticmethod
    def create_hierarchical_chunks(documents: List[Document]) -> List[Document]:
        """Create hierarchical chunks (parent/child relationships)."""
        from langchain.text_splitter import RecursiveCharacterTextSplitter, HeaderType
        
        # First split by headers
        header_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""],
            is_separator_regex=False,
            headers_to_split_on=[
                HeaderType(level=1, header_marker="# "),
                HeaderType(level=2, header_marker="## "),
                HeaderType(level=3, header_marker="### ")
            ]
        )
        
        # Then split the chunks further if needed
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        # Process each document
        all_chunks = []
        for doc in documents:
            # First split by headers
            header_chunks = header_splitter.split_text(doc.page_content)
            
            # Create documents with metadata
            for i, chunk in enumerate(header_chunks):
                chunk_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_id": i,
                        "document_id": doc.metadata.get("source", "unknown")
                    }
                )
                all_chunks.append(chunk_doc)
        
        return all_chunks
