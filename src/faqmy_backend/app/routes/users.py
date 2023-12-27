from fastapi import APIRouter

from faqmy_backend.users.auth_backends import (
    cookie_auth_backend,
    jwt_auth_backend,
)
from faqmy_backend.users.manager import fastapi_users
from faqmy_backend.users.schemas import UserCreate, UserRead, UserUpdate

# Here, we could monkeypatch router.routes object to modify routes itself

jwt_auth_router = fastapi_users.get_auth_router(
    backend=jwt_auth_backend,
    requires_verification=False,
)

cookie_auth_router = fastapi_users.get_auth_router(
    backend=cookie_auth_backend,
    requires_verification=False,
)

signup_router = fastapi_users.get_register_router(
    user_schema=UserRead, user_create_schema=UserCreate
)
signup_router.routes[0].path = "/signup"


# Fine tune email request endpoint URLs
verify_router = fastapi_users.get_verify_router(UserRead)
verify_router.routes[0].path = "/email/verify/request"
verify_router.routes[1].path = "/email/verify/confirmation"

# Fine tune password reset endpoint URLs
reset_password_router = fastapi_users.get_reset_password_router()
reset_password_router.routes[0].path = "/password/forgot"
reset_password_router.routes[1].path = "/password/reset"

# Fine tune user management endpoint URLs
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    r
    for r in users_router.routes
    if r.name
    in (
        "users:current_user",
        "users:patch_current_user",
    )
]


router = APIRouter()
router.include_router(jwt_auth_router, prefix="/auth/jwt")
# router.include_router(cookie_auth_router, prefix="/auth/cookie")
router.include_router(signup_router, prefix="/auth")
router.include_router(verify_router, prefix="/auth")
router.include_router(reset_password_router, prefix="/auth")
router.include_router(users_router, prefix="/auth")
