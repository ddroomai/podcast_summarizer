# src/core/processor.py
from typing import List, Dict, Any
import pdfplumber
import re
from pathlib import Path
import logging
import openai

class DocumentProcessor:
    """Core document processing class."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def process_document(self, file_path: Path) -> str:
        """Process document and return cleaned text."""
        try:
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text = await self.extract_pdf_text(file_path)
            else:
                text = await self.read_text_file(file_path)
            
            # Clean text
            cleaned_text = self.clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def extract_pdf_text(self, file_path: Path) -> str:
            """Extract text from PDF file."""
            with pdfplumber.open(file_path) as pdf:
                text_content = []
                for page in pdf.pages:
                    text_content.append(page.extract_text())
                    
            return "\n".join(text_content)
    
    def clean_text(self, text: str) -> str:
            """Clean and normalize text."""
            patterns = {
                'headers': r'(^.*?Page \d+.*?$)',
                'extra_spaces': r'\s+',
                'speaker_tags': r'^([A-Z][a-zA-Z]*\s*:)'  # Preserve speaker tags
            }
            
            cleaned = text
            
            # Remove headers/footers
            cleaned = re.sub(patterns['headers'], '', cleaned, flags=re.MULTILINE)
            
            # Normalize whitespace but preserve speaker tags
            speaker_tags = re.finditer(patterns['speaker_tags'], cleaned, re.MULTILINE)
            tag_positions = [(m.start(), m.group()) for m in speaker_tags]
            
            cleaned = re.sub(patterns['extra_spaces'], ' ', cleaned)
            
            # Restore speaker tags with proper formatting
            for pos, tag in tag_positions:
                cleaned = f"{cleaned[:pos]}\n{tag}{cleaned[pos+len(tag):]}"
            
            return cleaned.strip()

    async def read_text_file(self, file_path: Path) -> str:
            """Read text from a text file."""
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

class ChunkManager:
    """Manages text chunking with semantic awareness."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_chunk_size = config.get('min_chunk_size', 400)
        self.max_chunk_size = config.get('max_chunk_size', 1000)
        
    async def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create semantically meaningful chunks."""
        # Split into initial paragraphs
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para.split())
            
            # Check if adding paragraph exceeds max size
            if current_size + para_size > self.max_chunk_size:
                if current_chunk:
                    chunks.append(self.create_chunk_dict(current_chunk))
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(para)
            current_size += para_size
            
            # Check if chunk is big enough to split
            if current_size >= self.min_chunk_size:
                chunks.append(self.create_chunk_dict(current_chunk))
                current_chunk = []
                current_size = 0
        
        # Add any remaining content
        if current_chunk:
            chunks.append(self.create_chunk_dict(current_chunk))
        
        return chunks
    
    def create_chunk_dict(self, paragraphs: List[str]) -> Dict[str, Any]:
        """Create a chunk dictionary with metadata."""
        text = '\n\n'.join(paragraphs)
        return {
            'text': text,
            'size': len(text.split()),
            'speakers': self.extract_speakers(text)
        }
        
    def extract_speakers(self, text: str) -> List[str]:
        """Extract speaker names from chunk."""
        speaker_pattern = r'^([A-Z][a-zA-Z]*)\s*:'
        speakers = set(re.findall(speaker_pattern, text, re.MULTILINE))
        return list(speakers) 


