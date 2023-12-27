import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faqmy_backend.db.models.base import BaseModel


class MessageTypeEnum(str, enum.Enum):
    user = "user"
    bot = "bot"


class Conversation(BaseModel):
    __id_prefix__ = "conv"

    stack_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stacks.id", ondelete="cascade")
    )
    password: Mapped[str] = mapped_column(String(255))

    stack: Mapped["Stack"] = relationship("Stack", lazy="joined")


class Message(BaseModel):
    __id_prefix__ = "msg"

    conversation_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("conversations.id", ondelete="cascade")
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(255), ForeignKey("messages.id", ondelete="set null")
    )
    who: Mapped[MessageTypeEnum] = mapped_column(
        Enum(MessageTypeEnum, native_enum=False, length=16),
        default=MessageTypeEnum.user,
    )
    text: Mapped[str] = mapped_column(Text())

    conversation: Mapped["Conversation"] = relationship("Conversation")
    parent: Mapped["Message"] = relationship(
        backref="replies", remote_side="Message.id"
    )
