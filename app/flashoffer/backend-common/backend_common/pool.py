# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Connection pooling primitives for backend services."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from psycopg import conninfo
from psycopg_pool import ConnectionPool

from .config import DatabaseConfig


class PostgresPool:
    """Simple connection pool wrapper around psycopg."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        dsn = conninfo.make_conninfo(**config.connection_kwargs())
        self._pool = ConnectionPool(
            conninfo=dsn,
            min_size=config.minconn,
            max_size=config.maxconn,
        )

    @contextmanager
    def connection(self) -> Iterator:
        with self._pool.connection() as conn:
            yield conn

    def close(self) -> None:
        self._pool.close()

    def initialize(self) -> None:  # pragma: no cover - optional override
        """Hook for subclasses that need to ensure schema state."""


__all__ = ["PostgresPool"]
