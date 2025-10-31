import re
from typing import Dict
from fuzzywuzzy import fuzz
from services.llm_utils import get_llm

# --- Section keywords mapping for flexible detection ---
SECTION_KEYWORDS = {
    "contact_info": ["contact", "email", "phone", "address", "mobile"],
    "summary": ["summary", "objective", "profile", "overview"],
    "work_experience": ["experience", "employment", "professional", "projects", "roles"],
    "education": ["education", "degree", "university", "college", "school"],
    "skills": ["skills", "technologies", "tools", "competencies"]
}

# --- Grammar / syntax checks ---
def check_grammar(text: str) -> Dict:
    spelling_errors = len(re.findall(r'\bteh\b|\brecieve\b|\bmanagment\b', text.lower()))
    punctuation_issues = len(re.findall(r'[^.!?]\n', text))
    return {
        "spelling_errors": spelling_errors,
        "punctuation_issues": punctuation_issues
    }

# --- Section detection using fuzzy matching ---
def detect_sections(text: str) -> Dict[str, bool]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    detected = {}
    for section, keywords in SECTION_KEYWORDS.items():
        detected[section] = any(
            fuzz.partial_ratio(line.lower(), kw.lower()) > 70 or kw.lower() in line.lower()
            for line in lines
            for kw in keywords
        )
    return detected

# --- Readability score calculation ---
def calculate_readability_score(resume_text: str) -> Dict:
    sections_detected = detect_sections(resume_text)
    grammar_issues = check_grammar(resume_text)

    total_lines = len(resume_text.split("\n"))
    non_empty_lines = len([l for l in resume_text.split("\n") if l.strip()])
    blank_ratio = (total_lines - non_empty_lines) / max(1, total_lines)
    parsability_score = max(0, 100 - int(blank_ratio * 100))

    section_score = int((sum(sections_detected.values()) / len(sections_detected)) * 100)
    grammar_penalty = min(20, grammar_issues["spelling_errors"] * 5 + grammar_issues["punctuation_issues"] * 3)
    readability_score = max(0, int(0.4 * parsability_score + 0.4 * section_score + 0.2 * (100 - grammar_penalty)))

    return {
        "readability_score": readability_score,
        "sections_detected": sections_detected,
        "grammar_issues": grammar_issues
    }

# --- Optional LLM feedback ---
def get_readability_feedback(
    resume_text: str,
    model_name: str,
    openai_api_key: str = None,
    gemini_api_key: str = None,
    mistral_api_key: str = None,   # ✅ Added Mistral
    groq_api_key: str = None
) -> str:
    llm = get_llm(
        model_name,
        openai_api_key=openai_api_key,
        gemini_api_key=gemini_api_key,
        mistral_api_key=mistral_api_key,  # ✅ Pass Mistral API key
        groq_api_key=groq_api_key
    )

    prompt = f"""
    You are a resume expert. Evaluate the following resume for readability, clarity, and formatting.
    Suggest improvements for:
    - Section completeness (Contact Info, Summary, Work Experience, Education, Skills)
    - Grammar, punctuation, and sentence clarity
    - Overall text layout and structure

    Resume Text:
    {resume_text}

    Provide clear actionable suggestions for improvement in 3-5 bullet points.
    """
    response = llm.predict(prompt)
    return response.strip()

# --- Combined function for gap analyzer ---
def calculate_readability(
    resume_text: str,
    model_name: str,
    openai_api_key: str = None,
    gemini_api_key: str = None,
    mistral_api_key: str = None,  # ✅ Added Mistral
    groq_api_key: str = None
) -> Dict:
    rules_result = calculate_readability_score(resume_text)
    llm_feedback = get_readability_feedback(
        resume_text,
        model_name,
        openai_api_key=openai_api_key,
        gemini_api_key=gemini_api_key,
        mistral_api_key=mistral_api_key,  # ✅ Pass Mistral key
        groq_api_key=groq_api_key
    )
    return {
        **rules_result,
        "llm_feedback": llm_feedback
    }
