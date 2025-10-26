"""Document processing and chunking utilities."""
import logging
from typing import List, Dict, Any
from pathlib import Path
import pypdf
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk various document types."""
    
    def __init__(self):
        """Initialize document processor."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a file and return chunked documents.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of document chunks with metadata
        """
        file_path_obj = Path(file_path)
        suffix = file_path_obj.suffix.lower()
        
        try:
            if suffix == '.pdf':
                text = self._extract_pdf(file_path)
            elif suffix == '.docx':
                text = self._extract_docx(file_path)
            elif suffix in ['.txt', '.md']:
                text = self._extract_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
            
            # Chunk the text
            chunks = self.text_splitter.split_text(text)
            
            # Create document objects with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'text': chunk,
                    'metadata': {
                        'source': file_path_obj.name,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'file_type': suffix
                    }
                })
            
            logger.info(f"Processed {file_path_obj.name} into {len(documents)} chunks")
            return documents
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def process_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Process raw text and return chunked documents.
        
        Args:
            text: Text to process
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of document chunks with metadata
        """
        if metadata is None:
            metadata = {}
        
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy()
            doc_metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks)
            })
            documents.append({
                'text': chunk,
                'metadata': doc_metadata
            })
        
        return documents


# Global instance
document_processor = DocumentProcessor()
