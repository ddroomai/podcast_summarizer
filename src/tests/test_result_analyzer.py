# src/tests/test_result_analyzer.py
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

class TestResultAnalyzer:
    """Analyzes and reports test results."""
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test suite results."""
        analysis = {
            'total_tests': len(results),
            'passed_tests': sum(1 for r in results if r['status'] == 'passed'),
            'failed_tests': [],
            'performance_metrics': self.analyze_performance_metrics(results),
            'quality_metrics': self.analyze_quality_metrics(results)
        }
        
        # Collect failed tests
        for result in results:
            if result['status'] == 'failed':
                analysis['failed_tests'].append({
                    'test_name': result['name'],
                    'error': result['error'],
                    'details': result.get('details', {})
                })
        
        return analysis
    
    def analyze_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze performance test results."""
        performance_results = [r for r in results if r.get('type') == 'performance']
        return {
            'avg_processing_time': sum(r['processing_time'] for r in performance_results) / len(performance_results),
            'memory_usage': max(r['memory_usage'] for r in performance_results),
            'total_execution_time': sum(r['processing_time'] for r in performance_results)
        }
    
    def analyze_quality_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze quality test results."""
        quality_results = [r for r in results if r.get('type') == 'quality']
        return {
            'avg_content_preservation': sum(r['metrics']['content_preservation'] for r in quality_results) / len(quality_results),
            'avg_technical_accuracy': sum(r['metrics']['technical_accuracy'] for r in quality_results) / len(quality_results)
        }
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate test report."""
        report = [
            "Test Execution Report",
            "===================",
            f"Total Tests: {analysis['total_tests']}",
            f"Passed: {analysis['passed_tests']}",
            f"Failed: {len(analysis['failed_tests'])}",
            "",
            "Performance Metrics:",
            f"Average Processing Time: {analysis['performance_metrics']['avg_processing_time']:.2f}s",
            f"Memory Usage: {analysis['performance_metrics']['memory_usage']}MB",
            "",
            "Quality Metrics:",
            f"Average Content Preservation: {analysis['quality_metrics']['avg_content_preservation']:.2%}",
            f"Average Technical Accuracy: {analysis['quality_metrics']['avg_technical_accuracy']:.2%}"
        ]
        
        if analysis['failed_tests']:
            report.extend([
                "",
                "Failed Tests:",
                "============"
            ])
            for test in analysis['failed_tests']:
                report.extend([
                    f"Test: {test['test_name']}",
                    f"Error: {test['error']}",
                    "---"
                ])
        
        return "\n".join(report)