from sqlalchemy.orm import Session
import requests
from fastapi import HTTPException, status
from dto.user_dto import UserRequest, UserResponse
from dto.response import ErrorResponse, SuccessResponse, ErrorCode
from auth.jwt_handler import create_access_token, create_refresh_token
from models.users import Users
from dotenv import load_dotenv
import os

load_dotenv()
ACE_API_URL = os.getenv('ACE_API_URL')


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def login_and_store_user(self, user_request: UserRequest) -> SuccessResponse | ErrorResponse:
        params = {
            "fct": "Login",
            "accountid": user_request.account_id,
            "username": user_request.username,
            "password": user_request.password,
            "browserinfo": "NULL",
            "language": "NULL",
            "format": "json"
        }

        try:
            response = requests.get(ACE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            #print("API Response:", data)

            if data.get("status") != "ok":
                error_desc = data.get("results", [{}])[0].get("ERRORDESCRIPTION", "Unknown error")
                
                # Handle specific error cases and return appropriate error responses
                if "invalid account" in error_desc.lower() or "account not found" in error_desc.lower():
                    return ErrorResponse(
                        error="Invalid Account ID",
                        error_code=ErrorCode.INVALID_ACCOUNT_ID,
                        message="The provided account ID is invalid or does not exist",
                        data=None
                    ), status.HTTP_404_NOT_FOUND
                elif "invalid username" in error_desc.lower() or "invalid password" in error_desc.lower() or "authentication failed" in error_desc.lower():
                    return ErrorResponse(
                        error="Invalid Credentials",
                        error_code=ErrorCode.INVALID_CREDENTIALS,
                        message="The provided email/username or password is incorrect",
                        data=None
                    ), status.HTTP_401_UNAUTHORIZED
                elif "account locked" in error_desc.lower() or "account disabled" in error_desc.lower():
                    return ErrorResponse(
                        error="Account Locked",
                        error_code=ErrorCode.ACCOUNT_LOCKED,
                        message="Your account has been locked or disabled. Please contact support",
                        data=None
                    ), status.HTTP_403_FORBIDDEN
                else:
                    return ErrorResponse(
                        error="Login Failed",
                        error_code=ErrorCode.LOGIN_FAILED,
                        message=error_desc,
                        data=None
                    ), status.HTTP_400_BAD_REQUEST
                
            user_data = data["results"][0]
            guid = user_data.get("GUID")
            email = user_data.get("EMAIL_ALERT")
            
            user = self.db.query(Users).filter(Users.email == email).first()
            if user:
                user.guid = guid
            else:
                user = Users(
                    ace_user_id=user_data.get("USER_ID"),
                    guid=guid,
                    email=email,
                    role="user"
                )
                self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            access_token = create_access_token({"sub": str(user.guid), "role": user.role})
            refresh_token = create_refresh_token({"sub": str(user.guid)})

            return SuccessResponse(
                message="Login successful",
                data={
                    "guid": guid,
                    "user_id": str(user.user_id),
                    "ace_user_id": str(user.ace_user_id),
                    "username": user_request.username,
                    "account_id": user_request.account_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token
                },
                error=None
            ), status.HTTP_200_OK

        except requests.RequestException as e:
            return ErrorResponse(
                message="Unable to connect to authentication service. Please try again later",
                error="Service Unavailable",
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                data=None
            ), status.HTTP_500_INTERNAL_SERVER_ERROR
