from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from faqmy_backend.db.exceptions import DatabaseError
from faqmy_backend.db.models.conversations import Conversation, Message
from faqmy_backend.db.models.stack import Stack
from faqmy_backend.db.repositories.base import BaseRepository, Model

not_set = object()


class StackRepository(BaseRepository[Stack]):
    model = Stack

    async def is_accessible_by_user(self, stack_id: str, user_id: str) -> bool:
        return (
            await self._execute(
                select(
                    select(Stack.id)
                    .filter(Stack.id == stack_id, Stack.user_id == user_id)
                    .exists()
                )
            )
        ).scalar()

    async def create(
        self,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        initial_question: str | None = None,
        widget_delay: int | None = 3,
        color: str | None = None,
    ) -> Model:
        return await self._insert(
            user_id=user_id,
            name=name,
            description=description,
            initial_question=initial_question,
            widget_delay=widget_delay,
            color=color,
        )

    async def get_by_user_id(self, user_id: str) -> list[Model]:
        return await self._select_all(Stack.user_id == user_id)

    async def get_by_id(self, id: str, user_id: str | None = None) -> Model:
        conditions = [Stack.id == id]
        if user_id is not None:
            conditions.append(Stack.user_id == user_id)
        return await self._select_one(*conditions)

    async def get_by_message_id(self, id: str) -> Model:
        query = (
            select(Stack)
            .join(Conversation)
            .join(Message)
            .filter(Message.id == id)
        )
        res = await self._execute(query)
        return res.scalar()
        # return cast(Model, result)

    async def update(
        self,
        stack_id: str,
        user_id: str | None = not_set,
        name: str | None = not_set,
        description: str | None = not_set,
        initial_question: str | None = not_set,
        widget_delay: int | None = not_set,
        color: str | None = not_set,
    ) -> None:
        stack = await self.get_by_id(stack_id)

        values = {}
        fields = [
            "user_id",
            "name",
            "description",
            "initial_question",
            "widget_delay",
            "color",
        ]
        for field in fields:
            current_value = getattr(stack, field)
            new_value = locals()[field]
            if current_value != new_value and new_value is not not_set:
                values[field] = new_value
        if values:
            await self._update(Stack.id == stack.id, **values)

    async def delete(self, stack_id: str) -> None:
        try:
            await self._delete(self.model.id == stack_id)
        except IntegrityError as ex:
            raise DatabaseError(orig=ex)
