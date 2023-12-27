from sqlalchemy import select
from sqlalchemy.orm import joinedload

from faqmy_backend.db.models.conversations import (
    Conversation,
    Message,
    MessageTypeEnum,
)
from faqmy_backend.db.models.stack import Stack
from faqmy_backend.db.repositories.base import BaseRepository, Model


class MessageRepository(BaseRepository[Message]):
    model = Message

    async def create_message(self, conversation_id: str, text: str) -> Model:
        return await self._insert(
            conversation_id=conversation_id,
            text=text,
            who=MessageTypeEnum.user,
        )

    async def reply_message(self, message_id: str, text: str) -> Model:
        parent = await self._select_one(Message.id == message_id)
        reply = await self._insert(
            conversation_id=parent.conversation_id,
            parent_id=parent.id,
            text=text,
            who=MessageTypeEnum.bot,
        )
        return await self._find_message(Message.id == reply.id)

    async def get_by_parent_id(self, parent_id: str) -> Model:
        return await self._find_message(Message.parent_id == parent_id)

    async def _find_message(self, *cond):
        query = (
            select(Message)
            .options(joinedload(Message.parent))
            .join(Conversation)
            .join(Stack)
            .filter(*cond)
        )
        res = await self._execute(query)
        return res.scalar()

    async def get_by_conversation(self, conversation_id: str) -> list[Model]:
        return await self.get_msg_list(conversation_id)

    async def get_by_conversation_sealed(
        self, conversation_id: str, password: str
    ) -> list[Model]:
        return await self.get_msg_list(
            conversation_id, Conversation.password == password
        )

    async def get_msg_list(self, conversation_id: str, *cond) -> list[Model]:
        query = (
            select(Message)
            .join(Conversation)
            .filter(Message.conversation_id == conversation_id, *cond)
            .order_by(Message.created_at)
        )
        res = await self._execute(query)
        return res.scalars().all()
