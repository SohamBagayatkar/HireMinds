from fastapi import APIRouter, UploadFile, File, Form
from services.video_processor import transcribe_video
from services.embeddings import calculate_gap_score
from services.video_feedback import generate_video_feedback
import tempfile
import shutil
import os

router = APIRouter()


@router.post("/video-gap-analyzer")
async def analyze_video_gap(
    video: UploadFile = File(...),
    jd_text: str = Form(...),
    model: str = Form(...),
    openai_api_key: str = Form(None),
    gemini_api_key: str = Form(None),
    mistral_api_key: str = Form(None),
    groq_api_key: str = Form(None),
):
    """
    Video Resume Gap Analyzer:
    - Transcribes video
    - Computes ATS score
    - Generates AI feedback (plain text)
    """

    model_name = (model or "").lower()

    if model_name not in ["openai", "mistral", "gemini", "groq"]:
        raise ValueError(f"Unsupported model selected: {model}")

    # -------------------------------
    # Save uploaded video temporarily
    # -------------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{video.filename}") as tmp:
        shutil.copyfileobj(video.file, tmp)
        tmp_path = tmp.name

    try:
        # -------------------------------
        # 1️⃣ Transcription
        # -------------------------------
        transcript_text = transcribe_video(tmp_path)

        # -------------------------------
        # 2️⃣ ATS Score
        # -------------------------------
        ats_result = calculate_gap_score(
            resume_text=transcript_text,
            jd_text=jd_text,
            user_model=model_name,
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            mistral_api_key=mistral_api_key,
            groq_api_key=groq_api_key,
        )

        # -------------------------------
        # 3️⃣ AI Video Feedback (TEXT ONLY)
        # -------------------------------
        video_feedback = generate_video_feedback(
            transcript_text=transcript_text,
            jd_text=jd_text,
            matched_skills=ats_result["matched_skills"],
            missing_skills=ats_result["missing_skills"],
            model_name=model_name,
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            mistral_api_key=mistral_api_key,
            groq_api_key=groq_api_key,
        )

    finally:
        # -------------------------------
        # Cleanup temp file
        # -------------------------------
        os.remove(tmp_path)

    # -------------------------------
    # Final Response
    # -------------------------------
    return {
        # ATS
        "score": ats_result["score"],
        "matched_skills": ats_result["matched_skills"],
        "missing_skills": ats_result["missing_skills"],
        "total_resume_skills": ats_result["total_resume_skills"],
        "total_jd_skills": ats_result["total_jd_skills"],
        "skill_score": ats_result["skill_score"],
        "embedding_score": ats_result["embedding_score"],

        # Optional debug
        "transcript_preview": transcript_text[:500],

        # ✅ CLEAN TEXT FEEDBACK
        "video_feedback": video_feedback
    }