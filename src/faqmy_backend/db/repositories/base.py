from abc import ABC
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Generic,
    Sequence,
    Type,
    TypeVar,
    cast,
)

from sqlalchemy import (
    ScalarResult,
    delete,
    exists,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import Executable

from faqmy_backend.db.exceptions import DatabaseError

Model = TypeVar("Model")
ModelClass = ClassVar[Type[Model]]


class BaseRepository(ABC, Generic[Model]):
    model: ModelClass

    def __init__(self, session_or_pool: sessionmaker | AsyncSession):
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool

    async def _execute(self, stmt):
        async with self.__transaction:
            return await self._session.execute(stmt)

    async def commit(self):
        await self._session.commit()

    @property
    @asynccontextmanager
    async def __transaction(self) -> AsyncGenerator:
        if not self._session.in_transaction() and self._session.is_active:
            async with self._session.begin() as transaction:
                yield transaction
        else:
            yield

    async def _insert(self, **values: Any) -> Model:
        try:
            return (
                await self._execute(insert_stmt(self.model, values))
            ).first()[0]
        except (IntegrityError, ) as ex:
            raise DatabaseError(ex)

    async def _update(self, *clauses: Any, **values: Any) -> None:
        try:
            await self._execute(
                update(self.model).where(*clauses).values(**values)
            )
        except (IntegrityError, ) as ex:
            raise DatabaseError(ex)

    async def _delete(self, *clauses: Any) -> list[Model]:
        query = delete(self.model).where(*clauses).returning(self.model)
        return list((await self._execute(query)).mappings().all())

    # @asynccontextmanager
    async def _select(self, *clauses: Any, **cond: Any) -> ScalarResult:
        # Sequence[Model]:
        return (
            await self._execute(
                cast(Executable, select_stmt(self.model, *clauses, **cond))
            )
        ).scalars()

    async def _select_all(self, *clauses: Any, **cond: Any) -> Sequence[Model]:
        results = (await self._select(*clauses, **cond)).all()
        return results

    async def _select_one(self, *clauses: Any, **cond: Any) -> Model:
        result = cast(Model, (await self._select(*clauses, **cond)).first())
        return result

    async def _exists(self, *clauses: Any) -> bool | None:
        result = (
            await self._execute(exists_stmt(self.model, *clauses))
        ).scalar()
        return cast(bool | None, result)

    async def _count(self) -> int:
        result = (
            (await self._execute(count_stmt(self.model))).scalars().first()
        )
        return cast(int, result)


def select_stmt(model: Model, *clauses, **cond):
    return select(model).where(*clauses).order_by(*cond.get("order_by", []))


def count_stmt(model: Model):
    return select(func.count("*")).select_from(model)


def insert_stmt(model: Model, values):
    return insert(model).values(**values).returning(model)


def update_stmt(model: Model, *clauses, **values):
    return update(model).where(*clauses).values(**values).returning(None)


def exists_stmt(model: Model, *clauses):
    return exists(select(model).where(*clauses)).select()
