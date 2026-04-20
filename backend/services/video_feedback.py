from typing import List
from services.llm_utils import get_llm


def get_video_feedback(
    transcript_text: str,
    jd_text: str,
    matched_skills: List[str],
    missing_skills: List[str],
    model_name: str,
    openai_api_key: str = None,
    gemini_api_key: str = None,
    mistral_api_key: str = None,
    groq_api_key: str = None
) -> str:
    """
    Generate human-readable video resume feedback using LLM.
    Returns clean English text (NOT JSON).
    """

    llm = get_llm(
        model_name,
        openai_api_key=openai_api_key,
        gemini_api_key=gemini_api_key,
        mistral_api_key=mistral_api_key,
        groq_api_key=groq_api_key
    )

    prompt = f"""
You are an expert recruiter evaluating a VIDEO RESUME.

Analyze the candidate based on:
- Relevance to the job description
- Skills demonstrated in the video
- Missing important skills
- Clarity and communication (based on transcript)

---

Job Description:
{jd_text}

---

Transcript of Video Resume:
{transcript_text}

---

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

---

INSTRUCTIONS:
- Give clear, practical feedback in plain English
- Do NOT return JSON
- Do NOT use markdown or formatting symbols
- Keep it concise but insightful
- Write 4–6 bullet points OR a short paragraph

Focus on:
1. Strengths in the candidate’s profile
2. Gaps compared to the job description
3. Suggestions to improve the video resume
4. Any communication/presentation improvements

Output:
"""

    response = llm.predict(prompt)
    return response.strip()


def generate_video_feedback(
    transcript_text: str,
    jd_text: str,
    matched_skills: List[str],
    missing_skills: List[str],
    model_name: str,
    openai_api_key: str = None,
    gemini_api_key: str = None,
    mistral_api_key: str = None,
    groq_api_key: str = None
) -> str:
    """
    Wrapper (kept for consistency with your architecture).
    Returns clean feedback string.
    """

    return get_video_feedback(
        transcript_text,
        jd_text,
        matched_skills,
        missing_skills,
        model_name,
        openai_api_key,
        gemini_api_key,
        mistral_api_key,
        groq_api_key
    )