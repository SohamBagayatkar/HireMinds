from pydantic import BaseModel
from typing import List, Optional

class GapAnalyzerRequest(BaseModel):
    resume_text: str
    jd_text: str
    model: str  # e.g., "openai", "mistral", "gemini", "groq", etc.
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None

class GapAnalyzerResponse(BaseModel):
    score: float  # ATS score (0-100)
    matched_skills: List[str]  # Skills found in both resume and JD
    missing_skills: List[str]  # Skills required by JD but missing in resume
    total_resume_skills: List[str]  # All skills extracted from resume
    total_jd_skills: List[str]  # All skills extracted from JD

# ---------- Resume Advisor Models ----------
class ResumeAdvisorRequest(BaseModel):
    resume: str
    jd: str
    model: str  # openai, mistral, gemini, groq
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None

class ResumeAdvisorResponse(BaseModel):
    advisor_output: str  # The AI-generated resume improvement advice
