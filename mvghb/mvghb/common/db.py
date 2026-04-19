"""SQLAlchemy engine + session for noc-gov."""
from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from mvghb.common.settings import get_settings


@lru_cache(maxsize=1)
def _engine() -> Engine:
    return create_engine(
        get_settings().gov_dsn,
        pool_pre_ping=True,
        future=True,
    )


@lru_cache(maxsize=1)
def _Sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=_engine(), expire_on_commit=False, future=True)


@contextmanager
def gov_session() -> Iterator[Session]:
    s = _Sessionmaker()()
    try:
        yield s
    finally:
        s.close()


def reset_engine_cache() -> None:
    _engine.cache_clear()
    _Sessionmaker.cache_clear()
