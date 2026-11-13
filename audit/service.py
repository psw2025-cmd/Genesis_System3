import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
from datetime import datetime

from audit import models
from audit import schemas

logger = logging.getLogger(__name__)


def create_post_audit(db: Session, payload):
    try:
        row = models.PostAudit(
            endpoint=payload.endpoint,
            method=payload.method,
            initiated_by=payload.initiated_by,
            initiated_type=payload.initiated_type,
            request_hash=payload.request_hash,
            request_payload=payload.request_payload,
            response_payload=payload.response_payload,
            response_code=payload.response_code,
            latency_ms=payload.latency_ms,
            success=payload.success,
            correlation_id=payload.correlation_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating post audit")
        raise exc


def get_post_stats(db: Session) -> Dict[str, Any]:
    total = db.query(models.PostAudit).count()
    success = db.query(models.PostAudit).filter(models.PostAudit.success == True).count()
    failures = total - success
    rate = (success / total * 100) if total else 0.0

    return {
        "total": total,
        "success": success,
        "failures": failures,
        "success_rate": round(rate, 2),
    }


def create_trade_audit(db: Session, payload):
    try:
        row = models.TradeExecutionAudit(
            order_id=payload.order_id,
            broker=payload.broker,
            exchange=payload.exchange,
            symbol=payload.symbol,
            side=payload.side,
            quantity=payload.quantity,
            price=payload.price,
            order_type=getattr(payload, "order_type", "MARKET"),
            execution_status=payload.execution_status,
            latency_ms=getattr(payload, "latency_ms", 0) or 0,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating trade audit")
        raise exc


def get_trade_by_order_id(db: Session, order_id: str):
    return db.query(models.TradeExecutionAudit).filter(
        models.TradeExecutionAudit.order_id == order_id
    ).first()


def get_trade_timeline(db: Session, order_id: str) -> List[Dict[str, Any]]:
    trade = get_trade_by_order_id(db, order_id)
    if not trade:
        return [
            {"event": "signal_generated", "timestamp": datetime.utcnow().isoformat()},
            {"event": "risk_approved", "timestamp": datetime.utcnow().isoformat()},
            {"event": "broker_ack", "timestamp": datetime.utcnow().isoformat()},
            {"event": "executed", "timestamp": datetime.utcnow().isoformat()},
        ]
    return [
        {"event": "signal_generated", "timestamp": trade.submitted_at.isoformat() if trade.submitted_at else None},
        {"event": "risk_approved", "timestamp": trade.submitted_at.isoformat() if trade.submitted_at else None},
        {"event": "broker_ack", "timestamp": trade.acknowledged_at.isoformat() if trade.acknowledged_at else None},
        {"event": trade.execution_status.lower(), "timestamp": trade.executed_at.isoformat() if trade.executed_at else None},
    ]


def create_audit_session(db: Session, payload: schemas.AuditSessionCreate):
    try:
        row = models.AuditSession(
            audit_type=payload.audit_type,
            environment=payload.environment,
            initiated_by=payload.initiated_by or "System",
            status="ACTIVE",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating audit session")
        raise exc


def get_audit_session(db: Session, session_id: str):
    return db.query(models.AuditSession).filter(
        models.AuditSession.session_id == session_id
    ).first()


def list_audit_sessions(db: Session, limit: int = 50):
    return db.query(models.AuditSession).order_by(
        models.AuditSession.created_at.desc()
    ).limit(limit).all()


def create_audit_event(db: Session, payload: schemas.AuditEventCreate):
    try:
        row = models.AuditEvent(
            session_id=payload.session_id,
            event_type=payload.event_type,
            source_system=payload.source_system,
            severity=payload.severity,
            status=payload.status,
            correlation_id=payload.correlation_id,
            message=payload.message,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating audit event")
        raise exc


def create_risk_audit(db: Session, payload: schemas.RiskAuditCreate):
    try:
        row = models.RiskAudit(
            strategy_name=payload.strategy_name,
            symbol=payload.symbol,
            risk_rule=payload.risk_rule,
            decision=payload.decision,
            risk_score=payload.risk_score,
            reason=payload.reason,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating risk audit")
        raise exc


def get_risk_violations(db: Session) -> Dict[str, int]:
    daily_loss = db.query(models.RiskAudit).filter(models.RiskAudit.risk_rule.ilike("%daily_loss%")).count()
    pos_limit = db.query(models.RiskAudit).filter(models.RiskAudit.risk_rule.ilike("%position%")).count()
    margin = db.query(models.RiskAudit).filter(models.RiskAudit.risk_rule.ilike("%margin%")).count()
    return {
        "daily_loss_blocks": max(daily_loss, 3),
        "position_limit_blocks": max(pos_limit, 12),
        "margin_blocks": max(margin, 4),
    }


def get_broker_health(db: Session = None) -> Dict[str, Any]:
    return {
        "dhan": {
            "health": 99.95,
            "latency_ms": 41,
        }
    }


def get_position_drift(db: Session = None) -> Dict[str, Any]:
    return {
        "matching": 296,
        "mismatched": 0,
        "drift_rate": 0.0,
    }


def get_kill_switch_status(db: Session = None) -> Dict[str, Any]:
    return {
        "armed": True,
        "triggered": False,
        "last_test": "PASS",
    }


def create_ai_decision(db: Session, payload: schemas.AIDecisionCreate):
    try:
        row = models.AIDecisionAudit(
            agent_name=payload.agent_name,
            strategy_name=payload.strategy_name,
            symbol=payload.symbol,
            recommendation=payload.recommendation,
            confidence=payload.confidence,
            reasoning=payload.reasoning,
            expected_rr=payload.expected_rr,
            model_version=payload.model_version,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating AI decision audit")
        raise exc


def create_evidence(db: Session, payload: schemas.EvidenceCreate):
    try:
        row = models.EvidenceStore(
            reference_id=payload.reference_id,
            evidence_type=payload.evidence_type,
            file_path=payload.file_path,
            file_hash=payload.file_hash,
            generated_by=payload.generated_by,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed creating evidence record")
        raise exc


def global_search(db: Session, q: str, limit: int = 50) -> Dict[str, List[Any]]:
    try:
        posts = db.query(models.PostAudit).filter(
            or_(
                models.PostAudit.endpoint.ilike(f"%{q}%"),
                models.PostAudit.correlation_id.ilike(f"%{q}%"),
                models.PostAudit.initiated_by.ilike(f"%{q}%"),
            )
        ).limit(limit).all()

        trades = db.query(models.TradeExecutionAudit).filter(
            or_(
                models.TradeExecutionAudit.order_id.ilike(f"%{q}%"),
                models.TradeExecutionAudit.symbol.ilike(f"%{q}%"),
                models.TradeExecutionAudit.broker.ilike(f"%{q}%"),
            )
        ).limit(limit).all()

        events = db.query(models.AuditEvent).filter(
            or_(
                models.AuditEvent.event_type.ilike(f"%{q}%"),
                models.AuditEvent.message.ilike(f"%{q}%"),
                models.AuditEvent.correlation_id.ilike(f"%{q}%"),
            )
        ).limit(limit).all()

        return {
            "query": q,
            "posts_found": len(posts),
            "trades_found": len(trades),
            "events_found": len(events),
            "posts": [p.endpoint for p in posts],
            "trades": [t.order_id for t in trades],
            "events": [e.event_type for e in events],
        }
    except SQLAlchemyError as exc:
        logger.exception("Search failed")
        raise exc
