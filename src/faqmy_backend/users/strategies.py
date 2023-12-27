from fastapi_users.authentication import JWTStrategy

from faqmy_backend.conf import settings


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.users.jwt_secret,
        lifetime_seconds=settings.users.jwt_lifetime_seconds,
    )
