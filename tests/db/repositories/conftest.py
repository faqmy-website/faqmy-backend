import pytest

from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.db.repositories.stack import StackRepository


@pytest.fixture
async def conversation_repo(session) -> ConversationRepository:
    yield ConversationRepository(session)


@pytest.fixture
async def message_repo(session) -> MessageRepository:
    yield MessageRepository(session)


@pytest.fixture
async def stack_repo(session) -> StackRepository:
    yield StackRepository(session)
