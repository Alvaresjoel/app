import os
from fastapi import HTTPException
from dotenv import load_dotenv
from google import genai
from google.genai import types

client = genai.Client()
def call_gemini(context:str,question:str,) -> str :
    if not os.getenv('GEMINI_API_KEY'):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    try:
        response =  response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction="You are a helpful assistant. Answer questions based only on the provided context."),
                    contents= f"Context: {context}\n\nQuestion: {question}"
                )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")
