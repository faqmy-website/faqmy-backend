import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faqmy_backend.db.models.base import BaseModel


class Stack(BaseModel):
    __id_prefix__ = "st"

    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(255))
    special_offer: Mapped[str | None] = mapped_column(String(255))  # WTF?
    initial_question: Mapped[str | None] = mapped_column(String(255))

    last_modified_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
    )
    widget_delay: Mapped[int | None] = mapped_column(Integer(), default=3)
    color: Mapped[str | None] = mapped_column(String(255), default="#000000")

    user: Mapped["User"] = relationship("User")


class Card(BaseModel):
    __id_prefix__ = "card"

    stack_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("stacks.id", ondelete="cascade"),
        nullable=False,
    )
    question: Mapped[str | None] = mapped_column(Text())
    answer: Mapped[str | None] = mapped_column(Text())
    learned: Mapped[bool] = mapped_column(Boolean, default=False)
    es_doc_id: Mapped[str | None] = mapped_column(String(32))

    stack: Mapped[Stack] = relationship("Stack")
