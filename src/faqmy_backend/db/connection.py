import typing

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from faqmy_backend.conf import settings
from faqmy_backend.db.utils import normalize_pg_url


def create_session_maker(
    url: str,
    *,
    echo: bool | None = None,
    engine: Engine | AsyncEngine | None = None,
    autoflush: bool = False,
    autocommit: bool = False,
    expire_on_commit: bool = False,
    future: bool = True,
    asynchronous: bool = False,
) -> typing.Callable[[...], Session | AsyncSession]:
    return sessionmaker(
        bind=engine
        or create_sqlalchemy_engine(
            url,
            echo=echo,
            future=future,
            asynchronous=asynchronous,
        ),
        class_=AsyncSession if asynchronous else Session,
        autocommit=autocommit,
        autoflush=autoflush,
        expire_on_commit=expire_on_commit,
    )


def create_sqlalchemy_engine(
    url: str,
    echo: bool | None = None,
    asynchronous: bool | None = None,
    future: bool = True,
):
    engine_factory = create_async_engine if asynchronous else create_engine

    return engine_factory(
        normalize_pg_url(url, asynchronous),
        echo=(echo if echo is not None else settings.db.echo),
        future=future,
        pool_size=10,
    )


create_session = create_session_maker(
    settings.db.url, echo=settings.db.echo, asynchronous=True
)
