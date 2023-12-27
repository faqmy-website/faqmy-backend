import json

from fastapi import status

from faqmy_backend.services.bot import BotSDK


async def test_create_card(client, stack):
    resp = await client.post(
        "/v1/dashboard/cards",
        json={
            "stack_id": stack.id,
            "question": "To be or not to be?",
            "answer": "That is the question",
        },
    )
    assert all(
        (
            resp.status_code == status.HTTP_201_CREATED,
            resp.json()["question"] == "To be or not to be?",
            resp.json()["answer"] == "That is the question",
            resp.json()["id"],
        )
    )


async def test_edit_card(client, stack, session):
    resp = await client.post(
        "/v1/dashboard/cards",
        json={
            "stack_id": stack.id,
            "question": "To be or not to be?",
            "answer": "That is the question",
        },
    )
    card_id = resp.json()["id"]

    resp = await client.patch(
        "/v1/dashboard/cards/" + card_id,
        json={
            "stack_id": stack.id,
            "question": "How many roads must a man walk down?",
            "answer": "The answer, my friend, is blowin' in the wind",
        },
    )

    assert all(
        (
            resp.status_code == status.HTTP_200_OK,
            resp.json()["question"] == "How many roads must a man walk down?",
            resp.json()["answer"]
            == ("The answer, my friend, is blowin' in the wind"),
            resp.json()["id"] == card_id,
        )
    )


async def test_edit_card_learned(
    client, stack, session, httpx_mock, card_repo_dep
):
    bot_sdk = BotSDK(stack.id)

    resp = await client.post(
        "/v1/dashboard/cards",
        json={
            "stack_id": stack.id,
            "question": "To be or not to be?",
            "answer": "That is the question",
        },
    )
    card_id = resp.json()["id"]

    httpx_mock.add_response(
        url=bot_sdk.url_prefix,
        method="POST",
        content=json.dumps({"id": "es_doc_id_old"}).encode(),
    )
    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/es_doc_id_old/delete",
        method="GET",
        content=json.dumps({"status": "document deleted"}).encode(),
    )

    # Made the card 'learned'
    resp = await client.post("/v1/dashboard/cards/" + card_id + "/learn")
    assert resp.status_code == status.HTTP_202_ACCEPTED

    card_model = await card_repo_dep.get_by_id(card_id)
    assert card_model.es_doc_id == "es_doc_id_old"

    # Now, re-mock 'create document' bot endpoint to get a new DOC ID
    httpx_mock.add_response(
        url=bot_sdk.url_prefix,
        method="POST",
        content=json.dumps({"id": "es_doc_id_new"}).encode(),
    )

    # Then edit it.
    resp = await client.patch(
        "/v1/dashboard/cards/" + card_id,
        json={
            "stack_id": stack.id,
            "question": "How many roads must a man walk down?",
            "answer": "The answer, my friend, is blowin' in the wind",
        },
    )

    card_model = await card_repo_dep.get_by_id(card_id)

    assert all(
        (
            card_model.es_doc_id == "es_doc_id_new",
            resp.status_code == status.HTTP_200_OK,
            resp.json()["question"] == "How many roads must a man walk down?",
            resp.json()["answer"]
            == ("The answer, my friend, is blowin' in the wind"),
            resp.json()["id"] == card_id,
        )
    )


async def test_delete_card(client, stack, session):
    resp = await client.post(
        "/v1/dashboard/cards",
        json={
            "stack_id": stack.id,
            "question": "To be or not to be?",
            "answer": "That is the question",
        },
    )

    card_id = resp.json()["id"]

    resp = await client.delete("/v1/dashboard/cards/" + card_id)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = await client.get("/v1/dashboard/cards/" + card_id)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_delete__learned_card(client, stack, session, httpx_mock):
    bot_sdk = BotSDK(stack.id)

    resp = await client.post(
        "/v1/dashboard/cards",
        json={
            "stack_id": stack.id,
            "question": "To be or not to be?",
            "answer": "That is the question",
        },
    )

    card_id = resp.json()["id"]

    httpx_mock.add_response(
        url=bot_sdk.url_prefix,
        method="POST",
        content=json.dumps({"id": card_id}).encode(),
    )

    httpx_mock.add_response(
        url=bot_sdk.url_prefix + "/" + card_id + "/delete",
        method="GET",
        content=json.dumps({"status": "document deleted"}).encode(),
    )

    resp = await client.post("/v1/dashboard/cards/" + card_id + "/learn")
    assert resp.status_code == status.HTTP_202_ACCEPTED

    resp = await client.delete("/v1/dashboard/cards/" + card_id)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = await client.get("/v1/dashboard/cards/" + card_id)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_upload_file(
    client, stack, session, test_root, httpx_mock, card_repo_dep
):
    bot_sdk = BotSDK(stack.id)

    httpx_mock.add_response(
        method="post",
        url=bot_sdk.upload_url,
        content=json.dumps(
            [
                {"id": "1", "name": "Question 1", "content": "Answer 1"},
                {"id": "2", "name": "Question 2", "content": "Answer 3"},
                {"id": "3", "name": "Question 3", "content": "Answer 3"},
            ]
        ).encode(),
    )

    file_to_upload = test_root / "assets" / "sample.pdf"

    assert not await card_repo_dep.get_by_stack_id(stack.id)

    with file_to_upload.open("rb") as fp:
        resp = await client.post(
            url="/v1/dashboard/cards/_upload",
            data={"stack_id": stack.id},
            files={"file": fp},
        )
        assert resp.status_code == status.HTTP_202_ACCEPTED
        assert len(await card_repo_dep.get_by_stack_id(stack.id)) == 3


async def test_scrape_url(
    client, stack, session, test_root, httpx_mock, card_repo_dep
):
    bot_sdk = BotSDK(stack.id)

    httpx_mock.add_response(
        method="post",
        url=bot_sdk.scrape_url,
        content=json.dumps(
            [
                {"id": "1", "name": "Question 1", "content": "Answer 1"},
                {"id": "2", "name": "Question 2", "content": "Answer 3"},
            ]
        ).encode(),
    )

    assert not await card_repo_dep.get_by_stack_id(stack.id)

    resp = await client.post(
        url="/v1/dashboard/cards/_url",
        json={
            "stack_id": stack.id,
            "url": "https://libraryofbabel.info/book.cgi",
        },
    )
    assert resp.status_code == status.HTTP_202_ACCEPTED
    assert len(await card_repo_dep.get_by_stack_id(stack.id)) == 2
