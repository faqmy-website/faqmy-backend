import json

import httpx
import pytest
from fastapi import status
from fastapi_users.jwt import generate_jwt

from faqmy_backend.conf import settings
from faqmy_backend.db.models import Card, Stack, User
from faqmy_backend.db.repositories.cards import CardRepository
from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.services.bot import BotSDK


@pytest.fixture
def jwt_token(user):
    yield generate_jwt(
        data={"sub": str(user.id), "aud": ["fastapi-users:auth"]},
        secret=settings.users.jwt_secret,
        lifetime_seconds=settings.users.jwt_lifetime_seconds,
    )


@pytest.fixture
async def client(client, jwt_token) -> httpx.AsyncClient:
    client.headers["Authorization"] = "Bearer " + jwt_token
    yield client


async def test_create_stack(client):
    resp = await client.post("/v1/dashboard/stacks", json={"name": "MY STACK"})
    assert all(
        (
            resp.status_code == status.HTTP_201_CREATED,
            resp.json()["name"] == "MY STACK",
            resp.json()["id"],
        )
    )


async def test_get_stack_detail(client, stack):
    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert all(
        (
            resp.status_code == status.HTTP_200_OK,
            resp.json()["id"] == stack.id,
        )
    )


async def test_delete_stack(client, stack):
    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert resp.status_code == status.HTTP_200_OK

    await client.delete("/v1/dashboard/stacks/" + stack.id)

    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_stack_cascade(client, stack, session):
    for i in range(2):
        conv = await ConversationRepository(session).create(stack.id)
        for j in range(1, 4):
            await MessageRepository(session).create_message(
                conversation_id=conv.id, text="Message #" + str(j)
            )
        for k in range(1, 3):
            await CardRepository(session).create(
                stack_id=stack.id,
                question="Question #" + str(k),
                answer="Answer #" + str(k),
            )

    await session.commit()
    await client.delete("/v1/dashboard/stacks/" + stack.id)

    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_cannot_delete_foreign_stack(client, session):
    stack = Stack(
        user=User(email="jane@example.com", hashed_password="!"),
        name="My Stack",
    )
    session.add(stack)
    await session.commit()

    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_edit_stack_regression_zero_delay(client, stack):
    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert resp.json()["widget_delay"] == 3

    resp = await client.patch(
        "/v1/dashboard/stacks/" + stack.id,
        json={
            "name": "asdfasd",
            "delay": 0,
        },
    )
    assert resp.json()["widget_delay"] == 0

    resp = await client.get("/v1/dashboard/stacks/" + stack.id)
    assert resp.json()["widget_delay"] == 0
