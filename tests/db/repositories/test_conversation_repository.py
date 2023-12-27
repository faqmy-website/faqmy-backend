import pytest

from faqmy_backend.db.exceptions import DatabaseError


async def test_create_new_conversation(conversation_repo, stack):
    conv = await conversation_repo.create(stack.id)
    assert all((conv.id, conv.password))


async def test_create_wrong_stack_id(conversation_repo):
    with pytest.raises(DatabaseError):
        await conversation_repo.create("it's a wrong id")


async def test_delete_conversation(conversation_repo, stack):
    conv = await conversation_repo.create(stack.id)
    await conversation_repo.delete(conv.id)

    with pytest.raises(DatabaseError):
        await conversation_repo.get_by_id(conv.id)
