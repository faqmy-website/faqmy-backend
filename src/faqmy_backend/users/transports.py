from fastapi_users.authentication import BearerTransport, CookieTransport

from faqmy_backend.conf import settings

us = settings.users

cookie_transport = CookieTransport(cookie_max_age=us.cookie_max_age)
bearer_transport = BearerTransport(tokenUrl=us.bearer_token_url)
