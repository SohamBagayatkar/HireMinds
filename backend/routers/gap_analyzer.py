from fastapi import APIRouter, UploadFile, File
from models.request_models import GapAnalyzerRequest
from services.embeddings import calculate_gap_score
from services.pdf_parser import extract_text
from services.readability import calculate_readability
import tempfile
import shutil
import os

router = APIRouter()

@router.post("/gap-analyzer")
async def analyze_gap(data: GapAnalyzerRequest):
    """
    Computes ATS score and readability score with feedback.
    Supports user-provided API keys for OpenAI, Gemini, Mistral, and Groq.
    """

    # Normalize model name
    model_name = (data.model or "").lower()
    if model_name not in ["openai", "mistral", "gemini", "groq"]:
        raise ValueError(f"Unsupported model selected: {data.model}")

    # --- ATS Score ---
    ats_result = calculate_gap_score(
        resume_text=data.resume_text,
        jd_text=data.jd_text,
        user_model=model_name,
        openai_api_key=data.openai_api_key,
        gemini_api_key=data.gemini_api_key,
        mistral_api_key=data.mistral_api_key,
        groq_api_key=data.groq_api_key
    )

    # --- Readability Score & Feedback ---
    readability_result = calculate_readability(
        resume_text=data.resume_text,
        model_name=model_name,
        openai_api_key=data.openai_api_key,
        gemini_api_key=data.gemini_api_key,
        mistral_api_key=data.mistral_api_key,
        groq_api_key=data.groq_api_key
    )

    # --- Combine Results ---
    return {
        # ATS
        "score": ats_result["score"],
        "matched_skills": ats_result["matched_skills"],
        "missing_skills": ats_result["missing_skills"],
        "total_resume_skills": ats_result["total_resume_skills"],
        "total_jd_skills": ats_result["total_jd_skills"],

        # Readability
        "readability_score": readability_result["readability_score"],
        "readability_feedback": readability_result["llm_feedback"],
    }

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload resume (PDF/DOCX), extract text and return it.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
    finally:
        os.remove(tmp_path)

    return {"extracted_text": text}

@router.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    """
    Upload Job Description (PDF/DOCX), extract text and return it.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
    finally:
        os.remove(tmp_path)

    return {"extracted_text": text}
