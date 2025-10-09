# Copyright (c) Flashoffer Developers
# Released under the MIT license.

import os
from typing import Dict, Iterator

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

    os.environ.setdefault("CAMPAIGN_MANAGER_SECRET_KEY", "campaign-test-secret")

    app = create_app()
    yield app
    store: CampaignStore = app.config["DB_POOL"]
    with store.connection() as conn:  # type: ignore[assignment]
        with conn.cursor() as cur:
            cur.execute("TRUNCATE campaign")
        conn.commit()


@pytest.fixture()
def auth_headers(flask_app) -> Dict[str, str]:
    manager = flask_app.config["AUTH_MANAGER"]
    token, _ = manager.issue_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def client(flask_app, auth_headers):
    client = flask_app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = auth_headers["Authorization"]
    return client
