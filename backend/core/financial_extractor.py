from groq import Groq
from typing import Dict
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FINANCIAL_FIELDS = [
    "payment_amount", "currency", "deposit", "security_deposit",
    "payment_schedule", "billing_cycle", "late_payment_penalty",
    "refund_policy", "taxes", "renewal_cost", "interest",
    "additional_charges"
]

def extract_financials(extracted_text: str) -> Dict:
    text_sample = extracted_text[:8000]

    prompt = f"""You are a financial contract analyzer. Extract all financial information from this contract.

CONTRACT TEXT:
{text_sample}

Respond with ONLY a JSON object in this exact format:
{{
  "payment_amount": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location like 'early in contract' or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation of what this means"
  }},
  "currency": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "deposit": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "security_deposit": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "payment_schedule": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "billing_cycle": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "late_payment_penalty": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "refund_policy": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "taxes": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "renewal_cost": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "interest": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "additional_charges": {{
    "value": "extracted value or null",
    "found": true or false,
    "evidence": "exact quote from contract or null",
    "page_hint": "approximate location or null",
    "risk_level": "Low, Medium, or High",
    "ai_explanation": "plain English explanation"
  }},
  "overall_financial_risk": "Low, Medium, or High",
  "financial_summary": "2-3 sentence plain English summary of the financial picture",
  "hidden_risks": ["list of hidden financial risks or penalties found"],
  "missing_fields": ["list of important financial fields not found in contract"]
}}

Return ONLY the JSON. No other text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a financial contract analyzer. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except Exception:
        return {
            "overall_financial_risk": "Unknown",
            "financial_summary": "Could not parse financial data. Please try again.",
            "hidden_risks": [],
            "missing_fields": FINANCIAL_FIELDS
        }
