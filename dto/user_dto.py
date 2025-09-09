from pydantic import BaseModel

class UserRequest(BaseModel):
    account_id: str
    username: str
    password: str

class UserResponse(BaseModel):
    message: str
    username: str
    user_id: str
    ace_user_id: str
    account_id: str
