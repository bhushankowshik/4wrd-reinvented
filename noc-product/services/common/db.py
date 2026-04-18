from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from services.common.settings import get_settings


_data_engine: Engine | None = None
_gov_engine: Engine | None = None
_DataSession: sessionmaker[Session] | None = None
_GovSession: sessionmaker[Session] | None = None


def data_engine() -> Engine:
    global _data_engine, _DataSession
    if _data_engine is None:
        s = get_settings()
        _data_engine = create_engine(s.noc_data_dsn, pool_pre_ping=True, future=True)
        _DataSession = sessionmaker(bind=_data_engine, expire_on_commit=False)
    return _data_engine


def gov_engine() -> Engine:
    global _gov_engine, _GovSession
    if _gov_engine is None:
        s = get_settings()
        _gov_engine = create_engine(s.noc_gov_dsn, pool_pre_ping=True, future=True)
        _GovSession = sessionmaker(bind=_gov_engine, expire_on_commit=False)
    return _gov_engine


@contextmanager
def data_session() -> Iterator[Session]:
    data_engine()
    assert _DataSession is not None
    with _DataSession() as s:
        yield s


@contextmanager
def gov_session() -> Iterator[Session]:
    gov_engine()
    assert _GovSession is not None
    with _GovSession() as s:
        yield s
