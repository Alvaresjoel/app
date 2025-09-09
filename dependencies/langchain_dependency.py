from langchain_chroma import Chroma
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
import os

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_langchain_chroma() -> Chroma:
    year = datetime.now().year  # default to current year
    return Chroma(
    collection_name=f"Tasks_{year}",
    embedding_function=embeddings,
    chroma_cloud_api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
)
