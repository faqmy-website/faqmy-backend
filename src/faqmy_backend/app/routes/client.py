from fastapi import APIRouter, Depends, status
from fastapi.background import BackgroundTasks

from faqmy_backend.app.dependencies import (
    ConversationRepositoryDependMarker,
    MessageRepositoryDependMarker,
    StackRepositoryDependMarker,
)
from faqmy_backend.app.responses import err
from faqmy_backend.app.schemas import (
    Conversation,
    ConversationIn,
    Message,
    MessageIn,
    StackPublic,
)
from faqmy_backend.db.connection import create_session
from faqmy_backend.db.exceptions import DatabaseError
from faqmy_backend.db.models.conversations import Message as MessageOrm
from faqmy_backend.db.repositories.cards import CardRepository
from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.db.repositories.stack import StackRepository
from faqmy_backend.services.bot import BotSDK

router = APIRouter()


async def generate_reply(
    message: MessageOrm,
) -> None:
    session = create_session()
    stack = await StackRepository(session).get_by_message_id(message.id)

    bot_sdk = BotSDK(stack.id)

    reply_msg = await MessageRepository(session).reply_message(
        message_id=message.id, text=await bot_sdk.ask(message.text)
    )

    await CardRepository(session).create(
        stack_id=stack.id,
        question=message.text,
        answer=reply_msg.text,
    )

    await session.commit()
    await session.close()
    del session


@router.get(
    "/stacks/{id}",
    summary="Get Stack details",
    response_model=StackPublic,
    status_code=status.HTTP_200_OK,
)
async def stack_detail(
    id: str,
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    """
    Get the stack details
    \f
    :param id:
    :param repo:
    :return:
    """
    stack = await repo.get_by_id(id)
    if stack is None:
        raise err("Stack not found", status_code=status.HTTP_404_NOT_FOUND)
    try:
        return StackPublic.from_orm(stack)
    except DatabaseError:
        raise err("Failed to get stack detail")


@router.post(
    "/conversations",
    summary="New Conversation",
    response_model=Conversation,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    spec: ConversationIn,
    repo: ConversationRepository = Depends(ConversationRepositoryDependMarker),
):
    """
    Create a new conversation inside the stack
    \f
    :param spec:
    :param repo:
    :return:
    """
    try:
        conv = await repo.create(spec.stack_id)
        await repo.commit()
        return Conversation.from_orm(conv)
    except DatabaseError:
        raise err("Failed to create a new conversation")


@router.get(
    "/messages", response_model=list[Message], summary="List of Messages"
)
async def get_messages(
    conversation_id: str,
    password: str,
    repo: MessageRepository = Depends(MessageRepositoryDependMarker),
):
    """
    Get all the messages inside the conversation
    \f
    :param conversation_id:
    :param password:
    :param repo:
    :return:
    """
    return await repo.get_by_conversation_sealed(
        conversation_id=conversation_id,
        password=password,
    )


@router.post(
    "/messages", response_model=Message, status_code=status.HTTP_201_CREATED
)
async def create_message(
    spec: MessageIn,
    background_tasks: BackgroundTasks,
    repo: MessageRepository = Depends(MessageRepositoryDependMarker),
):
    message = await repo.create_message(
        conversation_id=spec.conversation_id,
        text=spec.text,
    )
    await repo.commit()

    background_tasks.add_task(generate_reply, message=message)
    return message
