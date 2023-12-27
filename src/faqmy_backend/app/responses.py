from fastapi import HTTPException
from starlette import status


def err(
    message: str = "Something went wrong",
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> HTTPException:
    return HTTPException(
        detail=[{"msg": message}],
        status_code=status_code,
    )
