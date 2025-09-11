from typing import Optional
from chromadb.api import ClientAPI
from fastapi import Depends
from connection.vectordb import get_chroma_client
from chromadb.api.models.Collection import Collection
from datetime import datetime


def get_chroma_collection(client: ClientAPI = Depends(get_chroma_client)) -> Collection:
	
    year = datetime.now().year  # default to current year

    collection_name = f"Tasks_{year}"

    # get_or_create_collection is safe to call multiple times;
    # ChromaDB will return the existing collection if it exists
    collection = client.get_or_create_collection(name=collection_name)
    return collection