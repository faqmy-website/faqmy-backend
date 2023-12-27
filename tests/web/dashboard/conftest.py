import httpx
import pytest
from fastapi_users.jwt import generate_jwt

from faqmy_backend.conf import settings


@pytest.fixture
def jwt_token(user):
    yield generate_jwt(
        data={"sub": str(user.id), "aud": ["fastapi-users:auth"]},
        secret=settings.users.jwt_secret,
        lifetime_seconds=settings.users.jwt_lifetime_seconds,
    )


@pytest.fixture
async def client(client, jwt_token) -> httpx.AsyncClient:
    client.headers["Authorization"] = "Bearer " + jwt_token
    yield client
