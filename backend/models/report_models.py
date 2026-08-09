from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ReportRequest(BaseModel):
    extracted_text: str
    file_name: str
    file_size: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    collection_name: Optional[str] = None
    include_summary: bool = True
    include_risks: bool = True
    include_clauses: bool = True
    include_financials: bool = True
    include_timeline: bool = True
    include_obligations: bool = True


class ReportMetadata(BaseModel):
    file_name: str
    file_size: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    collection_name: Optional[str] = None
    generated_at: str
    ai_model: str = "llama-3.3-70b-versatile"
    confidence: Optional[str] = None


class ReportSection(BaseModel):
    available: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ReportResponse(BaseModel):
    metadata: ReportMetadata
    executive_summary: ReportSection
    risk_findings: ReportSection
    clause_analysis: ReportSection
    financial_review: ReportSection
    timeline: ReportSection
    obligations: ReportSection
    final_recommendation: ReportSection
    generation_time_seconds: Optional[float] = None
