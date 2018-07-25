from typing import Any
import threading
import sqlalchemy as sa
import sqlalchemy.orm
from szurubooru import config

# pylint: disable=invalid-name
_data = threading.local()
_engine = sa.create_engine(config.config['database'])  # type: Any
sessionmaker = sa.orm.sessionmaker(bind=_engine, autoflush=False)  # type: Any
session = sa.orm.scoped_session(sessionmaker)  # type: Any


def get_session() -> Any:
    global session
    return session


def set_sesssion(new_session: Any) -> None:
    global session
    session = new_session


def reset_query_count() -> None:
    _data.query_count = 0


def get_query_count() -> int:
    return _data.query_count


def _bump_query_count() -> None:
    _data.query_count = getattr(_data, 'query_count', 0) + 1


sa.event.listen(_engine, 'after_execute', lambda *args: _bump_query_count())
