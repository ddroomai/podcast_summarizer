# src/core/quality.py
from typing import Dict, Any, List
import logging
from dataclasses import dataclass

class QualityCheckError(Exception):
    """Raised when quality checks fail."""
    pass

@dataclass
class QualityMetrics:
    """Defines quality metrics for summaries."""
    content_preservation: float  # 0-1 score
    technical_accuracy: float    # 0-1 score
    readability: float          # 0-1 score
    context_coherence: float    # 0-1 score

class QualityController:
    """Controls quality of generated summaries."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.min_quality_score = config.get('min_quality_score', 0.8)
        
    async def validate_summary(
        self,
        summary: str,
        original_chunk: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Validate summary quality."""
        try:
            # Calculate quality metrics
            metrics = await self.calculate_metrics(
                summary,
                original_chunk
            )
            
            # Check if metrics meet minimum requirements
            if self.meets_quality_standards(metrics):
                return {
                    'valid': True,
                    'metrics': metrics.__dict__,
                    'retry_count': retry_count
                }
                
            # Retry if below standards
            if retry_count < self.config.get('max_retries', 2):
                self.logger.warning("Summary below quality standards, retrying...")
                return await self.retry_summary(
                    original_chunk,
                    metrics,
                    retry_count + 1
                )
            
            raise QualityCheckError("Failed to meet quality standards")
            
        except Exception as e:
            self.logger.error(f"Quality validation error: {str(e)}")
            raise

    async def calculate_metrics(
            self,
            summary: str,
            original_chunk: Dict[str, Any]
        ) -> QualityMetrics:
            """Calculate quality metrics for summary."""
            return QualityMetrics(
                content_preservation=await self.check_content_preservation(
                    summary,
                    original_chunk
                ),
                technical_accuracy=await self.check_technical_accuracy(
                    summary,
                    original_chunk
                ),
                readability=self.check_readability(summary),
                context_coherence=await self.check_context_coherence(
                    summary,
                    original_chunk
                )
            )
        
    async def check_content_preservation(
            self,
            summary: str,
            original: Dict[str, Any]
        ) -> float:
            """Check how well the summary preserves important content."""
            # Extract key elements from original
            key_elements = {
                'quotes': self.extract_quotes(original['text']),
                'numbers': self.extract_numbers(original['text']),
                'names': self.extract_names(original['text'])
            }
    async def check_technical_accuracy(
            self,
            summary: str,
            original: Dict[str, Any]
        ) -> float:
            """Check technical term accuracy."""
            # Extract technical terms from both texts
            original_terms = set(self.extract_technical_terms(original['text']))
            summary_terms = set(self.extract_technical_terms(summary))
            
            # Calculate accuracy score
            if not original_terms:
                return 1.0
                
            correctly_used = len(original_terms.intersection(summary_terms))
            return correctly_used / len(original_terms)
        
    def check_readability(self, text: str) -> float:
            """Check text readability."""
            # Calculate average sentence length
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Penalize very long sentences
            if avg_sentence_length > 25:
                return max(0, 1 - (avg_sentence_length - 25) / 25)
                
            return 1.0
        
    def meets_quality_standards(
            self,
            metrics: QualityMetrics
        ) -> bool:
            """Check if metrics meet minimum standards."""
            return all(
                getattr(metrics, metric) >= self.min_quality_score
                for metric in metrics.__dict__
            )

class QualityReport:
    """Generates quality reports for summaries."""
    
    def generate_report(
        self,
        summary_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        return {
            'overall_quality': self.calculate_overall_quality(summary_results),
            'metrics_by_chunk': self.get_metrics_by_chunk(summary_results),
            'improvement_suggestions': self.generate_suggestions(summary_results)
        }
    
    def calculate_overall_quality(
        self,
        results: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall quality score."""
        scores = []
        for result in results:
            metrics = result['metrics']
            chunk_score = sum(metrics.values()) / len(metrics)
            scores.append(chunk_score)
            
        return sum(scores) / len(scores)