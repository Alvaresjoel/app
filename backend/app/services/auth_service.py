from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from auth.jwt_handler import create_access_token, create_refresh_token, decode_token

def refresh_access_token(refresh_token: str):
    payload = decode_token(refresh_token)
    access_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": access_token}
