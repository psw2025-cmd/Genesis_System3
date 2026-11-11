from unittest.mock import Mock
import pytest
from sqlalchemy.exc import SQLAlchemyError
import service


class DummyPayload:
    endpoint = "/api/order/place"
    method = "POST"
    initiated_by = "SignalAgent"
    initiated_type = "agent"
    request_hash = "abc123"
    request_payload = {}
    response_payload = {}
    response_code = 200
    latency_ms = 50
    success = True
    correlation_id = "corr-1"


def test_create_post_audit_commit_failure():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("database error")

    with pytest.raises(SQLAlchemyError):
        service.create_post_audit(
            db,
            DummyPayload(),
        )

    db.rollback.assert_called_once()


def test_create_post_audit_refresh_failure():
    db = Mock()
    db.refresh.side_effect = SQLAlchemyError("refresh failed")

    with pytest.raises(SQLAlchemyError):
        service.create_post_audit(
            db,
            DummyPayload(),
        )

    db.rollback.assert_called_once()


def test_create_post_audit_add_failure():
    db = Mock()
    db.add.side_effect = SQLAlchemyError("insert failed")

    with pytest.raises(SQLAlchemyError):
        service.create_post_audit(
            db,
            DummyPayload(),
        )

    db.rollback.assert_called_once()
