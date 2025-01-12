# src/monitoring/monitor.py
from typing import Dict, Any, Optional
import logging
import time
from dataclasses import dataclass
from datetime import datetime
import asyncio
import openai

@dataclass
class SystemMetrics:
    """System performance metrics."""
    processing_time: float
    memory_usage: float
    api_calls: int
    cache_hits: int
    error_count: int
    success_rate: float

class ProductionMonitor:
    """Monitors system performance in production."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = []
        self.alert_manager = AlertManager(config)

    async def start_monitoring(self):
        """Start monitoring system."""
        try:
            monitoring_tasks = [
                self.monitor_performance(),
                self.monitor_api_usage(),
                self.monitor_errors(),
                self.check_system_health()
            ]
            
            await asyncio.gather(*monitoring_tasks)
            
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
            await self.alert_manager.send_alert("MonitoringFailure", str(e))

class MetricsCollector:
    """Collects and processes system metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_metrics: Dict[str, Any] = {}
        
    async def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        return SystemMetrics(
            processing_time=self.measure_processing_time(),
            memory_usage=self.get_memory_usage(),
            api_calls=self.count_api_calls(),
            cache_hits=self.get_cache_hits(),
            error_count=self.get_error_count(),
            success_rate=self.calculate_success_rate()
        )
        
    def measure_processing_time(self) -> float:
        """Measure average processing time."""
        recent_times = self.current_metrics.get('processing_times', [])
        return sum(recent_times) / len(recent_times) if recent_times else 0.0

class AlertManager:
    """Manages system alerts and notifications."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_history = []
        
    async def check_alerts(self, metrics: SystemMetrics):
        """Check metrics against alert thresholds."""
        alerts = []
        
        # Check processing time
        if metrics.processing_time > self.config['max_processing_time']:
            alerts.append({
                'type': 'HighProcessingTime',
                'value': metrics.processing_time,
                'threshold': self.config['max_processing_time'],
                'severity': 'warning'
            })
            
        # Check error rate
        if metrics.error_count > self.config['max_error_count']:
            alerts.append({
                'type': 'HighErrorRate',
                'value': metrics.error_count,
                'threshold': self.config['max_error_count'],
                'severity': 'critical'
            })
            
        # Send alerts if any
        for alert in alerts:
            await self.send_alert(alert)
            
    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = 'warning'
    ):
        """Send alert through configured channels."""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log alert
        self.logger.warning(f"Alert: {alert}")
        
        # Store in history
        self.alert_history.append(alert)
        
        # Send through configured channels
        await self.send_to_channels(alert)

class HealthChecker:
    """Checks system health status."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def check_system_health(self) -> Dict[str, Any]:
        """Perform system health check."""
        return {
            'api_status': await self.check_api_status(),
            'memory_status': self.check_memory_status(),
            'cache_status': self.check_cache_status(),
            'error_status': self.check_error_status()
        }
        
    async def check_api_status(self) -> Dict[str, Any]:
        """Check API availability and response times."""
        try:
            start_time = time.time()
            # Make test API call
            await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "test"}],
                max_tokens=1
            )
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
 