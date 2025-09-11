from langchain.prompts import ChatPromptTemplate

POSSIBLE_PROMPTS = [
    "Show me tasks from the last 6 months",
    "Summarize my completed tasks for the past week",
    "show me time invested in all my tasks from 2023-01-01 to 2023-02-01",
    "Show me all tasks that are still 'In Progress'",
    "What is the total time spent on completed tasks in the last week?",
    "What is the longest task I worked on in the past year?",
    "What is the total duration of tasks completed in the last 3 days?",
    "List tasks with duration greater than 5 hours from the last 2 weeks"
]

metadata_parser_template = ChatPromptTemplate.from_template(
    """
    These are some examples of user prompts: {examples}. 
    Prompts from examples {examples} are not part of the user query; they are just for context.

    There are main keyword_actions the user can ask for:
    1. 'total': compute the total duration of tasks matching the filters
    2. 'longest': find the longest task matching the filters_duration
    3. 'list': list all tasks matching the filters 
    4. user asks for a specific status, like 'In Progress' or 'Completed'
    5. user provides a date range, like 'from 2023-01-01 to 2023-02-01' 
       or relative dates like 'last 6 months'
    6. user asks about "how much time was spent" or "duration of tasks" → set action to 'total' 
    7. if user ask give tasks that i spent more than X hours, set action to 'list' and duration to greater than X hours

    Rules for interpreting relative dates:
    - "Show me tasks from the last 6 months" → action is 'list', duration = False
    - "last week" eg:(today = 2025-03-11) → start_date = 2025-03-03, end_date = 2025-03-10
    - "last month" eg:(if current month = September 2025) → start_date = 2025-08-01, end_date = 2025-08-31
    - "last 6 months" eg:(today = 2025-03-11) → start_date = 2024-09-11, end_date = 2025-03-11

    Important: The response must **always include a JSON object** with the following keys:
    {{
        "action": string,        
        "status": string|null,   
        "duration": string|null,     
        "start_date": string,    
        "end_date": string       
    }}

    You may also include an optional "explanation" key for human-readable reasoning, but the JSON must be **parseable**.

    Today's date is {today}.

    User Question: {question}
    """
)
