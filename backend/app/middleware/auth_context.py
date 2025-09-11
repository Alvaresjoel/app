# middleware/auth_context.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError
from auth.jwt_handler import decode_token

class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.auth = None
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = decode_token(token)  # may raise on invalid/expired
                # Normalize expected claims: sub (user id) and role (if present)
                request.state.auth = {
                    "sub": payload.get("sub"),
                    "role": payload.get("role")
                }
            except JWTError as e:
                # Leave state.auth as None; dependencies will reject if required
                request.state.auth = None
                request.state.auth_error = str(e)  # keep cause; dependency can use/log it

        response = await call_next(request)
        return response
