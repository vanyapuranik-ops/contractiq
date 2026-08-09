from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_contract(extracted_text: str) -> dict:
    """
    Takes the full contract text and returns a structured summary.

    Args:
        extracted_text: The full cleaned contract text

    Returns:
        A dictionary with structured summary fields
    """

    # We limit text to 6000 characters to stay within token limits
    # Most important information is in the first part of a contract
    text_to_summarize = extracted_text[:6000]

    system_prompt = """You are a contract analysis assistant.
Your job is to read legal contracts and produce clear, structured summaries.
You are NOT providing legal advice.
Always respond in the exact JSON format requested."""

    user_prompt = f"""Please analyze this contract and respond with ONLY a JSON object in this exact format:

{{
  "contract_type": "Type of contract (e.g. Employment Agreement, Loan Agreement, NDA)",
  "parties": ["Party 1 name", "Party 2 name"],
  "effective_date": "Date if mentioned, otherwise Unknown",
  "duration": "Contract duration if mentioned, otherwise Unknown",
  "key_points": [
    "Key point 1",
    "Key point 2",
    "Key point 3",
    "Key point 4",
    "Key point 5"
  ],
  "financial_terms": "Any salary, payment, or financial details mentioned",
  "termination": "How the contract can be terminated",
  "risks": [
    "Risk 1",
    "Risk 2",
    "Risk 3"
  ],
  "summary": "2-3 sentence plain English overview of the entire contract"
}}

CONTRACT TEXT:
{text_to_summarize}

Respond with ONLY the JSON object. No extra text before or after."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=1000
    )

    raw = response.choices[0].message.content.strip()

    # Clean up response in case model adds markdown code fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    import json
    try:
        return json.loads(raw)
    except Exception:
        return {
            "contract_type": "Unknown",
            "parties": [],
            "effective_date": "Unknown",
            "duration": "Unknown",
            "key_points": ["Could not parse summary. Please try again."],
            "financial_terms": "Unknown",
            "termination": "Unknown",
            "risks": [],
            "summary": raw
        }
