# routers/resume_screening.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import tempfile
import shutil
import os

from services.pdf_parser import extract_text
from services.embeddings import calculate_gap_score  # Use embeddings module

router = APIRouter()


@router.post("/resume-screening")
async def resume_screening(
    jd_file: UploadFile = File(...),
    resumes: List[UploadFile] = File(...),
    openai_api_key: Optional[str] = Form(None),
):
    """
    Screen multiple resumes against a Job Description using OpenAI embeddings (text-embedding-3-small).
    Returns ATS scores, matched and missing skills for each resume ranked descending.
    """

    if not openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key is required.")

    if not (2 <= len(resumes) <= 10):
        raise HTTPException(status_code=400, detail="Upload between 2 and 10 resumes.")

    # --- Extract JD text ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{jd_file.filename}") as tmp:
        shutil.copyfileobj(jd_file.file, tmp)
        jd_path = tmp.name
    try:
        jd_text = extract_text(jd_path)
    finally:
        os.remove(jd_path)

    results = []

    # --- Process each resume ---
    for resume in resumes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{resume.filename}") as tmp:
            shutil.copyfileobj(resume.file, tmp)
            resume_path = tmp.name
        try:
            resume_text = extract_text(resume_path)
        finally:
            os.remove(resume_path)

        # --- Calculate ATS score using OpenAI embeddings ---
        ats_result = calculate_gap_score(
            resume_text=resume_text,
            jd_text=jd_text,
            user_model="openai",
            openai_api_key=openai_api_key
        )

        results.append({
            "resume_name": resume.filename,
            "score": ats_result["score"],
            "skill_score": ats_result.get("skill_score"),
            "embedding_score": ats_result.get("embedding_score"),
            "matched_skills": ats_result.get("matched_skills", []),
            "missing_skills": ats_result.get("missing_skills", []),
            "total_resume_skills": ats_result.get("total_resume_skills", 0),
            "total_jd_skills": ats_result.get("total_jd_skills", 0),
        })

    # --- Rank resumes by score descending ---
    ranked_results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {"ranked_resumes": ranked_results}
