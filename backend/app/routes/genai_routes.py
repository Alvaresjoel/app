from fastapi import APIRouter, Depends
from langchain_chroma import Chroma
from chromadb.api.models.Collection import Collection

from dto.document import DocumentActionResponse, DocumentRequest
from dto.prompt_dto import AskRequest, AskResponse

from dependencies.chromadb_dependency import get_chroma_collection
from dependencies.langchain_dependency import get_langchain_chroma


from services.document_service import DocumentService
from services.llm_service import AskService


genai_router = APIRouter(prefix="/genai", tags=["Embeddings"])

@genai_router.post("/embeddings",response_model = DocumentActionResponse )
async def add_documents(
    request: DocumentRequest,
    col: Collection = Depends(get_chroma_collection)
):
    return await DocumentService(col).add_documents(request)

@genai_router.post("/ask", response_model=AskResponse)
async def ask_gemini(
    request: AskRequest,
    vectordb: Chroma = Depends(get_langchain_chroma)
):
    return await AskService(vectordb).ask_question(request)


