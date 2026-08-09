from groq import Groq
from typing import Dict, Any, Optional
from datetime import datetime
import os
import json
import time
from dotenv import load_dotenv

from core.summarizer import summarize_contract
from core.risk_detector import detect_risks
from core.clause_extractor import classify_chunks
from core.financial_extractor import extract_financials
from core.timeline_extractor import extract_timeline
from core.obligation_extractor import extract_obligations
from core.chunker import chunk_text
from core.cleaner import clean_text

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _safe_run(fn, *args, **kwargs) -> Dict[str, Any]:
    try:
        result = fn(*args, **kwargs)
        return {"available": True, "data": result, "error": None}
    except Exception as e:
        return {"available": False, "data": None, "error": str(e)}


def generate_final_recommendation(
    summary: Optional[Dict],
    risks: Optional[Dict],
    obligations: Optional[Dict]
) -> Dict[str, Any]:
    context_parts = []

    if summary and summary.get("summary"):
        context_parts.append(f"Contract Summary: {summary.get('summary', '')}")

    if risks:
        overall = risks.get("overall_risk", "Unknown")
        total = risks.get("total_risks", 0)
        context_parts.append(f"Overall Risk: {overall}. Total risk findings: {total}.")

    if obligations:
        total_obs = obligations.get("total_obligations", 0)
        high_obs = obligations.get("high_priority_count", 0)
        context_parts.append(f"Total obligations: {total_obs}. High priority: {high_obs}.")

    if not context_parts:
        return {
            "recommendation": "Insufficient data to generate a final recommendation.",
            "overall_quality": "Unknown",
            "major_risks": [],
            "key_responsibilities": [],
            "areas_for_legal_review": [],
            "disclaimer": "This AI-generated review is intended to assist document understanding and should not replace professional legal advice."
        }

    context = "\n".join(context_parts)

    prompt = f"""You are a professional contract review AI assistant.

Based on the following contract analysis data, generate a final professional recommendation.

{context}

Respond with ONLY this JSON:
{{
  "recommendation": "3-4 sentence professional concluding summary of the contract",
  "overall_quality": "Strong | Acceptable | Needs Review | High Risk",
  "major_risks": ["risk 1", "risk 2", "risk 3"],
  "key_responsibilities": ["responsibility 1", "responsibility 2", "responsibility 3"],
  "areas_for_legal_review": ["area 1", "area 2"],
  "disclaimer": "This AI-generated review is intended to assist document understanding and should not replace professional legal advice."
}}

Return ONLY valid JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional contract review assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    except Exception as e:
        return {
            "recommendation": "Could not generate recommendation. Please try again.",
            "overall_quality": "Unknown",
            "major_risks": [],
            "key_responsibilities": [],
            "areas_for_legal_review": [],
            "disclaimer": "This AI-generated review is intended to assist document understanding and should not replace professional legal advice.",
            "error": str(e)
        }


def generate_report(
    extracted_text: str,
    file_name: str,
    file_size: Optional[str] = None,
    page_count: Optional[int] = None,
    word_count: Optional[int] = None,
    collection_name: Optional[str] = None,
    include_summary: bool = True,
    include_risks: bool = True,
    include_clauses: bool = True,
    include_financials: bool = True,
    include_timeline: bool = True,
    include_obligations: bool = True
) -> Dict[str, Any]:

    start_time = time.time()

    cleaned = clean_text(extracted_text)
    chunks = chunk_text(cleaned)

    metadata = {
        "file_name": file_name,
        "file_size": file_size,
        "page_count": page_count,
        "word_count": word_count or len(cleaned.split()),
        "collection_name": collection_name,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ai_model": "llama-3.3-70b-versatile"
    }

    executive_summary = {"available": False, "data": None, "error": "Skipped"}
    risk_findings = {"available": False, "data": None, "error": "Skipped"}
    clause_analysis = {"available": False, "data": None, "error": "Skipped"}
    financial_review = {"available": False, "data": None, "error": "Skipped"}
    timeline = {"available": False, "data": None, "error": "Skipped"}
    obligations = {"available": False, "data": None, "error": "Skipped"}

    if include_summary:
        executive_summary = _safe_run(summarize_contract, extracted_text)

    if include_risks:
        risk_findings = _safe_run(detect_risks, cleaned)

    if include_clauses and chunks:
        clause_analysis = _safe_run(classify_chunks, chunks[:15])

    if include_financials:
        financial_review = _safe_run(extract_financials, extracted_text)

    if include_timeline:
        timeline = _safe_run(extract_timeline, extracted_text)

    if include_obligations:
        obligations = _safe_run(extract_obligations, extracted_text)

    summary_data = executive_summary.get("data") if executive_summary.get("available") else None
    risk_data = risk_findings.get("data") if risk_findings.get("available") else None
    obligation_data = obligations.get("data") if obligations.get("available") else None

    final_recommendation = _safe_run(
        generate_final_recommendation,
        summary_data,
        risk_data,
        obligation_data
    )

    generation_time = round(time.time() - start_time, 2)

    return {
        "metadata": metadata,
        "executive_summary": executive_summary,
        "risk_findings": risk_findings,
        "clause_analysis": clause_analysis,
        "financial_review": financial_review,
        "timeline": timeline,
        "obligations": obligations,
        "final_recommendation": final_recommendation,
        "generation_time_seconds": generation_time
    }
