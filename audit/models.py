import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Float,
    DateTime,
    Text,
    ForeignKey,
    Index,
    JSON
)
from audit.database import Base


class AuditSession(Base):
    __tablename__ = "audit_sessions"

    session_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    audit_type = Column(String(100))
    environment = Column(String(50), default="production")
    status = Column(String(30), default="ACTIVE")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    initiated_by = Column(String(100), default="System")
    system_health_score = Column(Float, default=100.0)
    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    session_id = Column(
        String(36),
        ForeignKey("audit_sessions.session_id"),
        nullable=True
    )
    event_type = Column(String(50))
    source_system = Column(String(100), default="Genesis")
    severity = Column(String(20), default="INFO")
    status = Column(String(20), default="LOGGED")
    correlation_id = Column(String(255), nullable=True)
    message = Column(Text)
    event_timestamp = Column(DateTime, default=datetime.utcnow)


class PostAudit(Base):
    __tablename__ = "post_audit"

    post_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    endpoint = Column(String(500), index=True)
    method = Column(String(20), default="POST")
    initiated_by = Column(String(100), default="unknown")
    initiated_type = Column(String(50), default="api")
    request_hash = Column(String(256), default="")
    request_payload = Column(JSON, default=dict)
    response_payload = Column(JSON, default=dict)
    response_code = Column(Integer)
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True)
    correlation_id = Column(String(255), index=True, nullable=True)
    request_time = Column(DateTime, default=datetime.utcnow, index=True)


class TradeExecutionAudit(Base):
    __tablename__ = "trade_execution_audit"

    execution_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    order_id = Column(String(100), index=True)
    broker = Column(String(50))
    exchange = Column(String(50))
    symbol = Column(String(50), index=True)
    side = Column(String(10))
    quantity = Column(Integer)
    price = Column(Float)
    order_type = Column(String(20), default="MARKET")
    execution_status = Column(String(50))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    latency_ms = Column(Integer, default=0)


class BrokerAckAudit(Base):
    __tablename__ = "broker_ack_audit"

    ack_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    order_id = Column(String(100), index=True)
    broker = Column(String(50))
    broker_order_id = Column(String(100), nullable=True)
    request_sent_at = Column(DateTime, default=datetime.utcnow)
    ack_received_at = Column(DateTime, default=datetime.utcnow)
    acknowledgement_status = Column(String(30))
    error_message = Column(Text, nullable=True)


class ExchangeVerification(Base):
    __tablename__ = "exchange_verification"

    verification_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    order_id = Column(String(100), index=True)
    exchange_order_id = Column(String(100), nullable=True)
    broker_order_id = Column(String(100), nullable=True)
    exchange_status = Column(String(40))
    verified = Column(Boolean, default=True)
    verification_time = Column(DateTime, default=datetime.utcnow)
    remarks = Column(Text, nullable=True)


class PositionReconciliation(Base):
    __tablename__ = "position_reconciliation"

    reconciliation_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    symbol = Column(String(50), index=True)
    broker_qty = Column(Integer, default=0)
    database_qty = Column(Integer, default=0)
    strategy_qty = Column(Integer, default=0)
    matched = Column(Boolean, default=True)
    mismatch_reason = Column(Text, nullable=True)
    auto_fixed = Column(Boolean, default=False)
    checked_at = Column(DateTime, default=datetime.utcnow)


class RiskAudit(Base):
    __tablename__ = "risk_audit"

    risk_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    strategy_name = Column(String(100))
    symbol = Column(String(50))
    risk_rule = Column(String(200))
    decision = Column(String(20))
    risk_score = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)


class AIDecisionAudit(Base):
    __tablename__ = "ai_decision_audit"

    decision_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    agent_name = Column(String(100))
    strategy_name = Column(String(100))
    symbol = Column(String(50))
    recommendation = Column(String(20))
    confidence = Column(Float)
    reasoning = Column(JSON, default=dict)
    expected_rr = Column(Float, default=0.0)
    model_version = Column(String(50), default="v1")
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentHealthAudit(Base):
    __tablename__ = "agent_health_audit"

    health_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    agent_name = Column(String(100), index=True)
    heartbeat_time = Column(DateTime, default=datetime.utcnow)
    tasks_processed = Column(Integer, default=0)
    failures = Column(Integer, default=0)
    recoveries = Column(Integer, default=0)
    health_score = Column(Float, default=100.0)
    status = Column(String(20), default="HEALTHY")


class AutoRemediationAudit(Base):
    __tablename__ = "auto_remediation_audit"

    remediation_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    issue_type = Column(String(100))
    root_cause = Column(Text, nullable=True)
    fix_action = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    remediation_started = Column(DateTime, default=datetime.utcnow)
    remediation_completed = Column(DateTime, nullable=True)
    verification_result = Column(String(20), default="PASS")


class KillSwitchAudit(Base):
    __tablename__ = "kill_switch_audit"

    kill_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    trigger_source = Column(String(100))
    trigger_reason = Column(Text, nullable=True)
    positions_closed = Column(Integer, default=0)
    capital_protected = Column(Float, default=0.0)
    activated_at = Column(DateTime, default=datetime.utcnow)
    deactivated_at = Column(DateTime, nullable=True)


class APIPerformanceAudit(Base):
    __tablename__ = "api_performance_audit"

    metric_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    endpoint = Column(String(300))
    method = Column(String(10))
    response_time_ms = Column(Integer)
    status_code = Column(Integer)
    success = Column(Boolean, default=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class EvidenceStore(Base):
    __tablename__ = "evidence_store"

    evidence_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    reference_id = Column(String(255))
    evidence_type = Column(String(50))
    file_path = Column(Text)
    file_hash = Column(String(128))
    generated_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


# Explicit Indexes
Index("idx_post_time", PostAudit.request_time)
Index("idx_post_endpoint", PostAudit.endpoint)
Index("idx_order_id", TradeExecutionAudit.order_id)
Index("idx_symbol", TradeExecutionAudit.symbol)
Index("idx_corr", PostAudit.correlation_id)
Index("idx_agent", AgentHealthAudit.agent_name)
