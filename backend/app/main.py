"""FastAPI application factory and HTTP exception wiring."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import VentureMindError
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.schemas.common import ErrorDetail, ErrorResponse
from app.services.appointment_reminder_service import send_due_appointment_reminders

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and release process-scoped resources."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("Starting %s in %s", settings.app_name, settings.app_env)
    async def reminder_loop() -> None:
        while True:
            try:
                with SessionLocal() as session:
                    sent = send_due_appointment_reminders(session)
                    if sent:
                        logger.info("Sent %s advisor appointment reminder batches", sent)
            except Exception:
                logger.exception("Appointment reminder delivery failed")
            await asyncio.sleep(300)

    reminder_task = asyncio.create_task(reminder_loop())
    yield
    reminder_task.cancel()
    try:
        await reminder_task
    except asyncio.CancelledError:
        pass
    logger.info("Stopping %s", settings.app_name)


def create_application() -> FastAPI:
    """Build the configured ASGI application for Uvicorn and tests."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.cors_origins],
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$" if settings.app_env == "development" else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    register_exception_handlers(app)
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Map application and validation exceptions to stable response envelopes."""

    @app.exception_handler(VentureMindError)
    async def venturemind_error_handler(_: Request, exc: VentureMindError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message)
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields: dict[str, list[str]] = {}
        for error in exc.errors():
            location = ".".join(str(item) for item in error["loc"] if item != "body") or "body"
            fields.setdefault(location, []).append(error["msg"])
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="validation_error", message="Request validation failed.", fields=fields
                )
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", exc_info=exc)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="internal_server_error", message="An unexpected error occurred."
                )
            ).model_dump(),
        )


app = create_application()
