import typing
import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, InvalidID
from fastapi_users.db import SQLAlchemyUserDatabase

from faqmy_backend.conf import settings
from faqmy_backend.services.email import (
    ConfirmEmailNotification,
    EmailConfirmationDoneEmailNotification,
    ForgetPasswordEmailNotification,
)
from faqmy_backend.users.auth_backends import (
    cookie_auth_backend,
    jwt_auth_backend,
)
from faqmy_backend.users.db import User, get_user_db


class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.users.reset_password_token_secret
    verification_token_secret = settings.users.verification_token_secret

    def parse_id(self, value: typing.Any) -> str:
        if not isinstance(value, str) or not value.startswith("usr_"):
            raise InvalidID()
        return value

    async def on_after_register(
        self, user: User, request: Request | None = None
    ):
        await self.request_verify(user, request)

    async def on_after_update(
        self,
        user: User,
        update_dict: dict[str, typing.Any],
        request: Request | None = None,
    ):
        print(f"User {user.id} has been updated with {update_dict}.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        await ForgetPasswordEmailNotification.send(
            user.email,
            context={
                "user": user,
                "token": token,
                "request": request,
            },
        )

    async def on_after_reset_password(
        self, user: User, request: Request | None = None
    ):
        print(f"User {user.id} has reset their password.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        await ConfirmEmailNotification.send(
            user.email,
            context={
                "user": user,
                "token": token,
                "request": request,
            },
        )

    async def on_after_verify(
        self, user: User, request: Request | None = None
    ):
        print(f"User {user.id} has been verified")
        await EmailConfirmationDoneEmailNotification.send(
            user.email,
            {
                "user": user,
                "request": request,
            },
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, str](
    get_user_manager=get_user_manager,
    auth_backends=[jwt_auth_backend, cookie_auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
