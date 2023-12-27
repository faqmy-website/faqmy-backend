import pytest


@pytest.fixture
async def conversation(conversation_repo, stack):
    yield await conversation_repo.create(stack.id)


async def test_create_message(conversation, message_repo):
    msg = await message_repo.create_message(
        conversation_id=conversation.id, text="Hi, I to buy some stuff"
    )
    assert all((msg.id, msg.conversation == conversation, msg.who == "user"))


async def test_reply_message(conversation, message_repo):
    msg = await message_repo.create_message(
        conversation_id=conversation.id, text="Hi, I to buy some stuff"
    )
    reply = await message_repo.reply_message(
        message_id=msg.id,
        text="Sure, please browse our offers",
    )

    assert all(
        (
            reply.id,
            reply.conversation == conversation,
            reply.parent == msg,
            reply.who == "bot",
        )
    )


async def test_list(conversation_repo, message_repo, stack):
    conv_1 = await conversation_repo.create(stack.id)
    conv_2 = await conversation_repo.create(stack.id)

    msg_1 = await message_repo.create_message(conv_1.id, "Message in conv #1")
    msg_2 = await message_repo.create_message(conv_2.id, "Message in conv #2")

    message_list = await message_repo.get_by_conversation(conv_1.id)

    assert all((msg_1 in message_list, msg_2 not in message_list))


async def test_list_sealed(conversation_repo, message_repo, stack):
    conv_1 = await conversation_repo.create(stack.id)
    conv_2 = await conversation_repo.create(stack.id)

    msg_1 = await message_repo.create_message(conv_1.id, "Message in conv #1")
    msg_2 = await message_repo.create_message(conv_2.id, "Message in conv #2")

    message_list = await message_repo.get_by_conversation_sealed(
        conversation_id=conv_1.id, password=conv_1.password
    )

    assert all((msg_1 in message_list, msg_2 not in message_list))


async def test_list_sealed_wrong_password(
    conversation_repo, message_repo, stack
):
    conv_1 = await conversation_repo.create(stack.id)
    conv_2 = await conversation_repo.create(stack.id)

    msg_1 = await message_repo.create_message(conv_1.id, "Message in conv #1")
    msg_2 = await message_repo.create_message(conv_2.id, "Message in conv #2")

    message_list = await message_repo.get_by_conversation_sealed(
        conversation_id=conv_1.id, password="wrong password"
    )

    assert all((msg_1 not in message_list, msg_2 not in message_list))
