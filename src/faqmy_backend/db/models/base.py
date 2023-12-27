from __future__ import annotations

import datetime

import shortuuid
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, as_declarative, declared_attr, mapped_column

from faqmy_backend.db.metadata import metadata
from faqmy_backend.db.utils import camel_to_snake


def get_table_name_from_class(cls: BaseModel) -> str:
    """
    Generate a table name for the model class
    """
    return camel_to_snake(cls.__name__) + "s"


def get_class_by_table(table):
    try:
        return {
            c
            for c in BaseModel.registry._class_registry.values()  # NOQA
            if hasattr(c, "__table__") and c.__table__ is table
        }.pop()
    except KeyError:
        return None


def generate_pk(context) -> str:
    return get_class_by_table(context.current_column.table).generate_new_id()


@as_declarative(metadata=metadata)
class BaseModel:
    id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        primary_key=True,
        nullable=False,
        index=True,
        default=generate_pk,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
    )

    @classmethod
    def generate_new_id(cls) -> str:
        return cls.id_prefix + shortuuid.uuid()

    @declared_attr
    def id_prefix(cls):  # NOQA
        return (
            cls.__id_prefix__
            if hasattr(cls, "__id_prefix__")
            else cls.__tablename__[: getattr(cls, "__id_prefix_length__", 3)]
        ) + getattr(cls, "__id_prefix_separator__", "_")

    @declared_attr
    def __tablename__(cls):  # NOQA
        return get_table_name_from_class(cls)

    def __repr__(self):
        return "<" + self.__class__.__name__ + ": " + str(self.id) + ">"
