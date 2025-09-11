from pydantic import BaseModel
from typing import Any, List, Dict, Optional

class AskRequest(BaseModel):
    question: str
    user_id: str
    function_call : str

class AskResponse(BaseModel):
    question: str
    parsed_query: Optional[Dict] = None
    answer: str
    sources: Optional[List[Dict]] = None

class AgentRequest(BaseModel):
    question: str
    user_id: str

class AgentResponse(BaseModel):
    question: str
    parsed_query: Optional[Dict] = None
    answer: str
    sources: Optional[List[Dict]] = None