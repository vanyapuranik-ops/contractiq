from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks

def get_chunk_stats(chunks: List[str]) -> dict:
    if not chunks:
        return {"total_chunks": 0}
    lengths = [len(chunk) for chunk in chunks]
    return {
        "total_chunks": len(chunks),
        "avg_chunk_size": round(sum(lengths) / len(lengths)),
        "min_chunk_size": min(lengths),
        "max_chunk_size": max(lengths)
    }
