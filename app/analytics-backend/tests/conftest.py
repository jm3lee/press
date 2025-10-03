"""Test configuration for analytics-backend unit and integration suites."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
