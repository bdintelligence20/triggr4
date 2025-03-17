import os
import logging
from flask import request
from werkzeug.utils import secure_filename
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_user_organization_id():
    """Get the organization ID for the authenticated user."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        # Verify token
        from auth_routes import verify_token
        payload = verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        
        # Import here to avoid circular imports
        from firebase_admin import firestore
        db = firestore.client()
        
        # Get user data from Firestore
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return None
        
        user_data = user_doc.to_dict()
        return user_data.get('organizationId')
    except Exception as e:
        logger.error(f"Error getting user organization ID: {str(e)}")
        return None

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    import PyPDF2
    
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Process up to 50 pages to avoid memory issues
            for i in range(min(50, len(reader.pages))):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise

def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from a DOCX file."""
    import docx2txt
    
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        raise

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from a file based on its type."""
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'doc' or file_type == 'docx':
        return extract_text_from_docx(file_path)
    elif file_type == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def split_long_sentence(sentence, max_length):
    """
    Splits a long sentence into multiple chunks without breaking words.
    """
    words = sentence.split()
    chunks = []
    current_chunk = ""
    for word in words:
        # Add a space only if current_chunk isn't empty
        additional_space = 1 if current_chunk else 0
        if len(current_chunk) + len(word) + additional_space <= max_length:
            current_chunk = f"{current_chunk} {word}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def split_message_semantically(message_body, max_length=1600):
    """
    Splits a message into semantically coherent chunks using sentence boundaries.
    If a single sentence is too long, it is further split using word boundaries.
    """
    from nltk.tokenize import sent_tokenize
    
    sentences = sent_tokenize(message_body)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding the sentence exceeds the limit, start a new chunk.
        if len(current_chunk) + len(sentence) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # If a single sentence is too long, split it by words.
                long_chunks = split_long_sentence(sentence, max_length)
                # Append all but the last chunk, and use the last chunk as the new current_chunk.
                chunks.extend(long_chunks[:-1])
                current_chunk = long_chunks[-1]
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
