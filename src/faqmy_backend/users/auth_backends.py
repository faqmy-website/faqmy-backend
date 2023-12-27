from fastapi_users.authentication import AuthenticationBackend

from faqmy_backend.users.strategies import get_jwt_strategy
from faqmy_backend.users.transports import bearer_transport, cookie_transport

jwt_auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


cookie_auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
