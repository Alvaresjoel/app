from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum

class ErrorCode(str, Enum):
    INVALID_ACCOUNT_ID = "INVALID_ACCOUNT_ID"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    LOGIN_FAILED = "LOGIN_FAILED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: str
    error_code: ErrorCode
    data: Optional[Any] = None

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
