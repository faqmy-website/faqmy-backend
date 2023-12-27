import pytest
from fastapi import status

from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.services.bot import BotSDK


async def test_get_stack_detail(client, stack):
    resp = await client.get("/v1/client/stacks/" + stack.id)
    assert all(
        (
            resp.status_code == status.HTTP_200_OK,
            resp.json()["id"] == stack.id,
        )
    )


async def test_get_stack_detail_wrong(client):
    resp = await client.get("/v1/client/stacks/unpredictable-shit")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_post_conversations(client, stack):
    resp = await client.post(
        "/v1/client/conversations", json={"stack_id": stack.id}
    )
    assert all(
        (
            resp.status_code == status.HTTP_201_CREATED,
            resp.json()["stack_id"] == stack.id,
            resp.json()["password"],
        )
    )


@pytest.mark.parametrize(
    argnames="params, expected_code, found",
    argvalues=[
        ({}, 422, False),
        ({"conversation_id": "ok"}, 422, False),
        ({"conversation_id": "ok", "password": "ok"}, 200, True),
        ({"conversation_id": "ok", "password": "wrong"}, 200, False),
        ({"conversation_id": "bad", "password": "wrong"}, 200, False),
    ],
)
async def test_list_messages(
    client,
    stack,
    params,
    found,
    session,
    expected_code,
):
    conversation = await ConversationRepository(session).create(stack.id)

    message = await MessageRepository(session).create_message(
        conversation_id=conversation.id, text="Hi"
    )

    if params.get("conversation_id") == "ok":
        params["conversation_id"] = conversation.id
    if params.get("password") == "ok":
        params["password"] = conversation.password

    resp = await client.get("/v1/client/messages", params=params)

    assert resp.status_code == expected_code

    if found:
        assert resp.json()[0]["id"] == message.id
    elif resp.status_code < 400:
        assert resp.json() == []
    else:
        assert "detail" in resp.json()


async def test_create_message(client, stack, session, httpx_mock):
    httpx_mock.add_response(
        url=BotSDK(stack.id).url_prefix + "/ask",
        method="POST",
        content='"I\'m soo good"'.encode(),
    )
    conversation = await ConversationRepository(session).create(stack.id)
    resp = await client.post(
        "/v1/client/messages",
        json={
            "conversation_id": conversation.id,
            "text": "Hello how are you?",
        },
    )
    assert all(
        (
            resp.status_code == status.HTTP_201_CREATED,
            resp.json()["id"],
            resp.json()["text"] == "Hello how are you?",
        )
    )


async def test_create_message_creates_reply(
    client, stack, session, httpx_mock
):
    conversation = await ConversationRepository(session).create(stack.id)

    httpx_mock.add_response(
        url=BotSDK(stack.id).url_prefix + "/ask",
        method="POST",
        content='"I\'m soo good"'.encode(),
    )

    resp = await client.post(
        "/v1/client/messages",
        json={
            "conversation_id": conversation.id,
            "text": "Hello how are you?",
        },
    )

    message_id = resp.json()["id"]

    reply = await MessageRepository(session).get_by_parent_id(message_id)

    assert reply.parent_id == message_id
