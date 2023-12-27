import datetime

import pydantic


class Message(pydantic.BaseModel):
    id: str
    text: str
    created_at: datetime.datetime
    who: str
    parent_id: str | None

    class Config:
        orm_mode = True


class MessageIn(pydantic.BaseModel):
    conversation_id: str
    text: str


class StackPublic(pydantic.BaseModel):
    """
    Describes a stack being visible for a web surfer.
    """

    id: str
    initial_question: str | None
    widget_delay: int | None
    color: str | None

    class Config:
        orm_mode = True


class Stack(pydantic.BaseModel):
    id: str
    name: str | None
    description: str | None
    initial_question: str | None
    widget_delay: int | None
    color: str | None
    created_at: datetime.datetime
    # last_modified_at: datetime.datetime | None

    class Config:
        orm_mode = True


class StackIn(pydantic.BaseModel):
    name: str | None
    description: str | None
    initial_question: str | None
    widget_delay: int | None = 0
    color: str | None


class ConversationIn(pydantic.BaseModel):
    stack_id: str


class ConversationDashboard(pydantic.BaseModel):
    id: str
    stack: Stack
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class Conversation(pydantic.BaseModel):
    id: str
    password: str
    stack_id: str

    class Config:
        orm_mode = True


class Card(pydantic.BaseModel):
    id: str
    question: str | None = None
    answer: str | None = None
    learned: bool = False

    class Config:
        orm_mode = True


class CardIn(pydantic.BaseModel):
    stack_id: str
    question: str
    answer: str


class CardUrlIn(pydantic.BaseModel):
    stack_id: str
    url: pydantic.AnyUrl


class Widget(pydantic.BaseModel):
    is_active: bool = False
    reason: str
    metadata: dict = {}
