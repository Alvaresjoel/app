from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from dto.user_dto import UserRequest
from dto.response import ErrorResponse, SuccessResponse
from services.user_services import UserService
from dependencies.get_db import get_db

router = APIRouter(
    prefix="/user", 
    tags=["user"]
)

@router.post("/login", response_model=SuccessResponse | ErrorResponse)
def login_user(request: UserRequest, response: Response, db: Session = Depends(get_db)):
    service = UserService(db)
    result, status_code = service.login_and_store_user(request)
    response.status_code = status_code
    return result
