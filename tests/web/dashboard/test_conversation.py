from fastapi import status

from faqmy_backend.db.repositories.conversation import ConversationRepository


async def test_delete_conversation(client, stack, session):
    conv = await ConversationRepository(session).create(stack.id)
    await client.delete("/v1/dashboard/conversations/" + conv.id)

    resp = await client.get("/v1/dashboard/conversations/" + conv.id)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
