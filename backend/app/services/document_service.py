from datetime import datetime
from fastapi import HTTPException
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from dto.document import DocumentActionResponse, DocumentRequest

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class DocumentService:
    def __init__(self, col: Collection):
        self.col = col

    async def add_documents(self, req: DocumentRequest) -> DocumentActionResponse:
        try:
            if req.metadata:
                for meta in req.metadata:
                    date_str = meta.get("date")
                    if date_str and isinstance(date_str, str):
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                        meta["date"] = int(dt.timestamp())

            self.col.add(
                ids=req.id,
                documents=req.document,
                metadatas=req.metadata
            )
            return DocumentActionResponse(
                message="Documents added successfully",
                ids=req.id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

   
    
