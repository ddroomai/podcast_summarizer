# src/tests/quality_tests.py
import pytest
from typing import Dict, Any
from ..core.quality import QualityController

class QualityTests:
    """Quality assurance tests."""
    
    async def test_summary_quality(self):
        """Test summary quality metrics."""
        test_cases = self.load_test_cases()
        quality_controller = QualityController(self.config)
        
        for case in test_cases:
            summary = await self.summarizer.summarize_chunk(case['input'])
            
            # Validate quality
            quality_metrics = await quality_controller.validate_summary(
                summary,
                case['input']
            )
            
            assert quality_metrics['content_preservation'] >= 0.8
            assert quality_metrics['technical_accuracy'] >= 0.85
            assert quality_metrics['readability'] >= 0.8

    def load_test_cases(self):
        """Load test cases for quality testing."""
        return [
            {
                'input': {
                    'text': 'The artificial intelligence revolution has transformed various industries...',
                    'speakers': ['Expert A']
                },
                'expected_summary_length': 150,
                'key_topics': ['AI', 'transformation', 'industry impact']
            },
            {
                'input': {
                    'text': 'Machine learning models require careful training and validation...',
                    'speakers': ['Expert B']
                },
                'expected_summary_length': 120,
                'key_topics': ['machine learning', 'training', 'validation']
            }
        ]