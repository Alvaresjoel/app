import re, json
from datetime import datetime
from dependencies.gemini_dependency import llm
from prompts.prompt_comment import query_parser_template
from prompts.prompt_metadata import metadata_parser_template, POSSIBLE_PROMPTS

today = datetime.now().date()

def parse_user_query(question: str) -> dict:
    prompt = query_parser_template.invoke({"question": question, "today": str(today)})
    response = llm.invoke(prompt)

    text = response.content if hasattr(response, "content") else str(response)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        return {"start_date": None, "end_date": None, "keywords": [], "error": str(error)}

def metadata_parser(query: str) -> dict:
    prompt = metadata_parser_template.invoke({"question": query, "today": str(today), "examples": POSSIBLE_PROMPTS})
    response = llm.invoke(prompt)

    text = response.content if hasattr(response, "content") else str(response)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        return {"start_date": None, "end_date": None, "status": None, "duration": None, "project_name": None, "action": None, "error": str(error)}
