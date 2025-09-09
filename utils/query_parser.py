import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

from dependencies.gemini_dependency import llm #FIXME: this is not a dependency, move it to the connection folder

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import google.generativeai as genai
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
today = datetime.now().date()
template = ChatPromptTemplate([
    ("system", "You are a query parser. \
                Convert the user question into a structured JSON object with these keys: \
                - project_name:if project Name is mentioned     \
                - start_date: (ISO format, if relative like \"last 6 months\")\
                - end_date: (ISO format, if relative like \"last 6 months\")\
                - keywords: (list of relevant keywords) Output ONLY valid JSON \
                - do NOT include any explanations or extra text.\
                - Date today for your context is {today}\
    "),
                 
    ("human", "{question}")
])

def parse_user_query(question: str) -> dict:
    prompt = template.invoke({"question": question,"today":str(today)})
    response = llm.invoke(prompt)
    if hasattr(response, "content"):  
        text = response.content
    elif isinstance(response, dict) and "content" in response:
        text = response["content"]
    else:
        text = str(response)

    # Step 4: Clean markdown backticks
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()

    try:
        parsed_json = json.loads(cleaned)
    except json.JSONDecodeError as error:
        parsed_json = {
            "start_date": None,
            "end_date": None,
            "keywords": [],
            "error" : error
        }

    return parsed_json
