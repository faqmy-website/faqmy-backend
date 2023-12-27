import json
import uuid

import pytest

from faqmy_backend.services.bot import BotSDK


@pytest.fixture
async def bot_sdk(stack) -> BotSDK:
    yield BotSDK(stack.id)


async def test_create_document(bot_sdk, httpx_mock):
    mocked_id = str(uuid.uuid4())
    httpx_mock.add_response(
        url=bot_sdk.url_prefix,
        method="POST",
        content=json.dumps({"id": mocked_id}).encode(),
    )
    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/" + mocked_id,
        method="GET",
        content=json.dumps(
            {
                "id": mocked_id,
                "content": "Content of my doc",
                "meta": {
                    "name": "my-doc",
                },
            }
        ).encode(),
    )

    doc_id = await bot_sdk.create_document("my-doc", "Content of my doc")
    doc = await bot_sdk.get_document(doc_id)

    assert all(
        (
            doc["id"] == doc_id,
            doc["content"] == "Content of my doc",
            doc["meta"]["name"] == "my-doc",
        )
    )


async def test_delete_document(bot_sdk, httpx_mock):
    mocked_id = str(uuid.uuid4())

    httpx_mock.add_response(
        url=bot_sdk.url_prefix,
        method="POST",
        content=json.dumps({"id": mocked_id}).encode(),
    )

    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/" + mocked_id,
        method="GET",
        content=json.dumps({"id": mocked_id}).encode(),
    )

    doc_id = await bot_sdk.create_document("my-doc", "Content of my doc")
    assert "id" in await bot_sdk.get_document(doc_id)

    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/" + mocked_id + "/delete",
        method="GET",
        content=json.dumps({"status": "document deleted"}).encode(),
    )
    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/" + mocked_id,
        method="GET",
        content=json.dumps({"error": "Document not found"}).encode(),
    )

    await bot_sdk.delete_document(doc_id)
    assert await bot_sdk.get_document(doc_id) == {
        "error": "Document not found"
    }


async def test_ask(bot_sdk, httpx_mock):
    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/ask",
        method="POST",
        content=b'"We accept all major credit cards, including AmEx."',
    )

    answer = await bot_sdk.ask("Do you accept AmEx?")
    assert answer == "We accept all major credit cards, including AmEx."
