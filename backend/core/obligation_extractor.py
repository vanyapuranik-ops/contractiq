from groq import Groq
from typing import Dict, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_obligations(extracted_text: str) -> Dict[str, Any]:
    text_sample = extracted_text[:8000]

    prompt = """You are a legal contract obligation analyst.

Extract every contractual obligation, duty, responsibility, requirement, and commitment from the contract below.

Rules:
- Use actual party names from the contract, not generic labels
- If party cannot be determined, use "General Obligation"
- Never invent obligations not in the contract
- Do not duplicate obligations

CONTRACT:
""" + text_sample + """

Respond with ONLY this JSON:
{
  "obligations": [
    {
      "title": "Short obligation title max 7 words",
      "responsible_party": "Exact party name or General Obligation",
      "obligation_type": "Payment | Confidentiality | Notice | Delivery | Reporting | Compliance | Performance | Documentation | Insurance | Maintenance | Data Protection | Intellectual Property | Termination | Post-Termination | Other",
      "obligation_category": "Mandatory | Conditional | Prohibition | Ongoing | One-time | Recurring | Post-termination",
      "description": "Plain English explanation",
      "evidence": "Exact quote from contract",
      "related_clause": "Clause reference e.g. Clause 7.2",
      "page_hint": "Location hint e.g. Page 5",
      "deadline_type": "exact | relative | recurring | conditional | none",
      "deadline": "The deadline or null",
      "frequency": "Frequency if recurring or null",
      "priority": "High | Medium | Low",
      "confidence": 0.95
    }
  ],
  "parties": ["List of identified party names"],
  "summary": "2 sentence plain English summary of key obligations",
  "total_obligations": 0,
  "high_priority_count": 0,
  "obligations_with_deadlines": 0
}

Return ONLY valid JSON. No markdown."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a legal contract obligation analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=3000
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        obligations = data.get("obligations", [])

        validated = []
        seen = set()

        for o in obligations:
            key = (
                o.get("responsible_party", ""),
                o.get("obligation_type", ""),
                o.get("related_clause", "")
            )
            if key in seen:
                continue
            seen.add(key)

            validated.append({
                "title": o.get("title", "Unnamed Obligation"),
                "responsible_party": o.get("responsible_party", "General Obligation"),
                "obligation_type": o.get("obligation_type", "Other"),
                "obligation_category": o.get("obligation_category", "Mandatory"),
                "description": o.get("description", ""),
                "evidence": o.get("evidence", ""),
                "related_clause": o.get("related_clause", ""),
                "page_hint": o.get("page_hint", ""),
                "deadline_type": o.get("deadline_type", "none"),
                "deadline": o.get("deadline"),
                "frequency": o.get("frequency"),
                "priority": o.get("priority", "Low"),
                "confidence": o.get("confidence", 0.8)
            })

        high_count = sum(1 for o in validated if o["priority"] == "High")
        with_deadlines = sum(1 for o in validated if o["deadline_type"] != "none" and o["deadline"])

        return {
            "obligations": validated,
            "parties": data.get("parties", []),
            "summary": data.get("summary", "No summary available."),
            "total_obligations": len(validated),
            "high_priority_count": high_count,
            "obligations_with_deadlines": with_deadlines
        }

    except json.JSONDecodeError:
        return _empty_response("AI returned invalid data. Please try again.")
    except Exception as e:
        return _empty_response(f"Extraction failed: {str(e)}")


def _empty_response(message: str) -> Dict[str, Any]:
    return {
        "obligations": [],
        "parties": [],
        "summary": message,
        "total_obligations": 0,
        "high_priority_count": 0,
        "obligations_with_deadlines": 0
    }
