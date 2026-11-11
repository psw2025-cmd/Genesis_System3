from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AuditSessionCreate(BaseModel):
    audit_type: str = Field(..., max_length=100)
    environment: str = Field(default="production", max_length=50)
    initiated_by: Optional[str] = Field(default="System", max_length=100)

    model_config = ConfigDict(from_attributes=True)


class AuditSessionResponse(BaseModel):
    session_id: str
    audit_type: str
    environment: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    system_health_score: float
    total_checks: int
    passed_checks: int
    failed_checks: int

    model_config = ConfigDict(from_attributes=True)


class AuditEventCreate(BaseModel):
    event_type: str = Field(..., max_length=50)
    source_system: str = Field(default="Genesis", max_length=100)
    severity: str = Field(default="INFO", max_length=20)
    status: str = Field(default="LOGGED", max_length=20)
    correlation_id: Optional[str] = Field(default=None, max_length=255)
    message: str
    session_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PostAuditCreate(BaseModel):
    endpoint: str = Field(..., max_length=500)
    method: str = Field(default="POST", max_length=20)
    initiated_by: str = Field(default="agent", max_length=100)
    initiated_type: str = Field(default="agent", max_length=50)
    request_hash: str = Field(default="", max_length=256)
    request_payload: Dict[str, Any] = Field(default_factory=dict)
    response_payload: Dict[str, Any] = Field(default_factory=dict)
    response_code: int = Field(..., ge=100, le=599)
    latency_ms: int = Field(..., ge=0)
    success: bool = True
    correlation_id: Optional[str] = Field(default=None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class PostAuditResponse(BaseModel):
    post_id: str
    endpoint: str
    method: str
    initiated_by: str
    initiated_type: str
    request_hash: str
    request_payload: Dict[str, Any]
    response_payload: Dict[str, Any]
    response_code: int
    latency_ms: int
    success: bool
    correlation_id: Optional[str] = None
    request_time: datetime

    model_config = ConfigDict(from_attributes=True)


class TradeAuditCreate(BaseModel):
    order_id: str = Field(..., max_length=100)
    broker: str = Field(..., max_length=50)
    exchange: str = Field(default="NSE", max_length=50)
    symbol: str = Field(..., max_length=50)
    side: str = Field(..., max_length=10)
    quantity: int = Field(..., gt=0)
    price: float = Field(default=0.0)
    order_type: str = Field(default="MARKET", max_length=20)
    execution_status: str = Field(default="SUBMITTED", max_length=50)
    latency_ms: Optional[int] = Field(default=0, ge=0)

    model_config = ConfigDict(from_attributes=True)


class TradeAuditResponse(BaseModel):
    execution_id: str
    order_id: str
    broker: str
    exchange: str
    symbol: str
    side: str
    quantity: int
    price: float
    order_type: str
    execution_status: str
    latency_ms: int
    submitted_at: datetime
    acknowledged_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RiskAuditCreate(BaseModel):
    strategy_name: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=50)
    risk_rule: str = Field(..., max_length=200)
    decision: str = Field(..., max_length=20)
    risk_score: float = Field(default=0.0)
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PositionReconcileRequest(BaseModel):
    symbol: Optional[str] = None


class AIDecisionCreate(BaseModel):
    agent_name: str = Field(..., max_length=100)
    strategy_name: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=50)
    recommendation: str = Field(..., max_length=20)
    confidence: float = Field(...)
    reasoning: Dict[str, Any] = Field(default_factory=dict)
    expected_rr: float = Field(default=0.0)
    model_version: str = Field(default="v1", max_length=50)

    model_config = ConfigDict(from_attributes=True)


class IncidentCreate(BaseModel):
    issue_type: str = Field(..., max_length=100)
    root_cause: Optional[str] = None
    fix_action: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceCreate(BaseModel):
    reference_id: str = Field(..., max_length=255)
    evidence_type: str = Field(..., max_length=50)
    file_path: str
    file_hash: Optional[str] = Field(default="", max_length=128)
    generated_by: Optional[str] = Field(default="QA-Auditor", max_length=100)

    model_config = ConfigDict(from_attributes=True)
