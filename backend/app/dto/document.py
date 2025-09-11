from pydantic import BaseModel
from typing import Dict, List, Optional

class DocumentRequest(BaseModel):
    id: List[str]
    document: List[str]
    metadata: Optional[List[Dict]] = None


class DocumentActionResponse(BaseModel):
    message: str
    ids: List[str]
    
    
class DocumentResponse(BaseModel):
    id: List[str]
    document: List[str]
    metadata:Optional[List[dict]] = None
