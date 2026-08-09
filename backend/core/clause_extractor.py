from groq import Groq
from typing import List, Dict
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CATEGORIES = [
    "Termination", "Payment", "Confidentiality", "Liability",
    "Intellectual Property", "Governing Law", "Dispute Resolution",
    "Renewal", "Indemnification", "Non-compete", "Force Majeure",
    "Notices", "General"
]

RISK_LEVELS = ["Low", "Medium", "High"]


def classify_chunks(chunks: List[str]) -> List[Dict]:
    results = []

    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 50:
            continue

        prompt = f"""Analyze this contract clause and respond with ONLY a JSON object.

CLAUSE TEXT:
{chunk[:800]}

Respond with ONLY this JSON format, no other text:
{{
  "title": "Short descriptive title (max 6 words)",
  "category": "One of: Termination, Payment, Confidentiality, Liability, Intellectual Property, Governing Law, Dispute Resolution, Renewal, Indemnification, Non-compete, Force Majeure, Notices, General",
  "risk_level": "One of: Low, Medium, High",
  "plain_english": "2-3 sentence plain English explanation",
  "risk_assessment": "1-2 sentence risk assessment",
  "related_categories": ["category1", "category2"]
}}"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a legal contract analyzer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)

            results.append({
                "id": i,
                "title": data.get("title", f"Clause {i + 1}"),
                "category": data.get("category", "General"),
                "risk_level": data.get("risk_level", "Low"),
                "plain_english": data.get("plain_english", ""),
                "risk_assessment": data.get("risk_assessment", ""),
                "related_categories": data.get("related_categories", []),
                "original_text": chunk,
                "page_number": (i // 3) + 1,
                "clause_number": f"{(i // 5) + 1}.{(i % 5) + 1}"
            })

        except Exception as e:
            results.append({
                "id": i,
                "title": f"Clause {i + 1}",
                "category": "General",
                "risk_level": "Low",
                "plain_english": chunk[:200],
                "risk_assessment": "Unable to assess automatically.",
                "related_categories": [],
                "original_text": chunk,
                "page_number": (i // 3) + 1,
                "clause_number": f"{(i // 5) + 1}.{(i % 5) + 1}"
            })

    return results
