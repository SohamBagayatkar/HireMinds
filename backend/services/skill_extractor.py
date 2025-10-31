import os
import spacy
from typing import Dict, Set
from mistralai.client import MistralClient
from openai import OpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import json

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load curated skill list
SKILLS_FILE = os.path.join(os.path.dirname(__file__), "skills_list.json")
with open(SKILLS_FILE, "r", encoding="utf-8") as f:
    SKILL_WHITELIST = set(json.load(f))

# Load parent-child skill mapping
PARENT_SKILLS_FILE = os.path.join(os.path.dirname(__file__), "parent_skills.json")
with open(PARENT_SKILLS_FILE, "r", encoding="utf-8") as f:
    PARENT_SKILL_MAP = json.load(f)

# ---------- Normalization Helpers ---------- #
def normalize_skill(skill: str) -> str:
    """Normalize skill (lowercase, collapse spaces, remove punctuation except + # .)."""
    skill = skill.strip().lower()
    skill = re.sub(r"[^a-z0-9\+\#\. ]", "", skill)  # keep alphanum, +, #, .
    skill = re.sub(r"\s+", " ", skill)              # collapse spaces
    return skill.strip()

# Canonical whitelist map (normalized -> original)
NORMALIZED_WHITELIST = {normalize_skill(s): s for s in SKILL_WHITELIST}

# ---------- Parent-child lookup ---------- #
CHILD_TO_PARENT: Dict[str, Set[str]] = {}
PARENT_TO_CHILDREN: Dict[str, Set[str]] = {}

for parent, children in PARENT_SKILL_MAP.items():
    parent_norm = normalize_skill(parent)
    child_norms = {normalize_skill(c) for c in children}
    PARENT_TO_CHILDREN[parent_norm] = child_norms
    for child in children:
        CHILD_TO_PARENT.setdefault(normalize_skill(child), set()).add(parent_norm)

# ---------- Skill Extraction ---------- #
def extract_skills_spacy(text: str) -> Set[str]:
    """Extract skills/entities using spaCy and filter with whitelist."""
    doc = nlp(text)
    raw_skills = set()

    for token in doc:
        if token.pos_ in ["PROPN", "NOUN", "ADJ"] and len(token.text) > 1:
            raw_skills.add(token.text.strip())

    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:
            raw_skills.add(chunk.text.strip())

    final = set()
    for s in raw_skills:
        norm = normalize_skill(s)
        if norm in NORMALIZED_WHITELIST:
            final.add(NORMALIZED_WHITELIST[norm])  # return canonical
    return final

def extract_skills_llm(
    text: str,
    model: str = "mistral",
    openai_key: str = None,
    groq_key: str = None,
    gemini_key: str = None
) -> Set[str]:
    """Use LLM (Mistral, OpenAI, Groq, Gemini) to extract skill list."""
    prompt = f"""
    Extract a list of skills, tools, or technologies from the following text.
    Return only a JSON array of skills (e.g. ["Python", "Docker"]).

    Text:
    {text}
    """

    content = None
    if model == "openai" and openai_key:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()

    elif model == "groq" and groq_key:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)
        response = llm.invoke(prompt)
        content = response.content.strip()

    elif model == "gemini" and gemini_key:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_key)
        response = llm.invoke(prompt)
        content = response.content.strip()

    elif model == "mistral":
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_key:
            raise ValueError("MISTRAL_API_KEY is missing in environment variables.")
        mistral = MistralClient(api_key=mistral_key)
        response = mistral.chat(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
    else:
        raise ValueError(f"Unsupported model: {model}")

    # Parse JSON safely
    skills = set()
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            for s in parsed:
                if isinstance(s, str):
                    norm = normalize_skill(s)
                    if norm in NORMALIZED_WHITELIST:
                        skills.add(NORMALIZED_WHITELIST[norm])
    except Exception:
        for s in re.split(r"[,;\n]", content):
            norm = normalize_skill(s)
            if norm in NORMALIZED_WHITELIST:
                skills.add(NORMALIZED_WHITELIST[norm])

    return skills

def hybrid_extract_skills(
    text: str,
    model: str = "mistral",
    openai_key: str = None,
    groq_key: str = None,
    gemini_key: str = None,
    min_skills_threshold: int = 8
) -> Set[str]:
    """Combine spaCy + LLM extraction with normalization."""
    spacy_skills = extract_skills_spacy(text)
    llm_skills = set()

    if len(spacy_skills) < min_skills_threshold:
        llm_skills = extract_skills_llm(
            text, model, openai_key=openai_key, groq_key=groq_key, gemini_key=gemini_key
        )

    return spacy_skills.union(llm_skills)

# ---------- Parent Filtering ---------- #
def _filter_parent_skills(skills: Set[str]) -> Set[str]:
    """Drop parent skills if children present."""
    skills_norm = {normalize_skill(s) for s in skills}
    filtered = set(skills)

    for parent_norm, children_norm in PARENT_TO_CHILDREN.items():
        if parent_norm in skills_norm and any(c in skills_norm for c in children_norm):
            filtered = {s for s in filtered if normalize_skill(s) != parent_norm}
    return filtered

def _filter_missing_parents(missing: Set[str], resume_skills: Set[str]) -> Set[str]:
    """Drop parent skills from missing if resume has children."""
    missing_norm = {normalize_skill(s) for s in missing}
    resume_norm = {normalize_skill(s) for s in resume_skills}
    filtered = set(missing)

    for parent_norm, children_norm in PARENT_TO_CHILDREN.items():
        if parent_norm in missing_norm and any(c in resume_norm for c in children_norm):
            filtered = {s for s in filtered if normalize_skill(s) != parent_norm}
    return filtered

# ---------- Compare Resume vs JD ---------- #
def compare_skills(
    resume_text: str,
    jd_text: str,
    model: str = "mistral",
    openai_key: str = None,
    groq_key: str = None,
    gemini_key: str = None
) -> Dict:
    """Compare resume vs JD skills and calculate ATS score."""
    resume_raw = hybrid_extract_skills(resume_text, model, openai_key, groq_key, gemini_key)
    jd_raw = hybrid_extract_skills(jd_text, model, openai_key, groq_key, gemini_key)

    resume_skills = _filter_parent_skills(resume_raw)
    jd_skills = _filter_parent_skills(jd_raw)

    matched = sorted(list(resume_skills & jd_skills))
    missing_initial = jd_skills - resume_skills
    missing = sorted(list(_filter_missing_parents(missing_initial, resume_skills)))

    ats_score = round((len(matched) / max(1, len(jd_skills))) * 100, 2)

    return {
        "ats_score": ats_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "total_resume_skills": sorted(list(resume_skills)),
        "total_jd_skills": sorted(list(jd_skills))
    }
