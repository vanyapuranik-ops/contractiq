import chromadb
from chromadb.config import Settings
from typing import List
import hashlib

client = chromadb.Client(Settings(
    is_persistent=True,
    persist_directory="./chroma_db"
))

def get_or_create_collection(collection_name: str):
    """
    Gets an existing collection or creates a new one.
    A collection is like a table in a regular database.
    Each uploaded contract gets its own collection.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def store_chunks(collection_name: str, chunks: List[str], embeddings: List[List[float]]):
    """
    Stores chunks and their embeddings in ChromaDB.
    Each chunk gets a unique ID based on its content.
    """
    collection = get_or_create_collection(collection_name)

    ids = []
    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{collection_name}_{i}_{chunk[:50]}".encode()).hexdigest()
        ids.append(chunk_id)

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )

    return len(chunks)

def query_collection(collection_name: str, query_embedding: List[float], n_results: int = 5):
    """
    Finds the most similar chunks to a query vector.
    Returns the top n_results most relevant chunks.
    """
    collection = get_or_create_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0]

def delete_collection(collection_name: str):
    """
    Deletes a collection — used when reprocessing a contract.
    """
    try:
        client.delete_collection(collection_name)
    except Exception as e:
        print(f"[vector_store] Could not delete collection: {e}")
