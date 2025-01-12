# src/tests/test_runner.py
import sys
import yaml
import logging
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from .test_framework import TestFramework
from .test_result_analyzer import TestResultAnalyzer

class TestRunner:
    """Manages test execution and reporting."""
    
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.config = self.load_test_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.analyzer = TestResultAnalyzer()
        
    def load_test_config(self, config_path: str) -> Dict[str, Any]:
        """Load test configuration."""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    async def run_tests(self, test_pattern: str = None) -> Dict[str, Any]:
        """Run test suite with optional pattern matching."""
        try:
            self.logger.info("Starting test execution")
            
            # Initialize test framework
            framework = TestFramework(self.config)
            
            # Run test suites
            results = await framework.run_test_suite()
            
            # Analyze results
            analysis = self.analyzer.analyze_results(results)
            
            # Generate and save report
            report = self.analyzer.generate_report(analysis)
            self.save_report(report)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            raise
    
    def save_report(self, report: str):
        """Save test report to file."""
        report_path = Path("tests/reports") / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, "w") as f:
            f.write(report)

def main():
    """Command line interface for test runner."""
    parser = argparse.ArgumentParser(description="Run podcast summarizer tests")
    parser.add_argument("--pattern", help="Pattern to filter tests")
    parser.add_argument("--config", default="config/test_config.yaml", help="Test configuration file")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    try:
        runner = TestRunner(args.config)
        asyncio.run(runner.run_tests(args.pattern))
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()