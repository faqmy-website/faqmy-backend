import shortuuid
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from faqmy_backend.db.exceptions import DatabaseError
from faqmy_backend.db.models.conversations import Conversation
from faqmy_backend.db.models.stack import Stack
from faqmy_backend.db.repositories.base import BaseRepository, Model


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    async def is_accessible_by_user(
        self, conversation_id: str, user_id: str
    ) -> bool:
        return (
            await self._execute(
                select(
                    select(Conversation.id)
                    .join(Stack)
                    .filter(
                        Conversation.id == conversation_id,
                        Stack.user_id == user_id,
                    )
                    .exists()
                )
            )
        ).scalar()

    async def create(self, stack_id: str) -> Model:
        return await self._insert(stack_id=stack_id, password=shortuuid.uuid())

    async def delete(self, id: str) -> Model:
        try:
            return await self._delete(Conversation.id == id)
        except (NoResultFound,) as exc_info:
            raise DatabaseError(exc_info)

    async def get_by_user_id(self, user_id: str) -> list[Model]:
        query = (
            select(Conversation, Stack)
            .join(Stack)
            .filter(Stack.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        res = await self._execute(query)
        return res.scalars().all()

    async def get_by_id(self, id: str) -> Model:
        query = (
            select(Conversation, Stack)
            .join(Stack)
            .filter(Conversation.id == id)
        )
        res = await self._execute(query)
        try:
            return res.scalars().one()
        except (NoResultFound,) as err:
            raise DatabaseError(err)
