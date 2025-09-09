from pydantic import BaseModel
from typing import Any, List, Dict, Optional

class AskRequest(BaseModel):
    question: str
    user_id:str
    top_k: Optional[int] = 3


class AskResponse(BaseModel):
    question: str
    parsed_query: Dict[str, Any]
    answer: str
    sources: List[Dict[str, Any]]
