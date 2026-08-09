from core.embedder import get_single_embedding
from core.vector_store import query_collection
from typing import List

def retrieve_relevant_chunks(question: str, collection_name: str, n_results: int = 5) -> List[str]:
    """
    Takes a user question, converts it to a vector,
    searches ChromaDB for the most similar chunks,
    and returns them as a list of strings.

    Args:
        question: The user's question in plain English
        collection_name: Which contract to search in
        n_results: How many chunks to retrieve (default 5)

    Returns:
        List of the most relevant text chunks
    """

    # Step 1: Convert the question into a vector
    # We use the same embedding model as we used for chunks
    # This ensures question and chunks exist in the same vector space
    question_vector = get_single_embedding(question)

    # Step 2: Search ChromaDB for closest chunk vectors
    relevant_chunks = query_collection(
        collection_name=collection_name,
        query_embedding=question_vector,
        n_results=n_results
    )

    return relevant_chunks
