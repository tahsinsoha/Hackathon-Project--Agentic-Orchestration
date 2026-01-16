"""Incident scenario simulator using Tonic-like data generation."""
import random
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from core.models import Incident, IncidentType, IncidentSeverity


class IncidentSimulator:
    """Generates realistic incident scenarios for demo and testing."""
    
    def __init__(self):
        self.services = [
            "api-service",
            "auth-service", 
            "payment-service",
            "notification-service",
            "analytics-service"
        ]
    
    def generate_incident(self, incident_type: str = None) -> Tuple[Incident, Dict[str, Any], Dict[str, Any]]:
        """Generate a realistic incident with metrics.
        
        Args:
            incident_type: Specific type to generate, or None for random
            
        Returns:
            Tuple of (Incident, current_metrics, baseline_metrics)
        """
        if incident_type:
            scenario = getattr(self, f"_generate_{incident_type}")()
        else:
            scenarios = [
                self._generate_latency_spike,
                self._generate_error_rate,
                self._generate_resource_saturation,
                self._generate_queue_depth
            ]
            scenario = random.choice(scenarios)()
        
        return scenario
    
    def _generate_latency_spike(self) -> Tuple[Incident, Dict[str, Any], Dict[str, Any]]:
        """Generate a latency spike incident."""
        service = random.choice(self.services)
        
        incident = Incident(
            id=f"inc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            service_name=service,
            severity=IncidentSeverity.HIGH,
            incident_type=IncidentType.UNKNOWN  # Will be classified by triage
        )
        
        baseline_metrics = {
            "latency_p50": 150,
            "latency_p95": 300,
            "latency_p99": 500,
            "error_rate": 0.1,
            "cpu_usage": 45,
            "memory_usage": 60,
            "request_rate": 100,
            "queue_depth": 50
        }
        
        # Simulate latency spike
        current_metrics = baseline_metrics.copy()
        current_metrics.update({
            "latency_p50": 800,
            "latency_p95": 2500,
            "latency_p99": 5000,  # 5 seconds!
            "error_rate": 1.2,
            "cpu_usage": 55,
        })
        
        incident.add_timeline_event(
            "detection",
            f"Latency spike detected: p99 increased from 500ms to 5000ms",
            current_metrics
        )
        
        return incident, current_metrics, baseline_metrics
    
    def _generate_error_rate(self) -> Tuple[Incident, Dict[str, Any], Dict[str, Any]]:
        """Generate an error rate increase incident."""
        service = random.choice(self.services)
        
        incident = Incident(
            id=f"inc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            service_name=service,
            severity=IncidentSeverity.CRITICAL,
        )
        
        baseline_metrics = {
            "latency_p50": 120,
            "latency_p95": 250,
            "latency_p99": 400,
            "error_rate": 0.1,
            "cpu_usage": 40,
            "memory_usage": 55,
            "request_rate": 150,
            "queue_depth": 30
        }
        
        # Simulate error rate spike
        current_metrics = baseline_metrics.copy()
        current_metrics.update({
            "error_rate": 15.8,  # 15.8% errors!
            "latency_p99": 800,  # Also some latency increase
            "request_rate": 140,  # Slightly lower due to failures
        })
        
        incident.add_timeline_event(
            "detection",
            f"Error rate spike detected: {current_metrics['error_rate']}%",
            current_metrics
        )
        
        return incident, current_metrics, baseline_metrics
    
    def _generate_resource_saturation(self) -> Tuple[Incident, Dict[str, Any], Dict[str, Any]]:
        """Generate a resource saturation incident."""
        service = random.choice(self.services)
        
        incident = Incident(
            id=f"inc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            service_name=service,
            severity=IncidentSeverity.HIGH,
        )
        
        baseline_metrics = {
            "latency_p50": 100,
            "latency_p95": 200,
            "latency_p99": 350,
            "error_rate": 0.05,
            "cpu_usage": 50,
            "memory_usage": 60,
            "request_rate": 200,
            "queue_depth": 100
        }
        
        # Simulate resource saturation
        current_metrics = baseline_metrics.copy()
        current_metrics.update({
            "cpu_usage": 92,  # CPU maxed out
            "memory_usage": 89,  # Memory near limit
            "latency_p99": 3000,  # Slow due to resource contention
            "error_rate": 2.5,
        })
        
        incident.add_timeline_event(
            "detection",
            f"Resource saturation: CPU {current_metrics['cpu_usage']}%, Memory {current_metrics['memory_usage']}%",
            current_metrics
        )
        
        return incident, current_metrics, baseline_metrics
    
    def _generate_queue_depth(self) -> Tuple[Incident, Dict[str, Any], Dict[str, Any]]:
        """Generate a queue depth growth incident."""
        service = "message-processor-service"
        
        incident = Incident(
            id=f"inc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            service_name=service,
            severity=IncidentSeverity.MEDIUM,
        )
        
        baseline_metrics = {
            "latency_p50": 80,
            "latency_p95": 150,
            "latency_p99": 250,
            "error_rate": 0.02,
            "cpu_usage": 35,
            "memory_usage": 50,
            "request_rate": 80,
            "queue_depth": 200
        }
        
        # Simulate queue backlog
        current_metrics = baseline_metrics.copy()
        current_metrics.update({
            "queue_depth": 15000,  # Massive backlog!
            "cpu_usage": 25,  # Low CPU suggests consumer is down
            "latency_p99": 450,
        })
        
        incident.add_timeline_event(
            "detection",
            f"Queue depth explosion: {current_metrics['queue_depth']} messages pending",
            current_metrics
        )
        
        return incident, current_metrics, baseline_metrics
    
    def generate_normal_metrics(self, service: str = None) -> Dict[str, float]:
        """Generate normal/healthy metrics."""
        return {
            "latency_p50": random.uniform(80, 150),
            "latency_p95": random.uniform(180, 280),
            "latency_p99": random.uniform(300, 500),
            "error_rate": random.uniform(0.01, 0.2),
            "cpu_usage": random.uniform(30, 60),
            "memory_usage": random.uniform(40, 70),
            "request_rate": random.uniform(80, 200),
            "queue_depth": random.uniform(10, 100)
        }

