from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from services.llm_utils import get_llm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from services.pdf_parser import extract_text
import tempfile
import shutil
import os

router = APIRouter()

# ---------- Request & Response Models ----------
class ResumeAdvisorRequest(BaseModel):
    resume: str
    jd: str
    model: str  # "openai", "mistral", "gemini", or "groq"
    openai_api_key: str | None = None
    mistral_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None

class ResumeAdvisorResponse(BaseModel):
    advisor_output: str

# ---------- Endpoint ----------
@router.post("/resume-advisor", response_model=ResumeAdvisorResponse)
async def resume_advisor(data: ResumeAdvisorRequest):
    """
    Generates actionable resume improvement suggestions based on the job description.
    Supports OpenAI, Mistral, Gemini, and Groq models.
    """
    try:
        # ✅ Select appropriate LLM dynamically
        llm = get_llm(
            model_name=data.model,
            openai_api_key=data.openai_api_key,
            mistral_api_key=data.mistral_api_key,
            gemini_api_key=data.gemini_api_key,
            groq_api_key=data.groq_api_key,
        )

        # Prompt template
        prompt = PromptTemplate.from_template("""
        You are an expert career advisor helping users tailor their resume for a specific job description.

        Job Description:
        {jd}

        Resume:
        {resume}

        Based on this, please:
        1. Identify missing skills, qualifications, or experiences
        2. Suggest specific additions or edits to improve the resume
        3. Make your suggestions actionable and concise
        4. Format your response as readable bullet points under clear headings like "Missing Skills" and "Suggestions". Do not use JSON or brackets.
        """)

        # LLM Chain
        chain = LLMChain(llm=llm, prompt=prompt)

        # Run LLM
        response = chain.run(resume=data.resume, jd=data.jd)

        return ResumeAdvisorResponse(advisor_output=response.strip())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- File Upload Endpoints ----------
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
