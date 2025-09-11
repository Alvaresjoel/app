from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    user_id:str

class AskResponse(BaseModel):
    question: str
    answer: str