from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    LATENCY_SPIKE = "latency_spike"
    ERROR_RATE = "error_rate_increase"
    RESOURCE_SATURATION = "resource_saturation"
    QUEUE_DEPTH = "queue_depth_growth"
    UNKNOWN = "unknown"


class IncidentSeverity(str, Enum):
    """Severity levels for incidents."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentStage(str, Enum):
    """Stages in the multi-agent pipeline."""
    DETECTION = "detection"
    SCOUT = "scout"
    TRIAGE = "triage"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    EXECUTOR = "executor"
    POSTCHECK = "postcheck"
    COMPLETED = "completed"
    FAILED = "failed"


class MitigationType(str, Enum):
    """Types of mitigations available."""
    ROLLBACK = "rollback"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    FEATURE_FLAG_DISABLE = "feature_flag_disable"
    TRAFFIC_SHED = "traffic_shed"
    RESTART_SERVICE = "restart_service"


class Evidence(BaseModel):
    """Evidence collected by Scout agent."""
    metrics: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    recent_deploys: List[Dict[str, Any]] = Field(default_factory=list)
    traces: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Hypothesis(BaseModel):
    """A root cause hypothesis."""
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_needed: List[str]
    validation_criteria: str


class ExperimentResult(BaseModel):
    """Result of an experiment run by Verifier agent."""
    hypothesis_id: int
    validated: bool
    findings: str
    confidence: float = Field(ge=0.0, le=1.0)


class Mitigation(BaseModel):
    """A proposed mitigation action."""
    type: MitigationType
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reversible: bool = True
    estimated_impact: str
    risk_level: str
    requires_approval: bool = False


class GuardrailCheck(BaseModel):
    """Result of a guardrail safety check."""
    passed: bool
    reason: str
    policy_violated: Optional[str] = None


class IncidentMetrics(BaseModel):
    """Metrics tracked for an incident."""
    detection_latency_seconds: float = 0.0
    triage_accuracy: float = 0.0
    time_to_mitigation_seconds: float = 0.0
    mitigation_success: bool = False
    false_positive: bool = False


class Incident(BaseModel):
    """Main incident model tracking the entire lifecycle."""
    id: str
    service_name: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    # Current state
    stage: AgentStage = AgentStage.DETECTION
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    incident_type: IncidentType = IncidentType.UNKNOWN
    
    # Agent outputs
    evidence: Optional[Evidence] = None
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    experiments: List[ExperimentResult] = Field(default_factory=list)
    proposed_mitigation: Optional[Mitigation] = None
    applied_mitigation: Optional[Mitigation] = None
    
    # Status
    mitigation_approved: bool = False
    metrics_recovered: bool = False
    incident_summary: str = ""
    
    # Metrics
    metrics: IncidentMetrics = Field(default_factory=IncidentMetrics)
    
    # Audit trail
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_timeline_event(self, stage: str, message: str, data: Optional[Dict] = None):
        """Add an event to the incident timeline."""
        self.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "message": message,
            "data": data or {}
        })

