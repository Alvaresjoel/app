from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_chroma import Chroma
from dependencies.langchain_dependency import get_langchain_chroma 
from dependencies.gemini_dependency import llm
from dto.document import DocumentResponse
from dto.prompt_dto import AskRequest, AskResponse
from utils.query_parser import parse_user_query  # your existing parser
from datetime import datetime

class AskService:
    def __init__(self, vectordb: Chroma):
        self.vectordb = vectordb

    async def ask_question(self, req: AskRequest) -> AskResponse:
        try:
            # --- Step 1: Parse query ---
            parsed_query = parse_user_query(req.question)
            user_id = req.user_id
            
            start_date = parsed_query.get("start_date")
            end_date = parsed_query.get("end_date")
            project_name = parsed_query.get("project_name")
            start_date_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()) if start_date else None
            end_date_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) if end_date else None

            # --- Step 2: Build filter ---
            filters = [{"user_id": {"$eq": user_id}}]  # always include user_id
            if project_name:
                filters.append({"project_id":project_name}) #FIXME projects are not in the task_log table
            if start_date_ts and end_date_ts:
                filters.append({"date": {"$gte": start_date_ts}})
                filters.append({"date": {"$lte": end_date_ts}})
                vector_filter = {"$and": filters}
            else:
                vector_filter = filters[0]
            # Use $and if there are multiple conditions, otherwise just the single one
            

            # --- Step 3: Setup retriever ---
            retriever = self.vectordb.as_retriever(
                search_type="similarity",
                search_kwargs={"k": req.top_k, 
                               "filter": vector_filter
                               },
                
            )

            # --- Step 4: Prompt ---
            template = """
            You are a productivity assistant. Use the following context
            (task details and metadata) to answer the question. Do not send the user_id in the summary.

            {context}

            Question: {question}
            """
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template
            )

            # --- Step 5: Format docs ---
            def format_docs(docs):
                return "\n\n".join(
                    f"Task: {doc.page_content}\nMetadata: {doc.metadata}"
                    for doc in docs
                )

            qa_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
            )

            # --- Step 6: Query ---
            result = qa_chain.invoke(req.question)

            # --- Step 7: Sources ---
            sources = [
                {"document": doc.page_content, "metadata": doc.metadata}
                for doc in retriever.invoke(req.question)
            ]

            return AskResponse(
                question=req.question,
                parsed_query=parsed_query,
                answer=result.content if hasattr(result, "content") else str(result),
                sources=sources
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    
    async def get_documents(self) -> DocumentResponse:
        try:
            question = "fixed"
            result = self.vectordb.as_retriever()
            docs = result.invoke(question)
            return DocumentResponse(
                id = docs.id,
                document = docs.document,
                metadata = docs.metadata
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
