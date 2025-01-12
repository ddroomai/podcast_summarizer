# src/tests/performance_tests.py
import pytest
import time
from pathlib import Path
import psutil
from typing import Dict, Any
from ..core.pipeline import PodcastSummarizer

class PerformanceTests:
    """Performance testing implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.large_test_file = Path("tests/data/large_podcast.pdf")
    
    async def test_processing_speed(self):
        """Test processing performance."""
        start_time = time.time()
        
        result = await self.summarizer.process_podcast(self.large_test_file)
        
        processing_time = time.time() - start_time
        assert processing_time <= self.config['max_processing_time']
    
    async def test_memory_usage(self):
        """Test memory efficiency."""
        process = psutil.Process()
        
        # Record starting memory
        start_memory = process.memory_info().rss
        
        # Run processing
        result = await self.summarizer.process_podcast(self.large_test_file)
        
        # Check memory after processing
        end_memory = process.memory_info().rss
        memory_increase = end_memory - start_memory
        
        assert memory_increase <= self.config['max_memory_increase']
    
    async def test_batch_processing(self):
        """Test batch processing performance."""
        test_files = [
            self.large_test_file,
            Path("tests/data/medium_podcast.pdf"),
            Path("tests/data/small_podcast.pdf")
        ]
        
        start_time = time.time()
        
        # Process multiple files
        results = []
        for file in test_files:
            result = await self.summarizer.process_podcast(file)
            results.append(result)
            
        total_time = time.time() - start_time
        average_time = total_time / len(test_files)
        
        assert average_time <= self.config['max_avg_processing_time']