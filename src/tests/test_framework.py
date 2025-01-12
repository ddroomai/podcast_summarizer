# src/tests/test_framework.py
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any, List

class TestFramework:
    """Core testing framework."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        
    async def run_test_suite(self):
        """Run complete test suite."""
        test_suites = [
            self.run_unit_tests(),
            self.run_integration_tests(),
            self.run_quality_tests(),
            self.run_performance_tests()
        ]
        
        results = await asyncio.gather(*test_suites)
        return self.analyze_results(results)