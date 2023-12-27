from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from faqmy_backend.app.dependencies import (
    CardRepositoryDependMarker,
    ConversationRepositoryDependMarker,
    MessageRepositoryDependMarker,
    StackRepositoryDependMarker,
)
from faqmy_backend.app.responses import err
from faqmy_backend.app.schemas import (
    Card,
    CardIn,
    CardUrlIn,
    ConversationDashboard,
    Message,
    Stack,
    StackIn,
)
from faqmy_backend.db.exceptions import DatabaseError
from faqmy_backend.db.models.users import User
from faqmy_backend.db.repositories.cards import CardRepository
from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.db.repositories.stack import StackRepository
from faqmy_backend.services.bot import BotSDK
from faqmy_backend.users.manager import fastapi_users

router = APIRouter()
current_user = fastapi_users.current_user()


@router.get("/stacks", summary="Stack List", response_model=list[Stack])
async def stack_list(
    user: User = Depends(current_user),
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    return await repo.get_by_user_id(user.id)


@router.post(
    "/stacks",
    summary="New Stack",
    response_model=Stack,
    status_code=status.HTTP_201_CREATED,
)
async def stack_create(
    spec: StackIn,
    user: User = Depends(current_user),
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    """
    Create a new Stack
    """
    stack = await repo.create(
        user_id=user.id,
        name=spec.name,
        description=spec.description,
        initial_question=spec.initial_question,
        widget_delay=spec.widget_delay,
        color=spec.color,
    )
    await repo.commit()
    return stack


@router.get("/stacks/{id}", summary="Get Stack details", response_model=Stack)
async def stack_detail(
    id: str,
    user: User = Depends(current_user),
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    """
    Get the stack details
    \f
    :param id:
    :param user:
    :param repo:
    :return:
    """
    if not await repo.is_accessible_by_user(id, user.id):
        raise err("Failed to get stack detail", status.HTTP_404_NOT_FOUND)
    return Stack.from_orm(await repo.get_by_id(id))


@router.delete("/stacks/{id}", summary="Remove Stack")
async def stack_delete(
    id: str,
    user: User = Depends(current_user),
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    """
    Remove the stack completely
    \f
    :param id:
    :param user:
    :param repo:
    :return:
    """
    if not await repo.is_accessible_by_user(id, user.id):
        raise err("Failed to delete the stack", status.HTTP_404_NOT_FOUND)
    await repo.delete(id)
    await repo.commit()


@router.patch(
    "/stacks/{id}", summary="Update Stack settings", response_model=Stack
)
async def stack_update(
    id: str,
    spec: StackIn,
    user: User = Depends(current_user),
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    """
    Update stack settings
    \f
    :param id:
    :param spec:
    :param user:
    :param repo:
    :return:
    """
    if not await repo.is_accessible_by_user(id, user.id):
        raise err("Failed to update the stack", status.HTTP_404_NOT_FOUND)

    stack = await repo.get_by_id(id)
    await repo.update(
        stack_id=stack.id,
        user_id=user.id,
        name=spec.name,
        description=spec.description,
        initial_question=spec.initial_question,
        widget_delay=spec.widget_delay,
        color=spec.color,
    )
    await repo.commit()
    return Stack.from_orm(stack)


@router.get("/cards", summary="Card List", response_model=list[Card])
async def card_list(
    stack_id: str,
    learned: bool | None = None,
    user: User = Depends(current_user),
    stack_repo: StackRepository = Depends(StackRepositoryDependMarker),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    if not await stack_repo.is_accessible_by_user(stack_id, user.id):
        raise err("Stack not found", status_code=status.HTTP_404_NOT_FOUND)
    return await card_repo.get_by_stack_id(stack_id, learned=learned)


@router.post(
    "/cards",
    summary="New Card",
    response_model=Card,
    status_code=status.HTTP_201_CREATED,
)
async def card_create(
    spec: CardIn,
    user: User = Depends(current_user),
    stack_repo: StackRepository = Depends(StackRepositoryDependMarker),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    if not await stack_repo.is_accessible_by_user(spec.stack_id, user.id):
        raise err("Stack not found", status_code=status.HTTP_404_NOT_FOUND)

    try:
        card = await card_repo.create(
            stack_id=spec.stack_id,
            question=spec.question,
            answer=spec.answer,
        )
    except DatabaseError as ex:
        raise err("Failed to create card")
    return card


@router.post(
    path="/cards/_upload",
    summary="Upload a File",
    status_code=status.HTTP_202_ACCEPTED,
)
async def card_create_from_upload(
    stack_id: str = Form(),
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    stack_repo: StackRepository = Depends(StackRepositoryDependMarker),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    """
    Create cards from an uploaded file
    \f
    :param stack_id:
    :param file:
    :param user:
    :param stack_repo:
    :param card_repo:
    :return:
    """
    if not await stack_repo.is_accessible_by_user(stack_id, user.id):
        raise err("Stack not found", status_code=status.HTTP_404_NOT_FOUND)

    for doc in await BotSDK(stack_id).upload(file):
        card = await card_repo.create(
            stack_id=stack_id,
            question=doc.name,
            answer=doc.content,
        )
        await card_repo.mark_learned(card.id, doc.id)

    await card_repo.commit()
    # return card


@router.post(
    path="/cards/_url",
    summary="Scan a URL",
    status_code=status.HTTP_202_ACCEPTED,
)
async def card_create_from_url(
    spec: CardUrlIn,
    user: User = Depends(current_user),
    stack_repo: StackRepository = Depends(StackRepositoryDependMarker),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    """
    Create cards from data crawled from the given URL
    \f
    :param spec:
    :param user:
    :param stack_repo:
    :param card_repo:
    :return:
    """
    if not await stack_repo.is_accessible_by_user(spec.stack_id, user.id):
        raise err("Stack not found", status_code=status.HTTP_404_NOT_FOUND)

    for doc in await BotSDK(spec.stack_id).scan(spec.url):
        card = await card_repo.create(
            stack_id=spec.stack_id,
            question=doc.name,
            answer=doc.content,
        )
        await card_repo.mark_learned(card.id, doc.id)

    await card_repo.commit()


@router.get("/cards/{id}", summary="Get Card Detail", response_model=Card)
async def card_detail(
    id: str,
    user: User = Depends(current_user),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    if not await card_repo.is_accessible_by_user(id, user.id):
        raise err("Card not found", status_code=status.HTTP_404_NOT_FOUND)

    # Assume it won't be a NULL, cuz we just checked accessible
    return await card_repo.get_by_id(id)


@router.patch(
    "/cards/{id}",
    summary="Update Card",
    response_model=Card,
)
async def card_update(
    id: str,
    spec: CardIn,
    user: User = Depends(current_user),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    if not await card_repo.is_accessible_by_user(id, user.id):
        raise err("Card not found", status_code=status.HTTP_404_NOT_FOUND)

    await card_repo.update(
        card_id=id,
        question=spec.question,
        answer=spec.answer,
    )

    card = await card_repo.get_by_id(id)
    bot_sdk = BotSDK(card.stack_id)

    if card.learned:
        await bot_sdk.delete_document(card.es_doc_id)
        await card_repo.mark_learned(
            card.id, await bot_sdk.create_document(card.question, card.answer)
        )

    return card


@router.delete(
    "/cards/{id}",
    summary="Remove Card",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def card_delete(
    id: str,
    user: User = Depends(current_user),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    """
    Remove the card
    \f
    :param id:
    :param user:
    :param card_repo:
    :return:
    """
    if not await card_repo.is_accessible_by_user(id, user.id):
        raise err("Card not found", status_code=status.HTTP_404_NOT_FOUND)

    card = await card_repo.get_by_id(id)
    await card_repo.delete(id)

    if card.learned:
        bot_sdk = BotSDK(card.stack_id)
        await bot_sdk.delete_document(card.es_doc_id)
    await card_repo.commit()

    return


@router.post(
    "/cards/{id}/learn",
    summary="Learn Card",
    status_code=status.HTTP_202_ACCEPTED,
)
async def card_learn(
    id: str,
    user: User = Depends(current_user),
    card_repo: CardRepository = Depends(CardRepositoryDependMarker),
):
    """
    Send the card to bot learning process
    \f
    :param id:
    :param user:
    :param card_repo:
    :return:
    """
    if not await card_repo.is_accessible_by_user(id, user.id):
        raise err("Card not found", status_code=status.HTTP_404_NOT_FOUND)

    card = await card_repo.get_by_id(id)

    es_doc_id = await BotSDK(card.stack_id).create_document(
        name=card.question,
        content=card.answer,
    )

    await card_repo.mark_learned(id, es_doc_id)
    await card_repo.commit()


@router.get(
    "/conversations",
    summary="Conversation List",
    response_model=list[ConversationDashboard],
)
async def conversation_list(
    user: User = Depends(current_user),
    repo: ConversationRepository = Depends(ConversationRepositoryDependMarker),
):
    return await repo.get_by_user_id(user.id)


@router.get("/conversations/{id}", summary="Get Conversation Detail")
async def conversation_detail(
    id: str,
    user: User = Depends(current_user),
    repo: ConversationRepository = Depends(ConversationRepositoryDependMarker),
):
    """
    Get detailed information about the conversation
    \f
    :param id:
    :param user:
    :param repo:
    :return:
    """
    if not await repo.is_accessible_by_user(id, user.id):
        raise err(
            "Conversation not found", status_code=status.HTTP_404_NOT_FOUND
        )
    return await repo.get_by_id(id)


@router.delete(
    "/conversations/{id}",
    summary="Remove a conversation",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def conversation_remove(
    id: str,
    user: User = Depends(current_user),
    repo: ConversationRepository = Depends(ConversationRepositoryDependMarker),
):
    """
    Remove the conversation
    \f
    :param id:
    :param user:
    :param repo:
    :return:
    """
    if not await repo.is_accessible_by_user(id, user.id):
        raise err(
            "Conversation not found", status_code=status.HTTP_404_NOT_FOUND
        )
    await repo.delete(id)
    await repo.commit()


@router.get(
    "/messages", response_model=list[Message], summary="List of Messages"
)
async def message_list(
    conversation_id: str,
    repo: MessageRepository = Depends(MessageRepositoryDependMarker),
):
    """
    Get all the messages inside the conversation
    \f
    :param conversation_id:
    :param repo:
    :return:
    """
    return await repo.get_by_conversation(conversation_id=conversation_id)
