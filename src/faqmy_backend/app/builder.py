from fastapi import APIRouter, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from faqmy_backend import __version__
from faqmy_backend.app.dependencies import (
    CardRepositoryDependMarker,
    ConversationRepositoryDependMarker,
    GetDbDependMarker,
    MessageRepositoryDependMarker,
    StackRepositoryDependMarker,
    UserDbMarker,
)
from faqmy_backend.app.middleware.process_time import add_process_time_header
from faqmy_backend.app.routes.client import router as client_router
from faqmy_backend.app.routes.dashboard import router as dashboard_router
from faqmy_backend.app.routes.billing import router as billing_router
from faqmy_backend.app.routes.healthcheck import router as healthcheck_router
from faqmy_backend.app.routes.users import router as users_router
from faqmy_backend.conf import settings
from faqmy_backend.db.connection import create_session
from faqmy_backend.db.repositories.cards import CardRepository
from faqmy_backend.db.repositories.conversation import ConversationRepository
from faqmy_backend.db.repositories.message import MessageRepository
from faqmy_backend.db.repositories.stack import StackRepository
from faqmy_backend.users.db import get_async_session


def build_app(app: FastAPI) -> FastAPI:
    setup_metadata(app)
    setup_middlewares(app)
    setup_routes(app)
    setup_fastapi_users(app)
    setup_dependencies(app)
    return app


def setup_metadata(app: FastAPI) -> FastAPI:
    app.title = "faqmy.website backend"
    app.description = "Servers to handle bots and user inputs"
    app.version = __version__
    app.debug = settings.app.debug
    return app


def setup_middlewares(app: FastAPI) -> FastAPI:
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def setup_routes(app: FastAPI) -> FastAPI:
    v1_router = APIRouter()

    v1_router.include_router(
        router=users_router,
        # prefix="/dashboard",
        tags=["Authentication and Authorization"],
    )

    v1_router.include_router(
        router=client_router, prefix="/client", tags=["Client Side"]
    )
    v1_router.include_router(
        router=dashboard_router,
        prefix="/dashboard",
        tags=["Webmaster Dashboard"],
    )
    v1_router.include_router(
        router=billing_router,
        prefix="/billing",
        tags=["Billing"],
    )

    app.include_router(v1_router, prefix="/v1")
    app.include_router(healthcheck_router, prefix="/status")

    return app


def setup_fastapi_users(app: FastAPI) -> FastAPI:
    """
    Injects fastapi-users into the application
    """
    return app


def setup_dependencies(app: FastAPI) -> FastAPI:
    session = create_session  #

    app.dependency_overrides.update(
        {
            GetDbDependMarker: lambda: session,
            UserDbMarker: get_async_session,
            StackRepositoryDependMarker: lambda: StackRepository(session),
            MessageRepositoryDependMarker: lambda: MessageRepository(session),
            CardRepositoryDependMarker: lambda: CardRepository(session),
            ConversationRepositoryDependMarker: lambda: ConversationRepository(
                session
            ),
        }
    )
    return app
