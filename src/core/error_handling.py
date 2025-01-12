from typing import Dict, Any, Optional, Callable
import logging
import asyncio
from datetime import datetime

class PodcastSummarizerError(Exception):
    """Base error class for podcast summarizer."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class DocumentProcessingError(PodcastSummarizerError):
    """Document processing specific errors."""
    pass

class SummarizationError(PodcastSummarizerError):
    """Summarization specific errors."""
    pass

class QualityError(PodcastSummarizerError):
    """Quality check specific errors."""
    pass

class ErrorHandler:
    """Handles errors and recovery strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.retry_counts = {}
        
    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Handle errors with appropriate recovery strategies."""
        try:
            # Log error
            self.logger.error(
                f"Error encountered: {str(error)}",
                exc_info=True,
                extra={'context': context}
            )
            
            # Get recovery strategy
            strategy = self.get_recovery_strategy(error)
            
            if strategy:
                return await self.execute_recovery(
                    strategy,
                    error,
                    context
                )
            else:
                raise error
                
        except Exception as e:
            self.logger.error(f"Error recovery failed: {str(e)}")
            raise
            
    def get_recovery_strategy(
        self,
        error: Exception
    ) -> Optional[Callable]:
        """Get appropriate recovery strategy for error."""
        strategies = {
            DocumentProcessingError: self.retry_document_processing,
            SummarizationError: self.retry_summarization,
            QualityError: self.handle_quality_error
        }
        
        for error_type, strategy in strategies.items():
            if isinstance(error, error_type):
                return strategy
                
        return None
    
    async def retry_document_processing(
        self,
        error: DocumentProcessingError,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Retry document processing with backoff."""
        max_retries = self.config.get('max_retries', 3)
        operation = context.get('operation')
        
        if not operation:
            return None
            
        for attempt in range(max_retries):
            try:
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                
                # Retry operation
                result = await operation()
                return result
                
            except Exception as e:
                self.logger.warning(
                    f"Retry attempt {attempt + 1} failed: {str(e)}"
                )
                
        return None
    
    async def retry_summarization(
        self,
        error: SummarizationError,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Retry summarization with modified parameters."""
        try:
            chunk = context.get('chunk')
            if not chunk:
                return None
                
            # Modify summarization parameters
            modified_context = {
                **context,
                'temperature': 0.5,  # Increase temperature for variety
                'max_tokens': int(context.get('max_tokens', 1000) * 1.2)
            }
            
            # Retry summarization
            result = await context['summarizer'].summarize_chunk(
                chunk,
                modified_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Summarization retry failed: {str(e)}")
            return None
    
    async def handle_quality_error(
        self,
        error: QualityError,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle quality validation failures."""
        try:
            # Analyze quality issues
            quality_issues = self.analyze_quality_issues(error, context)
            
            # Adjust parameters based on issues
            adjusted_params = self.adjust_quality_parameters(
                context,
                quality_issues
            )
            
            # Retry with adjusted parameters
            return await context['summarizer'].summarize_chunk(
                context['chunk'],
                adjusted_params
            )
            
        except Exception as e:
            self.logger.error(f"Quality error handling failed: {str(e)}")
            return None

    def analyze_quality_issues(
        self,
        error: QualityError,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze specific quality issues."""
        metrics = context.get('quality_metrics', {})
        issues = {}
        
        for metric, value in metrics.items():
            if value < self.config['quality_thresholds'][metric]:
                issues[metric] = {
                    'value': value,
                    'threshold': self.config['quality_thresholds'][metric],
                    'difference': self.config['quality_thresholds'][metric] - value
                }
                
        return issues