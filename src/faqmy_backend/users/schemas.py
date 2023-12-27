import pydantic
from fastapi_users import schemas


class UserRead(schemas.BaseUser[str]):
    name: str | None
    phone: str | None


class UserCreate(schemas.CreateUpdateDictModel):
    email: pydantic.EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    name: str | None
    phone: str | None
