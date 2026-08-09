from sentence_transformers import SentenceTransformer
from typing import List

model = SentenceTransformer('BAAI/bge-small-en-v1.5')

def get_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Converts a list of text chunks into a list of vectors.
    Each chunk becomes a list of 384 numbers.
    """
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings.tolist()

def get_single_embedding(text: str) -> List[float]:
    """
    Converts a single piece of text into a vector.
    Used later for converting user questions into vectors.
    """
    embedding = model.encode([text])
    return embedding[0].tolist()
