# routes.py
from fastapi import APIRouter, Depends
from services.agent_services import ProductivityAgent
from dependencies.chromadb_dependency import get_chroma_collection
from dependencies.langchain_dependency import get_langchain_chroma
from dependencies.gemini_dependency import get_llm  
from dto.prompt_dto import AgentRequest,AgentResponse
agent_router = APIRouter(
    prefix="/agent", tags=["Agent"]
)

# Request/Response schema


@agent_router.post("/ask", response_model=AgentResponse)
async def ask_question(
    req: AgentRequest,
    vectordb = Depends(get_langchain_chroma),
    llm = Depends(get_llm),
    col = Depends(get_chroma_collection)
):
    agent = ProductivityAgent(llm=llm, vectordb=vectordb, col=col)
    answer = agent.run(req.question, req.user_id)
    return AgentResponse(question=req.question, answer=answer)