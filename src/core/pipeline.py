# src/core/pipeline.py
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import asyncio
from datetime import datetime

from .processor import DocumentProcessor
from .semantic import SemanticProcessor
from .summarization import SummarizationPipeline
from .term_processor import TechnicalTermProcessor
from .quality import QualityController
from .context import ContextManager

class QualityError(Exception):
    """Raised when quality validation fails."""
    pass

class PodcastSummarizer:
    """Main pipeline orchestrator."""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Initialize components
        self.document_processor = DocumentProcessor(self.config)
        self.semantic_processor = SemanticProcessor(self.config)
        self.summarization_pipeline = SummarizationPipeline(self.config)
        self.term_processor = TechnicalTermProcessor(self.config)
        self.quality_controller = QualityController(self.config)
        self.context_manager = ContextManager(self.config)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)

    async def process_podcast(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """Process podcast transcript end-to-end."""
        try:
            # Start timing
            start_time = datetime.now()
            
            # Phase 1: Document Processing
            self.logger.info("Starting document processing")
            text = await self.document_processor.process_document(file_path)
            
            # Phase 2: Create and Enhance Chunks
            chunks = await self.semantic_processor.enhance_chunks(
                await self.document_processor.create_chunks(text)
            )
            
            # Phase 3: Process Chunks
            summaries = []
            for i, chunk in enumerate(chunks):
                self.logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Get relevant context
                context = self.context_manager.get_relevant_context(chunk)
                
                # Process technical terms
                terms = await self.term_processor.process_terms(chunk['text'])
                
                # Generate summary
                summary = await self.summarization_pipeline.summarize_chunk(
                    chunk,
                    context=context,
                    terms=terms
                )
                
                # Validate quality
                validation = await self.quality_controller.validate_summary(
                    summary['summary'],
                    chunk
                )
                
                if validation['valid']:
                    summaries.append(summary)
                    # Update context
                    self.context_manager.update_context(chunk, summary['summary'])
                else:
                    raise QualityError(f"Quality validation failed for chunk {i+1}")
            
            # Create final output
            result = self.create_final_output(
                summaries,
                start_time,
                file_path
            )
            
            self.logger.info("Processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            raise
    def create_final_output(
        self,
        summaries: List[Dict[str, Any]],
        start_time: datetime,
        file_path: Path
    ) -> Dict[str, Any]:
        """Create final formatted output."""
        return {
            'summary': self.format_summaries(summaries),
            'metadata': {
                'filename': file_path.name,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'chunk_count': len(summaries),
                'timestamp': datetime.now().isoformat()
            },
            'technical_terms': self.term_processor.get_all_terms()
        }
    def format_summaries(
        self,
        summaries: List[Dict[str, Any]]
    ) -> str:
        """Format summaries into final text."""
        formatted_parts = []
        
        for i, summary in enumerate(summaries):
            formatted_parts.append(
                f"Section {i+1}:\n{summary['summary']}\n"
            )
            
        return "\n\n".join(formatted_parts)