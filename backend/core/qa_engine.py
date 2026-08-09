from groq import Groq
from typing import List, Generator
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are ContractIQ, a professional AI legal assistant.
Your job is to help users understand legal contracts in plain English.
You are NOT providing legal advice. You are explaining what the contract says.

Rules:
- Answer based ONLY on the contract sections provided
- Use clear, simple language anyone can understand
- Structure your response with clear sections when appropriate
- Use markdown formatting for better readability
- Always cite which section your answer comes from
- If the answer is not in the provided sections, say so honestly
- End every response with a brief disclaimer about consulting a lawyer"""


def answer_question(question: str, relevant_chunks: List[str]) -> str:
    context = "\n\n---\n\n".join(relevant_chunks)

    user_prompt = f"""Based on the following contract sections, please answer this question:

**QUESTION:** {question}

**CONTRACT SECTIONS:**
{context}

Provide a clear, structured answer with markdown formatting."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content


def answer_question_streaming(question: str, relevant_chunks: List[str]) -> Generator:
    context = "\n\n---\n\n".join(relevant_chunks)

    user_prompt = f"""Based on the following contract sections, please answer this question:

**QUESTION:** {question}

**CONTRACT SECTIONS:**
{context}

Provide a clear, structured answer with markdown formatting."""

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=800,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


def generate_followup_questions(question: str, answer: str) -> List[str]:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Generate exactly 3 short follow-up questions a non-lawyer might ask after reading this contract Q&A. Return only a JSON array of 3 strings. No other text."
            },
            {
                "role": "user",
                "content": f"Question: {question}\nAnswer: {answer[:500]}"
            }
        ],
        temperature=0.5,
        max_tokens=200
    )

    import json
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        questions = json.loads(raw)
        return questions[:3] if isinstance(questions, list) else []
    except Exception:
        return [
            "Is this clause standard in most contracts?",
            "What are the risks if I do not comply?",
            "Can this clause be negotiated?"
        ]


def calculate_confidence(chunks: List[str], question: str) -> int:
    if not chunks:
        return 0
    avg_len = sum(len(c) for c in chunks) / len(chunks)
    base = 75
    if avg_len > 300:
        base += 10
    if len(chunks) >= 3:
        base += 10
    keywords = question.lower().split()
    matches = sum(1 for kw in keywords if any(kw in c.lower() for c in chunks))
    base += min(matches * 2, 10)
    return min(base, 98)
