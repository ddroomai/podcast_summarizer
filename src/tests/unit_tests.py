# src/tests/unit_tests.py
import pytest
from pathlib import Path
from typing import Dict, Any
from ..core.processor import DocumentProcessor
from ..core.semantic import ChunkManager

class UnitTests:
    """Unit test implementation."""
    
    @pytest.mark.asyncio
    async def test_document_processing(self):
        """Test document processing functionality."""
        processor = DocumentProcessor(self.config)
        test_file = Path("tests/data/test_document.pdf")
        
        result = await processor.process_document(test_file)
        assert result is not None
        assert len(result) > 0
        
    @pytest.mark.asyncio
    async def test_chunk_creation(self):
        """Test chunk creation and validation."""
        chunk_manager = ChunkManager(self.config)
        test_text = "Test content " * 100  # Create substantial test content
        
        chunks = await chunk_manager.create_chunks(test_text)
        assert len(chunks) > 0
        assert all(
            self.config['min_chunk_size'] <= len(chunk['text'].split()) <= self.config['max_chunk_size']
            for chunk in chunks
        )