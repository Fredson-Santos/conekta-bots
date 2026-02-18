"""Exceções customizadas da aplicação.

Todas as exceções de negócio herdam de AppException,
permitindo tratamento centralizado via exception_handlers.
"""

from fastapi import status


class AppException(Exception):
    """Exceção base da aplicação."""

    def __init__(
        self,
        detail: str = "Erro interno",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class NotFoundException(AppException):
    """Recurso não encontrado (404)."""

    def __init__(self, resource: str = "Recurso", detail: str | None = None):
        super().__init__(
            detail=detail or f"{resource} não encontrado(a)",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ForbiddenException(AppException):
    """Acesso negado ao recurso (403)."""

    def __init__(self, detail: str = "Acesso negado"):
        super().__init__(
            detail=detail,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictException(AppException):
    """Conflito — recurso já existe (409)."""

    def __init__(self, detail: str = "Recurso já existe"):
        super().__init__(
            detail=detail,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class UnauthorizedException(AppException):
    """Credenciais inválidas ou token expirado (401)."""

    def __init__(self, detail: str = "Não autorizado"):
        super().__init__(
            detail=detail,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class BadRequestException(AppException):
    """Dados de entrada inválidos (400)."""

    def __init__(self, detail: str = "Requisição inválida"):
        super().__init__(
            detail=detail,
            error_code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class PlanLimitException(ForbiddenException):
    """Limite do plano atingido (403)."""

    def __init__(self, resource: str = "bots", limit: int = 0, plan: str = "free"):
        super().__init__(
            detail=f"Limite de {limit} {resource} atingido no plano {plan}",
        )
        self.error_code = "PLAN_LIMIT_EXCEEDED"
