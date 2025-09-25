from __future__ import annotations

import os
from typing import Iterator

import pytest

from analytics_backend.app import create_app
from analytics_backend.db import TimescaleDB


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
        missing_list = ", ".join(sorted(missing))
        raise RuntimeError(
            "Tests require the database containers to be running. Missing "
            f"variables: {missing_list}"
        )

    app = create_app()
    yield app
    pool: TimescaleDB = app.config["DB_POOL"]
    pool.truncate_events()


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()
