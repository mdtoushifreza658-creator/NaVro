"""
M2: consistent error envelope across every endpoint.

Every non-2xx response has the shape:
    { "error": { "code": "...", "message": "...", "details": [...] | null } }

per docs/spec.md Section 3 ("Error envelope"). Route handlers raise
NavroError (or its subclasses) rather than a bare HTTPException, so the
shape is guaranteed centrally instead of by convention.
"""

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class NavroError(Exception):
    """Base app error. Carries an HTTP status + stable machine-readable code."""

    status_code = 500
    code = "internal_error"

    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(NavroError):
    status_code = 404
    code = "not_found"


class ConflictError(NavroError):
    status_code = 409
    code = "conflict"


class UnauthorizedError(NavroError):
    status_code = 401
    code = "unauthorized"


def _envelope(code: str, message: str, details: list | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def register_exception_handlers(app):
    @app.exception_handler(NavroError)
    async def handle_navro_error(request: Request, exc: NavroError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in err["loc"][1:]), "issue": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_envelope("validation_error", "Request failed validation", details),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        # Catches FastAPI/Starlette-native HTTPExceptions (e.g. from Header(...)
        # required-field errors) so even those conform to the envelope.
        code_by_status = {401: "unauthorized", 404: "not_found", 409: "conflict"}
        code = code_by_status.get(exc.status_code, "error")
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(code, str(exc.detail)),
        )
