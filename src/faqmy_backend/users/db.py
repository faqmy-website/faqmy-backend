from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from faqmy_backend.app.dependencies import UserDbMarker
from faqmy_backend.db.connection import create_session
from faqmy_backend.db.models.users import User


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with create_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(UserDbMarker)):
    yield SQLAlchemyUserDatabase(session, User)
