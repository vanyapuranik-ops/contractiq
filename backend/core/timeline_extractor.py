from groq import Groq
from typing import List, Dict, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_timeline(extracted_text: str) -> Dict[str, Any]:
    text_sample = extracted_text[:8000]

    prompt = """You are a legal contract timeline analyst.

Extract every date, deadline, duration, and time-related obligation from the contract below.

For each event, classify the date type:
- "exact" = a specific calendar date e.g. January 1 2024
- "relative" = relative to another event e.g. 30 days after signing
- "duration" = a period of time e.g. 5 years
- "recurring" = repeating event e.g. monthly payment
- "conditional" = depends on a trigger e.g. 90 days written notice

NEVER invent or assume exact calendar dates for relative or conditional events.
NEVER hallucinate dates that are not in the contract.
If no dates exist, return an empty events array.

CONTRACT:
""" + text_sample + """

Respond with ONLY this JSON structure:

{
  "events": [
    {
      "title": "Short event title max 6 words",
      "date_value": "The date or period exactly as found or derived",
      "date_type": "exact | relative | duration | recurring | conditional",
      "category": "Contract Date | Payment | Renewal | Termination | Notice | Milestone | Delivery | Confidentiality | Non-compete | Grace Period | Other",
      "importance": "High | Medium | Low",
      "description": "Plain English explanation of what this date or deadline means",
      "evidence": "Exact quote from contract that supports this event",
      "related_clause": "Clause or section reference if found e.g. Clause 8.1",
      "page_hint": "Location hint e.g. Page 3 or early in contract",
      "confidence": "High | Medium | Low"
    }
  ],
  "summary": "2 sentence plain English summary of the contract timeline",
  "missing_dates": ["List of important dates not found e.g. End Date"],
  "total_events": 0,
  "has_exact_dates": true,
  "has_relative_dates": true
}

Return ONLY valid JSON. No markdown. No explanation."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal contract timeline analyst. Always respond with valid JSON only. Never hallucinate dates."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        events = data.get("events", [])
        validated = []
        for e in events:
            validated.append({
                "title": e.get("title", "Unnamed Event"),
                "date_value": e.get("date_value", "Not specified"),
                "date_type": e.get("date_type", "relative"),
                "category": e.get("category", "Other"),
                "importance": e.get("importance", "Low"),
                "description": e.get("description", ""),
                "evidence": e.get("evidence", ""),
                "related_clause": e.get("related_clause", ""),
                "page_hint": e.get("page_hint", ""),
                "confidence": e.get("confidence", "Medium")
            })

        return {
            "events": validated,
            "summary": data.get("summary", "No timeline summary available."),
            "missing_dates": data.get("missing_dates", []),
            "total_events": len(validated),
            "has_exact_dates": data.get("has_exact_dates", False),
            "has_relative_dates": data.get("has_relative_dates", False)
        }

    except json.JSONDecodeError:
        return _empty_response("AI returned invalid data. Please try again.")
    except Exception as e:
        return _empty_response(f"Extraction failed: {str(e)}")


def _empty_response(message: str) -> Dict[str, Any]:
    return {
        "events": [],
        "summary": message,
        "missing_dates": [],
        "total_events": 0,
        "has_exact_dates": False,
        "has_relative_dates": False
    }
