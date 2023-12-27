import fastapi
import httpx
import pytest

from faqmy_backend.app.builder import build_app
from faqmy_backend.app.dependencies import (
    CardRepositoryDependMarker,
    ConversationRepositoryDependMarker,
    GetDbDependMarker,
    MessageRepositoryDependMarker,
    StackRepositoryDependMarker,
    UserDbMarker,
)
from faqmy_backend.app.routes import client as client_routes
from faqmy_backend.db.repositories.cards import CardRepository
from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.db.repositories.stack import StackRepository


@pytest.fixture
def get_db_dep(session):
    return session


@pytest.fixture
def conversation_repo_dep(session):
    return ConversationRepository(session)


@pytest.fixture
def message_repo_dep(session):
    return MessageRepository(session)


@pytest.fixture
def stack_repo_dep(session):
    return StackRepository(session)


@pytest.fixture
def card_repo_dep(session):
    return CardRepository(session)


@pytest.fixture(name="app")
def app_fixture(
    session,
    dependency_overrides,
    get_db_dep,
    message_repo_dep,
    conversation_repo_dep,
    stack_repo_dep,
    card_repo_dep,
    monkeypatch,
) -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    app = build_app(app)

    monkeypatch.setattr(client_routes, "create_session", lambda: get_db_dep)

    with dependency_overrides(
        app,
        {
            UserDbMarker: lambda: get_db_dep,
            GetDbDependMarker: lambda: get_db_dep,
            ConversationRepositoryDependMarker: lambda: conversation_repo_dep,
            MessageRepositoryDependMarker: lambda: message_repo_dep,
            StackRepositoryDependMarker: lambda: stack_repo_dep,
            CardRepositoryDependMarker: lambda: card_repo_dep,
        },
    ):
        yield app


@pytest.fixture
def app_domain_name() -> str:
    return "faqmy"


@pytest.fixture
async def client(app, app_domain_name) -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        app=app, base_url="http://" + app_domain_name
    ) as ac:
        yield ac


@pytest.fixture
def non_mocked_hosts(app_domain_name) -> list:
    return [app_domain_name]
