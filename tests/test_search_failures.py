from unittest.mock import Mock
from sqlalchemy.exc import SQLAlchemyError
import pytest


def test_search_db_failure():
    db = Mock()
    db.query.side_effect = SQLAlchemyError("query failed")

    with pytest.raises(SQLAlchemyError):
        db.query()
