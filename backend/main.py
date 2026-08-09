from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.pdf_extractor import extract_text_from_pdf, get_page_count
from core.cleaner import clean_text
from core.chunker import chunk_text, get_chunk_stats
from core.embedder import get_embeddings
from core.vector_store import store_chunks, delete_collection
from core.retriever import retrieve_relevant_chunks
from core.qa_engine import answer_question, answer_question_streaming, generate_followup_questions, calculate_confidence
from core.summarizer import summarize_contract
from core.risk_detector import detect_risks
from core.clause_extractor import classify_chunks
from core.financial_extractor import extract_financials
from core.timeline_extractor import extract_timeline
from utils.helpers import format_file_size
from core.obligation_extractor import extract_obligations
from core.report_service import generate_report
from models.report_models import ReportRequest
import io
import re
import json
from typing import List
from fastapi.responses import StreamingResponse, Response
from core.pdf_generator import generate_pdf_report

app = FastAPI(
    title="AI Contract Explainer API",
    description="Backend API for extracting and analyzing legal contracts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    collection_name: str
    n_results: int = 5

class SummarizeRequest(BaseModel):
    extracted_text: str

class RiskRequest(BaseModel):
    extracted_text: str

class ClauseRequest(BaseModel):
    chunks: List[str]

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Contract Explainer API is running"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are accepted.")
    file_bytes = await file.read()
    page_count = get_page_count(io.BytesIO(file_bytes))
    extracted_text = extract_text_from_pdf(io.BytesIO(file_bytes))
    if not extracted_text:
        raise HTTPException(status_code=422, detail="Could not extract text. PDF may be image-based.")
    cleaned = clean_text(extracted_text)
    chunks = chunk_text(cleaned)
    stats = get_chunk_stats(chunks)
    collection_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file.filename.replace('.pdf', ''))
    collection_name = re.sub(r'[_-]+', '_', collection_name)
    collection_name = collection_name.strip('_-')
    delete_collection(collection_name)
    embeddings = get_embeddings(chunks)
    store_chunks(collection_name, chunks, embeddings)
    return {
        "file_name": file.filename,
        "file_size": format_file_size(len(file_bytes)),
        "page_count": page_count,
        "word_count": len(cleaned.split()),
        "extracted_text": cleaned,
        "chunks": chunks,
        "chunk_stats": stats,
        "collection_name": collection_name,
        "embeddings_stored": len(embeddings)
    }

@app.post("/retrieve")
def retrieve(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        chunks = retrieve_relevant_chunks(
            question=request.question,
            collection_name=request.collection_name,
            n_results=request.n_results
        )
        return {"question": request.question, "relevant_chunks": chunks, "chunks_found": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@app.post("/ask")
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        chunks = retrieve_relevant_chunks(
            question=request.question,
            collection_name=request.collection_name,
            n_results=request.n_results
        )
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant sections found.")
        answer = answer_question(question=request.question, relevant_chunks=chunks)
        followups = generate_followup_questions(request.question, answer)
        confidence = calculate_confidence(chunks, request.question)
        return {
            "question": request.question,
            "answer": answer,
            "sources": chunks,
            "followup_questions": followups,
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

@app.post("/ask-stream")
async def ask_stream(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    chunks = retrieve_relevant_chunks(
        question=request.question,
        collection_name=request.collection_name,
        n_results=request.n_results
    )
    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant sections found.")
    confidence = calculate_confidence(chunks, request.question)

    def generate():
        full_answer = ""
        meta = json.dumps({"type": "meta", "sources": chunks, "confidence": confidence})
        yield f"data: {meta}\n\n"
        for token in answer_question_streaming(request.question, chunks):
            full_answer += token
            payload = json.dumps({"type": "token", "content": token})
            yield f"data: {payload}\n\n"
        followups = generate_followup_questions(request.question, full_answer)
        done = json.dumps({"type": "done", "followup_questions": followups})
        yield f"data: {done}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    if not request.extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    try:
        summary = summarize_contract(request.extracted_text)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/detect-risks")
def detect_risks_endpoint(request: RiskRequest):
    if not request.extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    try:
        risks = detect_risks(request.extracted_text)
        return risks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk detection failed: {str(e)}")


@app.post("/extract-financials")
def extract_financials_endpoint(request: SummarizeRequest):
    if not request.extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    try:
        result = extract_financials(request.extracted_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial extraction failed: {str(e)}")


@app.post("/extract-timeline")
def extract_timeline_endpoint(request: SummarizeRequest):
    if not request.extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    try:
        result = extract_timeline(request.extracted_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline extraction failed: {str(e)}")


@app.post("/generate-report")
def generate_report_endpoint(request: ReportRequest):
    if not request.extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    try:
        result = generate_report(
            extracted_text=request.extracted_text,
            file_name=request.file_name,
            file_size=request.file_size,
            page_count=request.page_count,
            word_count=request.word_count,
            collection_name=request.collection_name,
            include_summary=request.include_summary,
            include_risks=request.include_risks,
            include_clauses=request.include_clauses,
            include_financials=request.include_financials,
            include_timeline=request.include_timeline,
            include_obligations=request.include_obligations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/extract-clauses")
def extract_clauses(request: ClauseRequest):
    if not request.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided.")
    try:
        clauses = classify_chunks(request.chunks[:20])
        return {"clauses": clauses, "total": len(clauses)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clause extraction failed: {str(e)}")

@app.post("/download-report")
def download_report(request: ReportRequest):
    if not request.extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    try:
        report_data = generate_report(
            extracted_text=request.extracted_text,
            file_name=request.file_name,
            file_size=request.file_size,
            page_count=request.page_count,
            word_count=request.word_count,
            collection_name=request.collection_name,
            include_summary=request.include_summary,
            include_risks=request.include_risks,
            include_clauses=request.include_clauses,
            include_financials=request.include_financials,
            include_timeline=request.include_timeline,
            include_obligations=request.include_obligations
        )
        pdf_bytes = generate_pdf_report(report_data)
        filename = request.file_name.replace(".pdf", "_review_report.pdf")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")