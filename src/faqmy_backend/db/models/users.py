from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from faqmy_backend.db.models.base import BaseModel


class User(BaseModel, SQLAlchemyBaseUserTable[str]):
    __id_prefix__ = "usr"

    # fastapi-users fields
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(), default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean(), default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # The application fields
    name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(255))
