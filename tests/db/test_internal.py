import pytest
from sqlalchemy import select

from faqmy_backend.db.models.users import User


@pytest.mark.asyncio
async def test_orm_async_session_works(session):
    async with session:
        original_user = User(email="john.example.com", hashed_password="!")
        session.add(original_user)
        await session.commit()
        user_id = original_user.id

    async with session:
        fetched_user = (await session.execute(select(User))).scalar()
        assert fetched_user.id == user_id
        assert fetched_user.email == original_user.email


# Internal tests to make sure fixtures create objects inside  nested
# transactions and gracefully roll back on the finish


async def test_fixture_rolling_back_when_teardown_1(user):
    assert user.id


async def test_fixture_rolling_back_when_teardown_2(user):
    assert user.id


async def test_fixture_rolling_back_when_teardown_3(user, stack):
    assert user.id
    assert stack.id
