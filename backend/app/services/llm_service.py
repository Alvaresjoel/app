import langchain
from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from dependencies.langchain_dependency import get_langchain_chroma 
from dependencies.gemini_dependency import llm
from dto.prompt_dto import AskRequest, AskResponse
from utils.parser import parse_user_query
from datetime import datetime
from langchain_community.cache import InMemoryCache
from langchain.memory import ConversationBufferMemory
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

langchain.llm_cache = InMemoryCache()

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

class AskService:
    def __init__(self, vectordb: Chroma):
        self.vectordb = vectordb
        
        # Define prompt templates as class attributes for better organization
        self.WEEKLY_COMMENT_TEMPLATE = """
You are a productivity assistant. Answer in the FIRST PERSON (use "I"). Based on the user's query, provide a concise summary of my tasks.

FORMATTING REQUIREMENTS:
- Group tasks by date in chronological order
- Format each task as: <Project_Name> → <Task Name> (<Status>) : <Comment) — <Duration in hrs>
- Explicitly write duration as decimal hours with the suffix "hrs" (e.g., 1 hr, 2.5 hrs). If duration is missing, omit it.
- Use clear, professional language
- NEVER include user_id, log_id, ace_task_id, or any UUIDs
- If no tasks exist for the requested period, clearly state this

OUTPUT FORMAT:
<Day Name>, <Date>
- <Project_Name> → <Task Name> (<Status>) : <Comment) — <duration> hrs
- <Project_Name> → <Task Name> (<Status>) : <Comment) — <duration> hrs

[Repeat for each day with tasks]

Context:
{context}

Question: {question}

Answer:"""

        self.CSV_REPORT_TEMPLATE = """
You are a productivity assistant generating a structured report. Follow these exact requirements:

OUTPUT FORMAT:
1. **CSV Section** (required)
2. **Summary Section** (required)

CSV REQUIREMENTS:
- Header row with exact columns: task_title,project_name,user_name,start_time,end_time,duration,status,comment
- Each row represents one task
- Dates in ISO format (YYYY-MM-DD)
- Times in ISO 8601 format (YYYY-MM-DDTHH:MM)
- Duration in decimal hours (0.25 increments: 1, 1.25, 2.5, 3.75, etc.)
- Status: Completed, In Progress, Pending
- NO markdown formatting, NO code fences
- NO user_id, log_id, ace_task_id, or UUIDs

SUMMARY REQUIREMENTS:
- Answer in the FIRST PERSON (use "I").
- 2-3 sentences maximum
- Focus on key accomplishments and patterns
- Include total time spent and explicitly use "hrs" as the unit

EXAMPLE OUTPUT:
task_title,project_name,user_name,start_time,end_time,duration,status,comment
Fix login bug,Project Alpha,john@example.com,2025-09-08T09:00,2025-09-08T11:00,2.0,Completed,Resolved authentication issue
Write documentation,Project Beta,jane@example.com,2025-09-08T13:00,2025-09-08T15:15,2.25,Completed,Updated API documentation

Summary: I focused on bug fixes and documentation across two projects, completing 4.25 hrs of productive work.

Context: {context}
Question: {question}
Answer:"""

    async def ask_question(self, req: AskRequest) -> AskResponse:
        """
        Optimized ask_question method with improved error handling and flow
        """
        try:
            logger.info(f"Processing question: {req.question[:100]}...")
            
            # Step 1: Parse and validate query
            parsed_query = self._parse_and_validate_query(req.question)
            if not parsed_query:
                raise HTTPException(status_code=400, detail="Invalid query format")
            
            # Step 2: Build optimized filter
            vector_filter = self._build_filter(req.user_id, parsed_query)
            
            # Step 3: Retrieve documents with error handling
            results = self._retrieve_documents(vector_filter)
            
            # Step 4: Clean and format context
            context = self._format_context(results)
            
            # Step 5: Select appropriate template and generate response
            template = self._select_template(req.function_call)
            response = self._generate_response(template, context, req.question)
            
            # Step 6: Clean response and prepare sources
            cleaned_response = self._clean_response(response)
            sources = self._prepare_sources(results)
            
            logger.info(f"Successfully processed question for user: {req.user_id}")
            
            return AskResponse(
                question=req.question,
                parsed_query=parsed_query,
                answer=cleaned_response,
                sources=sources
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    def _parse_and_validate_query(self, question: str) -> Optional[Dict]:
        """Parse and validate the user query"""
        try:
            parsed_query = parse_user_query(question)
            
            # Validate required fields
            if not parsed_query.get("start_date") and not parsed_query.get("end_date"):
                logger.warning("No date range found in query")
            
            return parsed_query
        except Exception as e:
            logger.error(f"Query parsing failed: {str(e)}")
            return None

    def _build_filter(self, user_id: str, parsed_query: Dict) -> Dict:
        """Build optimized filter for document retrieval"""
        filters = [{"user_id": {"$eq": user_id}}]
        
        start_date = parsed_query.get("start_date")
        end_date = parsed_query.get("end_date")
        
        if start_date and end_date:
            try:
                start_date_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
                end_date_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
                
                filters.extend([
                    {"start_time": {"$gte": start_date_ts}},
                    {"start_time": {"$lte": end_date_ts}}
                ])
            except ValueError as e:
                logger.warning(f"Date parsing failed: {str(e)}")
        
        return {"$and": filters} if len(filters) > 1 else filters[0]

    def _retrieve_documents(self, vector_filter: Dict) -> Dict:
        """Retrieve documents with error handling"""
        try:
            results = self.vectordb._collection.get(
                where=vector_filter,
                include=["documents", "metadatas"],
                limit=100  # Set reasonable limit
            )
            
            if not results.get("documents"):
                logger.info("No documents found for the given filter")
            
            return results
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve documents")

    def _format_context(self, results: Dict) -> str:
        """Format documents into clean context"""
        docs = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        if not docs:
            return "No tasks found for the specified criteria."
        
        # Clean metadata to remove sensitive IDs and normalize duration units to hours
        cleaned_contexts = []
        for doc, meta in zip(docs, metadatas):
            # Remove sensitive keys from metadata
            clean_meta = {k: v for k, v in meta.items() 
                         if k not in ['user_id', 'log_id', 'ace_task_id']}
            
            # Format timestamp if present
            if 'start_time' in clean_meta:
                try:
                    clean_meta['start_time'] = datetime.fromtimestamp(
                        clean_meta['start_time']
                    ).strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    pass  # Keep original value if conversion fails
            
            # Normalize duration to '<n> hrs' if present
            try:
                if 'duration' in clean_meta and clean_meta['duration'] is not None:
                    duration_val = float(clean_meta['duration'])
                    # Trim trailing .0
                    duration_str = (
                        f"{int(duration_val)}" if abs(duration_val - int(duration_val)) < 1e-9 else f"{duration_val:.2f}"
                    )
                    clean_meta['duration'] = f"{duration_str} hrs"
            except (ValueError, TypeError):
                pass

            cleaned_contexts.append(f"Task: {doc}\nMetadata: {clean_meta}")
        
        return "\n\n".join(cleaned_contexts)

    def _select_template(self, function_call: str) -> str:
        """Select appropriate template based on function call"""
        if function_call == 'weekly_comment':
            return self.WEEKLY_COMMENT_TEMPLATE
        else:
            return self.CSV_REPORT_TEMPLATE

    def _generate_response(self, template: str, context: str, question: str) -> str:
        """Generate response using LLM"""
        try:
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template
            )
            
            chain = prompt | llm
            result = chain.invoke({"context": context, "question": question})
            
            return result.content if hasattr(result, "content") else str(result)
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate response")

    def _clean_response(self, response: str) -> str:
        """Clean response to remove any remaining IDs"""
        import re
        
        # Remove any remaining ID patterns
        id_patterns = [
            r'user_id["\']?\s*[:=]\s*["\']?[a-f0-9\-]{8,}["\']?',
            r'log_id["\']?\s*[:=]\s*["\']?[a-f0-9\-]{8,}["\']?',
            r'ace_task_id["\']?\s*[:=]\s*["\']?[a-f0-9\-]{8,}["\']?',
            r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b'
        ]
        
        cleaned = response
        for pattern in id_patterns:
            cleaned = re.sub(pattern, '[ID_REMOVED]', cleaned, flags=re.IGNORECASE)
        
        # Replace vague unit phrasing with hrs
        cleaned = re.sub(r"\bunit of time\b", "hr", cleaned, flags=re.IGNORECASE)

        # Clean up whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()

    def _prepare_sources(self, results: Dict) -> List[Dict]:
        """Prepare clean sources for response"""
        docs = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        sources = []
        for doc, meta in zip(docs, metadatas):
            # Clean metadata for sources
            clean_meta = {k: v for k, v in meta.items() 
                         if k not in ['user_id', 'log_id', 'ace_task_id']}
            
            sources.append({
                "document": doc,
                "metadata": clean_meta
            })
        
        return sources
