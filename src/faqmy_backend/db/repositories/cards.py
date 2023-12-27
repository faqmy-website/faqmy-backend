from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from faqmy_backend.db.exceptions import DatabaseError
from faqmy_backend.db.models.stack import Card, Stack
from faqmy_backend.db.repositories.base import BaseRepository, Model

not_set = object()


class CardRepository(BaseRepository[Card]):
    model = Card

    async def is_accessible_by_user(self, card_id: str, user_id: str) -> bool:
        return (
            await self._execute(
                select(
                    select(Card.id)
                    .join(Stack)
                    .filter(Card.id == card_id, Stack.user_id == user_id)
                    .exists()
                )
            )
        ).scalar()

    async def create(self, stack_id: str, question: str, answer: str) -> Model:
        return await self._insert(
            stack_id=stack_id,
            question=question,
            answer=answer,
            learned=False,
        )

    async def get_by_id(self, id: str) -> Model:
        return await self._select_one(Card.id == id)

    async def mark_learned(
        self, card_id: str, es_doc_id: str | None = None
    ) -> Model:
        values = {
            "learned": True,
        }
        if es_doc_id is not None:
            values["es_doc_id"] = es_doc_id
        return await self._update(Card.id == card_id, **values)

    async def get_by_stack_id(
        self,
        stack_id: str,
        learned: bool | None = None,
    ) -> list[Model]:
        conds = [Card.stack_id == stack_id]
        if learned is not None:
            conds.append(Card.learned.is_(learned))
        return await self._select_all(*conds)

    async def delete(self, stack_id: str) -> None:
        try:
            await self._delete(self.model.id == stack_id)
        except IntegrityError as ex:
            raise DatabaseError(orig=ex)

    async def update(
        self,
        card_id: str | None = not_set,
        question: str | None = not_set,
        answer: str | None = not_set,
        learned: bool | None = not_set,
        es_doc_id: str | None = not_set,
    ) -> None:
        card = await self.get_by_id(card_id)
        values = {}
        fields = ["question", "answer", "learned", "es_doc_id"]

        for field in fields:
            current_value = getattr(card, field)
            new_value = locals()[field]
            if current_value != new_value and new_value is not not_set:
                values[field] = new_value
        if values:
            await self._update(Card.id == card.id, **values)
