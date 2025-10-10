# Copyright (c) Flashoffer Developers
# Released under the MIT license.

"""Connection pooling primitives for backend services."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from psycopg_pool import SimpleConnectionPool

from .config import DatabaseConfig


class PostgresPool:
    """Simple connection pool wrapper around psycopg."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._pool = SimpleConnectionPool(
            config.minconn,
            config.maxconn,
            **config.connection_kwargs(),
        )

    @contextmanager
    def connection(self) -> Iterator:
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    def close(self) -> None:
        self._pool.closeall()

    def initialize(self) -> None:  # pragma: no cover - optional override
        """Hook for subclasses that need to ensure schema state."""


__all__ = ["PostgresPool"]
