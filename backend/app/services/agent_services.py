# agent.py
from fastapi import HTTPException
from langchain.agents import initialize_agent, Tool
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from genai.summarizer import semantic_search_tool
from genai.metadata_search import metadata_query_tool_factory
from utils.tool_router import ToolRouter

class ProductivityAgent:
    def __init__(self, llm, vectordb, col):
        self.llm = llm
        self.vectordb = vectordb
        self.col = col
        self.tool_router = ToolRouter()

    def run(self, question: str, user_id: str) -> str:
        try:
            # Pre-analyze the query to get tool recommendation
            routing_info = self.tool_router.get_tool_recommendation(question)
            print(f"Tool Router Analysis: {routing_info}")
            
            # Create a retriever filtered by user_id
            retriever = self.vectordb.as_retriever(search_kwargs={"k": 5, "filter": {"user_id": user_id}})

            # Initialize tools with the filtered retriever
            tools = [
                Tool(
                    name="SemanticRetriever",
                    func=semantic_search_tool(retriever, self.llm),
                    description="""Use this tool ONLY when the user explicitly mentions specific:
                    - Project names (e.g., 'Project X', 'My Website Project')
                    - Task names (e.g., 'Task Y', 'Bug Fix Task')
                    - Specific task content or comments
                    
                    DO NOT use for date-based queries, status queries, or time-based filtering.
                    Examples: 'Find tasks related to Project X', 'Get details about Task Y', 'What comments did I add to Task Z?'"""
                ),
                Tool(
                    name="MetadataQuery",
                    func=metadata_query_tool_factory(self.col, user_id),
                    description="""Use this tool for ALL queries involving:
                    - Date ranges (August, September, last week, last month, etc.)
                    - Time periods (2023-01-01 to 2023-02-01)
                    - Task status (completed, in progress, pending)
                    - Duration/time spent queries
                    - Aggregation queries (total time, longest task, etc.)
                    - General task listing without specific project/task names
                    
                    Examples: 'Give me tasks in August and September', 'Show completed tasks last week', 'Total time spent in September'"""
                )
            ]
            agent_prompt = PromptTemplate(
                    input_variables=["input", "routing_info"],
                                    template = """
                You are a productivity assistant. You have access to two tools and must choose the correct one based on the user's question.

                TOOL ROUTING ANALYSIS:
                Recommended Tool: {routing_info}
                
                CRITICAL TOOL SELECTION RULES:
                
                🔍 Use SemanticRetriever ONLY when:
                - User mentions a SPECIFIC project name (e.g., "Project X", "My Website", "Mobile App")
                - User mentions a SPECIFIC task name (e.g., "Bug Fix Task", "Database Migration")
                - User asks about specific task content or comments
                
                📊 Use MetadataQuery for ALL other queries, especially:
                - Date-based queries (August, September, last week, last month, 2023, etc.)
                - Time period queries (from X to Y date)
                - Status queries (completed, in progress, pending)
                - Duration/time spent queries
                - Aggregation queries (total time, longest task, count)
                - General task listing without specific names

                DECISION TREE:
                1. Does the question contain specific project/task names? → Use SemanticRetriever
                2. Does the question contain dates, time periods, or status? → Use MetadataQuery
                3. Is it asking for general task information? → Use MetadataQuery
                4. Default: Use MetadataQuery

                EXAMPLES:
                ✅ "Give me tasks in August and September" → MetadataQuery (date-based)
                ✅ "Show completed tasks last week" → MetadataQuery (status + date)
                ✅ "Total time spent in September" → MetadataQuery (aggregation + date)
                ✅ "Find tasks related to Project X" → SemanticRetriever (specific project)
                ✅ "Get details about Task Y" → SemanticRetriever (specific task)
                ✅ "What is the longest task I worked on?" → MetadataQuery (aggregation)

                Output Style:
                - Answer as if you are speaking directly to the user (second person: "you").
                - Be concise and confident.
                - Normalize durations to hours with the suffix "hrs" (e.g., 1 hr, 1.5 hrs). If the text says "unit of time" or omits units, interpret it as hours and state it explicitly.
                - Prefer phrasing like: "You completed ...", "You worked ... for <n> hrs".
                - NEVER include user_id, ace_task_id, log_id, or any UUIDs in your response.
                - If you see any IDs in the data, ignore them completely.

                Question: {input}
                """)

            # Initialize the agent
            agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent="zero-shot-react-description",
                verbose=True,
                agent_kwargs={"prompt":agent_prompt}
            )

            # Run the agent with routing information embedded in the prompt
            enhanced_question = f"ROUTING HINT: Recommended tool is {routing_info['recommended_tool']} (confidence: {routing_info['confidence']:.2f})\n\nQuestion: {question}"
            result = agent.run(enhanced_question)
            
            # Clean the result to remove any IDs and fix unit wording
            cleaned = self._clean_output(result)
            cleaned = self._normalize_units_and_perspective(cleaned)
            return cleaned

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def _clean_output(self, text: str) -> str:
        """
        Clean the output to remove any user_id, log_id, or ace_task_id references
        """
        import re
        
        # Patterns to match various ID formats
        id_patterns = [
            r'user_id["\']?\s*[:=]\s*["\']?[a-f0-9\-]{8,}["\']?',  # user_id: "uuid"
            r'log_id["\']?\s*[:=]\s*["\']?[a-f0-9\-]{8,}["\']?',   # log_id: "uuid"
            r'ace_task_id["\']?\s*[:=]\s*["\']?[a-f0-9\-]{8,}["\']?', # ace_task_id: "uuid"
            r'user_id\s*:\s*[a-f0-9\-]{8,}',  # user_id: uuid
            r'log_id\s*:\s*[a-f0-9\-]{8,}',   # log_id: uuid
            r'ace_task_id\s*:\s*[a-f0-9\-]{8,}', # ace_task_id: uuid
            r'user_id["\']?\s*:\s*["\']?[a-f0-9\-]{8,}["\']?',  # user_id: "uuid"
            r'log_id["\']?\s*:\s*["\']?[a-f0-9\-]{8,}["\']?',   # log_id: "uuid"
            r'ace_task_id["\']?\s*:\s*["\']?[a-f0-9\-]{8,}["\']?', # ace_task_id: "uuid"
        ]
        
        cleaned_text = text
        for pattern in id_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Remove any standalone UUIDs that might be IDs
        uuid_pattern = r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b'
        cleaned_text = re.sub(uuid_pattern, '[ID_REMOVED]', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and newlines
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()

    def _normalize_units_and_perspective(self, text: str) -> str:
        """
        Normalize ambiguous duration units to hours and steer phrasing to second person.
        """
        import re
        out = text
        # Replace 'unit of time' with 'hr'
        out = re.sub(r"\bunit of time\b", "hr", out, flags=re.IGNORECASE)
        # Add 'hrs' suffix to numbers followed by 'hr' or bare durations in common patterns
        out = re.sub(r"(\b\d+(?:\.\d+)?)(\s*hr\b)", r"\1 hrs", out, flags=re.IGNORECASE)
        out = re.sub(r"(duration\s*:\s*)(\d+(?:\.\d+)?)\b(?!\s*(?:hr|hrs))", r"\1\2 hrs", out, flags=re.IGNORECASE)
        # Encourage second-person phrasing lightly and replace named subjects
        out = re.sub(r"\bI (completed|did|worked on)\b", r"You \1", out)
        out = re.sub(r"\bworked on by\s+[A-Za-z][\w\.-]*\b", "worked on by you", out, flags=re.IGNORECASE)
        out = re.sub(r"\bcompleted by\s+[A-Za-z][\w\.-]*\b", "completed by you", out, flags=re.IGNORECASE)
        out = re.sub(r"\bdone by\s+[A-Za-z][\w\.-]*\b", "done by you", out, flags=re.IGNORECASE)
        return out.strip()