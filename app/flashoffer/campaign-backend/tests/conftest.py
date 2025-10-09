# Copyright (c) Flashoffer Developers
# Released under the MIT license.

import os
from typing import Iterator

import pytest

from campaign_backend.app import create_app
from campaign_backend.db import CampaignStore


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
    store: CampaignStore = app.config["DB_POOL"]
    with store.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute("TRUNCATE campaign")
        conn.commit()


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()
