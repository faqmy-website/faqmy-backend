from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get(
    path="/live",
    response_class=PlainTextResponse,
    tags=["Health Care"],
    summary="Is the service live?",
    include_in_schema=True,
)
async def liveness_probe():
    """
    This endpoint responds with a success code to your orchestrator when
    the service is live
    \f
    """
    return "OK"


@router.get(
    path="/ready",
    response_class=PlainTextResponse,
    tags=["Health Care"],
    summary="Is the service ready?",
    include_in_schema=True,
)
async def readiness_probe():
    """
    This endpoint responds with a success code to your orchestrator when
    the service is ready to accept connections.

    Use it for

    \f
    """
    return "OK"
