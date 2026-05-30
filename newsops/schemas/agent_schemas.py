from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Literal

class FactItem(BaseModel):
    text: str
    confidence: Literal["high", "medium", "low"] = "medium"
    source_index: Optional[int] = None

class IngestionOutput(BaseModel):
    agent: Literal["ingestion"]
    domain: str
    facts: List[FactItem]
    entities: List[str] = []
    sentiment: Literal["positive", "negative", "neutral", "mixed"] = "neutral"
    overall_confidence: Literal["high", "medium", "low"]
    corroboration_count: int = 0
    mock_mode_active: bool = False
    
    @field_validator("facts")
    def must_have_facts(cls, v):
        if len(v) == 0:
            raise ValueError("facts list cannot be empty")
        return v

class KPIItem(BaseModel):
    kpi: str
    current_value: Optional[float] = None
    current_unit: Optional[str] = None
    projected_value: Optional[float] = None
    delta: Optional[float] = None
    delta_pct: Optional[float] = None
    direction: Literal["increase", "decrease", "stable"] = "stable"

class AnalysisOutput(BaseModel):
    agent: Literal["analysis"]
    domain: str
    severity: int = Field(ge=1, le=10)
    severity_label: str
    severity_reasoning: str
    time_horizon: Literal["immediate", "short_term", "medium_term"]
    kpis_affected: List[KPIItem] = []
    total_impact: Dict[str, Any] = {}
    affected_parties: List[str] = []
    second_order_effects: List[str] = []
    reasoning_chain: List[str] = Field(min_length=4)
    data_gaps: List[str] = []

class ActionItem(BaseModel):
    rank: int
    action_id: str
    action_type: str
    description: str
    api_endpoint: str
    api_payload: Dict[str, Any]
    quantified_delta: str
    feasibility_score: int = Field(ge=1, le=10)
    impact_score: int = Field(ge=1, le=10)
    composite_score: float
    justification: str
    success_metric: str
    time_to_execute: str

class DecisionOutput(BaseModel):
    agent: Literal["decision"]
    domain: str
    candidates_evaluated: int
    actions: List[ActionItem] = Field(min_length=1)
    recommended_execution_sequence: List[int] = []
    auto_execute_rank_1: bool = True
    reasoning_summary: str

class ResearchOutput(BaseModel):
    agent: Literal["research"]
    domain: str
    additional_context: str
    corroboration: Literal["confirmed", "likely", "unconfirmed", "contradicted"]
    confidence_boosters: List[str] = []
    rag_sources_used: int = 0
    rag_augmented: bool = False
