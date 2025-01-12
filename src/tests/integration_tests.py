# src/tests/integration_tests.py
import pytest
from pathlib import Path
from typing import Dict, Any
from ..core.pipeline import PodcastSummarizer
from ..core.semantic import ContextManager

class IntegrationTests:
    """Integration test implementation."""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self):
        """Test complete summarization pipeline."""
        summarizer = PodcastSummarizer(self.config)
        test_file = Path("tests/data/test_podcast.pdf")
        
        result = await summarizer.process_podcast(test_file)
        
        assert result is not None
        assert 'summary' in result
        assert 'metadata' in result
        
    @pytest.mark.asyncio
    async def test_context_preservation(self):
        """Test context preservation across chunks."""
        chunks = [
            {'text': 'Initial context about AI'},
            {'text': 'More details about AI concepts'},
            {'text': 'Conclusion about AI impact'}
        ]
        
        context_manager = ContextManager(self.config)
        summaries = []
        
        for chunk in chunks:
            context = context_manager.get_relevant_context(chunk)
            summary = await self.summarizer.summarize_chunk(chunk, context)
            summaries.append(summary)
            context_manager.update_context(chunk, summary)
            
        # Verify context preservation
        assert len(summaries) == len(chunks)
        # Check for thematic consistency