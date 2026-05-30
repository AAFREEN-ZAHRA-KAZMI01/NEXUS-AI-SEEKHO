from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class KpiAffected(BaseModel):
    kpi: str
    current_value: Optional[float] = None
    projected_value: Optional[float] = None
    current_unit: Optional[str] = None
    direction: Optional[str] = None
    delta: Optional[float] = None
    delta_pct: Optional[float] = None

    model_config = {"extra": "allow"}


class TopAction(BaseModel):
    action_type: Optional[str] = None
    description: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_payload: Optional[Dict[str, Any]] = None
    quantified_delta: Optional[str] = None
    justification: Optional[str] = None
    rank: Optional[int] = None
    action_id: Optional[str] = None
    feasibility_score: Optional[float] = None
    impact_score: Optional[float] = None
    composite_score: Optional[float] = None
    success_metric: Optional[str] = None
    time_to_execute: Optional[str] = None

    model_config = {"extra": "allow"}


class DeltaItem(BaseModel):
    from_value: Optional[float] = None
    to: Optional[float] = None
    change_pct: Optional[float] = None

    model_config = {"extra": "allow"}


class NotificationSent(BaseModel):
    notification_id: Optional[str] = None
    session_id: Optional[str] = None
    recipient: Optional[str] = None
    recipient_role: Optional[str] = None
    channel: Optional[str] = None
    message_preview: Optional[str] = None
    status: Optional[str] = None
    timestamp: Optional[str] = None

    model_config = {"extra": "allow"}


class AnalysisResponse(BaseModel):
    session_id: str
    domain: str
    status: str
    duration_seconds: Optional[float] = None
    insight: Optional[str] = None
    severity: Optional[int] = None
    severity_label: Optional[str] = None
    impact_summary: Optional[Any] = None
    kpis_affected: Optional[List[KpiAffected]] = None
    top_action: Optional[TopAction] = None
    alternative_actions: Optional[List[TopAction]] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    delta: Optional[Dict[str, Any]] = None
    notifications_sent: Optional[List[NotificationSent]] = None
    execution_status: Optional[str] = None
    corroboration: Optional[str] = None
    context: Optional[str] = None
    trace_url: Optional[str] = None
    artifacts: Optional[Dict[str, Any]] = None
    rag_sources_used: Optional[int] = None
    rag_augmented: Optional[bool] = None

    model_config = {"extra": "allow"}


class TraceArtifact(BaseModel):
    id: str
    session_id: str
    agent_name: Optional[str] = None
    artifact_type: Optional[str] = None
    content: Optional[Any] = None
    created_at: Optional[str] = None
    duration_seconds: Optional[float] = None

    model_config = {"extra": "allow"}


class TraceResponse(BaseModel):
    session: Optional[Dict[str, Any]] = None
    artifacts: List[TraceArtifact]
    total_artifacts: int
    pipeline_duration_seconds: Optional[float] = None

    model_config = {"extra": "allow"}
