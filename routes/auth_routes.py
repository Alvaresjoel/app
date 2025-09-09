from fastapi import APIRouter, HTTPException, status, Security
from dto.response import SuccessResponse
from services.auth_service import refresh_access_token
from fastapi.security import HTTPAuthorizationCredentials
from dependencies.auth_dependencies import refresh_scheme

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.patch(
    "/refresh",
    response_model=SuccessResponse,
    summary="Refresh Token",
    description="Generate a new access token using refresh token",
    openapi_extra={"security": [{"refreshAuth": []}]}  # tell Swagger to use refreshAuth
)
def refresh(creds: HTTPAuthorizationCredentials = Security(refresh_scheme)):
    if not creds or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    data = refresh_access_token(creds.credentials)
    return SuccessResponse(
        message="Token refreshed", 
        data=data,
        errors=None
    )