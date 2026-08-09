import re
from typing import List, Dict
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RISK_PATTERNS = {
    "high": [
        {
            "id": "unlimited_liability",
            "label": "Unlimited Liability",
            "patterns": [
                r"unlimited liability",
                r"liable for all damages",
                r"liable for any and all",
                r"unconditional liability"
            ]
        },
        {
            "id": "unilateral_termination",
            "label": "Unilateral Termination Without Cause",
            "patterns": [
                r"terminate.*without cause",
                r"terminate.*at any time.*without",
                r"terminate.*sole discretion",
                r"terminate.*without.*notice"
            ]
        },
        {
            "id": "indemnification",
            "label": "Broad Indemnification Clause",
            "patterns": [
                r"indemnif\w+.*all claims",
                r"indemnif\w+.*any.*loss",
                r"hold harmless.*all",
                r"indemnif\w+.*third.party"
            ]
        },
        {
            "id": "ip_assignment",
            "label": "Broad IP Assignment",
            "patterns": [
                r"all intellectual property.*assign",
                r"assign.*all.*rights",
                r"work.*made.*for.*hire",
                r"all inventions.*belong"
            ]
        },
        {
            "id": "personal_guarantee",
            "label": "Personal Guarantee",
            "patterns": [
                r"personal guarantee",
                r"personally liable",
                r"personal liability",
                r"guarantor.*personally"
            ]
        }
    ],
    "medium": [
        {
            "id": "non_compete",
            "label": "Non-Compete Clause",
            "patterns": [
                r"non.compete",
                r"not.*compete.*with",
                r"shall not.*work.*competitor",
                r"competing.*business"
            ]
        },
        {
            "id": "auto_renewal",
            "label": "Automatic Renewal",
            "patterns": [
                r"auto.?renew",
                r"automatically.*renew",
                r"renew.*automatically",
                r"unless.*terminated.*prior"
            ]
        },
        {
            "id": "arbitration",
            "label": "Mandatory Arbitration",
            "patterns": [
                r"mandatory arbitration",
                r"binding arbitration",
                r"disputes.*arbitration",
                r"arbitration.*sole.*remedy"
            ]
        },
        {
            "id": "non_solicitation",
            "label": "Non-Solicitation Clause",
            "patterns": [
                r"non.solicit",
                r"shall not.*solicit",
                r"not.*approach.*employee",
                r"poaching.*prohibited"
            ]
        },
        {
            "id": "penalty_clause",
            "label": "Penalty / Liquidated Damages",
            "patterns": [
                r"liquidated damages",
                r"penalty.*breach",
                r"damages.*fixed.*amount",
                r"pre.?determined.*damages"
            ]
        }
    ],
    "low": [
        {
            "id": "confidentiality",
            "label": "Confidentiality Obligation",
            "patterns": [
                r"confidential.*information",
                r"non.disclosure",
                r"shall not.*disclose",
                r"proprietary.*information"
            ]
        },
        {
            "id": "governing_law",
            "label": "Governing Law Clause",
            "patterns": [
                r"governed by.*law",
                r"governing law",
                r"jurisdiction.*courts",
                r"laws of.*shall govern"
            ]
        },
        {
            "id": "amendment",
            "label": "Unilateral Amendment Right",
            "patterns": [
                r"amend.*sole.*discretion",
                r"modify.*without.*notice",
                r"change.*terms.*anytime",
                r"reserve.*right.*modify"
            ]
        }
    ]
}


def find_clause_context(text: str, pattern: str, context_chars: int = 300) -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return ""
    start = max(0, match.start() - 100)
    end = min(len(text), match.end() + context_chars)
    return text[start:end].strip()


def detect_risks(text: str) -> Dict:
    found_risks = {"high": [], "medium": [], "low": []}
    text_lower = text.lower()

    for severity, risk_list in RISK_PATTERNS.items():
        for risk in risk_list:
            for pattern in risk["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    clause_context = find_clause_context(text, pattern)
                    found_risks[severity].append({
                        "id": risk["id"],
                        "label": risk["label"],
                        "severity": severity,
                        "clause": clause_context
                    })
                    break

    total = (
        len(found_risks["high"]) * 3 +
        len(found_risks["medium"]) * 2 +
        len(found_risks["low"]) * 1
    )

    if total >= 6:
        overall = "High"
    elif total >= 3:
        overall = "Medium"
    else:
        overall = "Low"

    return {
        "overall_risk": overall,
        "high_risks": found_risks["high"],
        "medium_risks": found_risks["medium"],
        "low_risks": found_risks["low"],
        "total_risks": len(found_risks["high"]) + len(found_risks["medium"]) + len(found_risks["low"]),
        "risk_score": total
    }
