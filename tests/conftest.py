import pathlib

import pytest
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from faqmy_backend.conf import settings
from faqmy_backend.db import connection
from faqmy_backend.db.metadata import metadata
from faqmy_backend.db.models.stack import Stack
from faqmy_backend.db.models.users import User
from faqmy_backend.db.utils import normalize_pg_url


@pytest.fixture
def test_root() -> pathlib.Path:
    return pathlib.Path(__file__).parent


@pytest.fixture(scope="session")
def database_url():
    image = "postgres:15.2-alpine"

    with PostgresContainer(image) as container:
        yield container.get_connection_url()


@pytest.fixture(scope="session")
def pg_create_schema(database_url):
    engine = connection.create_engine(database_url, echo=settings.db.echo)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


@pytest.fixture
async def session(pg_create_schema, database_url):
    engine = create_async_engine(
        normalize_pg_url(database_url, asynchronous=True)
    )
    conn_ = await engine.connect()
    session: AsyncSession = sessionmaker(
        bind=conn_,
        expire_on_commit=False,
        class_=AsyncSession,
    )()

    await conn_.begin_nested()

    @listens_for(session.sync_session, "after_transaction_end")
    def end_savepoint(*args, **kwargs):
        if not conn_.closed and not conn_.in_nested_transaction():
            conn_.sync_connection.begin_nested()

    yield session

    if session.in_transaction():
        await session.rollback()
    await conn_.close()


@pytest.fixture
async def user(session):
    user = User(email="john@example.com", hashed_password="!")
    session.add(user)
    await session.commit()
    yield user


@pytest.fixture
async def stack(session, user):
    stack = Stack(user=user, name="My Stack")
    session.add(stack)
    await session.commit()
    yield stack


@pytest.fixture
def dependency_overrides():
    """
    A tool to override FastAPI dependencies
    """

    class DependencyOverrider:
        def __init__(self, app, overrides):
            self.overrides = overrides
            self.app = app

        def __enter__(self):
            for dep, new_dep in self.overrides.items():
                self.app.dependency_overrides[dep] = new_dep
            return self

        def __exit__(self, *args) -> None:
            for dep in self.overrides.keys():
                del self.app.dependency_overrides[dep]

    yield lambda app, overrides: DependencyOverrider(app, overrides)
