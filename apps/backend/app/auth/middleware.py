from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.auth.security import decode_access_token


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.user = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            payload = decode_access_token(token, raise_error=False)
            if payload:
                request.state.user = {
                    "id": payload.get("sub"),
                    "role": payload.get("role"),
                }

        response = await call_next(request)
        return response
