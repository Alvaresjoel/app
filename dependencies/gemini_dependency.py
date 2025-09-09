import os
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",   # or gemini-1.5-pro / gemini-1.5-flash
            temperature=0,
            google_api_key=os.getenv('GEMINI_API_KEY')
            )


