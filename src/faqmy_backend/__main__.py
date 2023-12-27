import uvicorn

from faqmy_backend.conf import settings

uvicorn.run(
    "faqmy_backend.app.asgi:app",
    host=settings.app.host,
    port=settings.app.port,
    log_level=settings.app.log_level,
    reload=settings.app.debug,
)
