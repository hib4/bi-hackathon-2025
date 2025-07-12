from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import *

def json_error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return json_error_response(HTTP_400_BAD_REQUEST, "Bad request. Invalid input.")

async def http_exception_handler(request: Request, exc: HTTPException):
    return json_error_response(exc.status_code, str(exc.detail))

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return json_error_response(exc.status_code, str(exc.detail))

async def internal_server_error_handler(request: Request, exc: Exception):
    return json_error_response(HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
