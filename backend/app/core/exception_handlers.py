"""Handlers globais de exceções para FastAPI.

Registrados no app via `register_exception_handlers(app)`.
Garantem respostas de erro padronizadas em JSON.
"""

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException

logger = logging.getLogger("conekta-bots")


def _error_response(
    status_code: int,
    detail: str,
    error_code: str = "ERROR",
    errors: list | None = None,
) -> JSONResponse:
    """Formata resposta de erro padronizada."""
    content: dict = {
        "detail": detail,
        "error_code": error_code,
    }
    if errors:
        content["errors"] = errors
    return JSONResponse(status_code=status_code, content=content)


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Handler para exceções customizadas da aplicação."""
    logger.warning("AppException [%s]: %s", exc.error_code, exc.detail)
    return _error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_code=exc.error_code,
    )


async def http_exception_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handler para HTTPException padrão do FastAPI/Starlette."""
    return _error_response(
        status_code=exc.status_code,
        detail=str(exc.detail),
        error_code="HTTP_ERROR",
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler para erros de validação Pydantic (422 → 400)."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    logger.info("Validation error: %d campo(s) inválido(s)", len(errors))
    return _error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Erro de validação nos dados enviados",
        error_code="VALIDATION_ERROR",
        errors=errors,
    )


async def unhandled_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Handler catch-all para exceções não tratadas (500)."""
    logger.error(
        "Unhandled exception: %s\n%s",
        str(exc),
        traceback.format_exc(),
    )
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Erro interno do servidor",
        error_code="INTERNAL_ERROR",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os handlers no app FastAPI."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
