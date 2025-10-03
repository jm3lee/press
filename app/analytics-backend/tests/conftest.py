"""Test configuration for analytics-backend unit and integration suites."""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path
from typing import Iterator

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if importlib.util.find_spec("psycopg2") is None:
    fake_psycopg2 = types.ModuleType("psycopg2")
    fake_extras = types.ModuleType("psycopg2.extras")
    fake_pool = types.ModuleType("psycopg2.pool")

    def _json(value):
        return value

    def _execute_values(*args, **kwargs):
        raise RuntimeError("psycopg2 execute_values is not available in tests")

    class _SimpleConnectionPool:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("psycopg2 pool is not available in tests")

    fake_extras.Json = _json
    fake_extras.execute_values = _execute_values
    fake_pool.SimpleConnectionPool = _SimpleConnectionPool

    sys.modules["psycopg2"] = fake_psycopg2
    sys.modules["psycopg2.extras"] = fake_extras
    sys.modules["psycopg2.pool"] = fake_pool

os.environ.setdefault("PIE_DATA_DIR", "/data/src/templates")


@pytest.fixture(scope="session")
def flask_app() -> Iterator:
    required_vars = [
        "DATABASE_HOST",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_NAME",
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        pytest.skip(
            "analytics-backend integration tests require TimescaleDB credentials"
        )

    from analytics_backend.app import create_app
    from analytics_backend.db import TimescaleDB

    app = create_app()
    yield app
    pool: TimescaleDB = app.config["DB_POOL"]
    pool.truncate_events()


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()
