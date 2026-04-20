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

# Load parent-child mapping
PARENT_SKILLS_FILE = os.path.join(os.path.dirname(__file__), "parent_skills.json")
with open(PARENT_SKILLS_FILE, "r", encoding="utf-8") as f:
    PARENT_SKILL_MAP = json.load(f)

# ---------- Normalization ---------- #

def normalize_skill(skill: str) -> str:
    skill = skill.strip().lower()
    skill = re.sub(r"\b\d+(\.\d+)?\b", "", skill)
    skill = re.sub(r"[^a-z0-9\+\#\. ]", "", skill)
    skill = re.sub(r"\s+", " ", skill).strip()

    if skill.endswith("s") and len(skill) > 3:
        skill = skill[:-1]

    return skill


NORMALIZED_WHITELIST = {normalize_skill(s): s for s in SKILL_WHITELIST}

# ---------- Parent-child mapping ---------- #

CHILD_TO_PARENT: Dict[str, Set[str]] = {}
PARENT_TO_CHILDREN: Dict[str, Set[str]] = {}

for parent, children in PARENT_SKILL_MAP.items():
    parent_norm = normalize_skill(parent)
    child_norms = {normalize_skill(c) for c in children}
    PARENT_TO_CHILDREN[parent_norm] = child_norms

    for child in children:
        CHILD_TO_PARENT.setdefault(normalize_skill(child), set()).add(parent_norm)

# ---------- Mapping (FIXED) ---------- #

def map_to_known_skill(norm: str):
    # exact match
    if norm in NORMALIZED_WHITELIST:
        return NORMALIZED_WHITELIST[norm]

    # ✅ only allow partial match for multi-word phrases
    if len(norm.split()) > 1:
        for w_norm, original in NORMALIZED_WHITELIST.items():
            if len(w_norm.split()) > 1:
                if norm in w_norm or w_norm in norm:
                    return original

    return None

# ---------- Extraction ---------- #

def extract_skills_spacy(text: str) -> Set[str]:
    doc = nlp(text)
    raw = set()

    for token in doc:
        if token.pos_ in ["PROPN", "NOUN"] and len(token.text) > 2:
            raw.add(token.text.strip())

    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:
            raw.add(chunk.text.strip())

    final = set()

    for s in raw:
        norm = normalize_skill(s)
        mapped = map_to_known_skill(norm)
        if mapped:
            final.add(mapped)

    return final


def extract_skills_llm(text: str, model: str, openai_key=None, groq_key=None, gemini_key=None) -> Set[str]:

    prompt = f"""
    Extract ONLY skills that are EXACTLY mentioned in the text.

    STRICT RULES:
    - Do NOT infer
    - Do NOT guess
    - Do NOT add related skills
    - Only extract exact words/phrases from text

    Return JSON array.

    Text:
    {text}
    """

    content = None

    if model == "openai" and openai_key:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()

    elif model == "groq" and groq_key:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)
        content = llm.invoke(prompt).content.strip()

    elif model == "gemini" and gemini_key:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_key)
        content = llm.invoke(prompt).content.strip()

    elif model == "mistral":
        mistral_key = openai_key or os.getenv("MISTRAL_API_KEY")
        mistral = MistralClient(api_key=mistral_key)
        response = mistral.chat(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()

    skills = set()

    try:
        parsed = json.loads(content)
        for s in parsed:
            norm = normalize_skill(s)
            mapped = map_to_known_skill(norm)
            if mapped:
                skills.add(mapped)
    except:
        for s in re.split(r"[,;\n]", content):
            norm = normalize_skill(s)
            mapped = map_to_known_skill(norm)
            if mapped:
                skills.add(mapped)

    # 🔥 remove hallucinations
    text_norm = normalize_skill(text)
    skills = {s for s in skills if normalize_skill(s) in text_norm}

    return skills


def hybrid_extract_skills(text, model, openai_key, groq_key, gemini_key):
    return extract_skills_spacy(text).union(
        extract_skills_llm(text, model, openai_key, groq_key, gemini_key)
    )

# ---------- Parent Expansion (FIXED) ---------- #

def expand_with_parents(skills: Set[str], jd_norm_set: Set[str]) -> Set[str]:
    expanded = set(skills)

    for skill in skills:
        norm = normalize_skill(skill)

        if norm in CHILD_TO_PARENT:
            for parent in CHILD_TO_PARENT[norm]:

                # ✅ ONLY add if JD expects it
                if parent in jd_norm_set:
                    if parent in NORMALIZED_WHITELIST:
                        expanded.add(NORMALIZED_WHITELIST[parent])

    return expanded

# ---------- Compare ---------- #

def compare_skills(
    resume_text: str,
    jd_text: str,
    model: str = "mistral",
    openai_key: str = None,
    groq_key: str = None,
    gemini_key: str = None
) -> Dict:

    jd_raw = hybrid_extract_skills(jd_text, model, openai_key, groq_key, gemini_key)

    jd_text_norm = normalize_skill(jd_text)

    # ---------- STRICT JD FILTER ----------
    jd_skills = set()

    for s in jd_raw:
        norm = normalize_skill(s)

        if norm in jd_text_norm:
            jd_skills.add(s)
            continue

        words = [w for w in norm.split() if len(w) > 3]

        if len(words) >= 2 and all(w in jd_text_norm for w in words):
            jd_skills.add(s)

    # prepare JD norm set
    jd_norm = {normalize_skill(s): s for s in jd_skills}
    jd_norm_set = set(jd_norm.keys())

    # expand JD
    jd_skills = expand_with_parents(jd_skills, jd_norm_set)

    # resume
    resume_skills = hybrid_extract_skills(resume_text, model, openai_key, groq_key, gemini_key)
    resume_skills = expand_with_parents(resume_skills, jd_norm_set)

    # ---------- MATCH ----------
    resume_norm = {normalize_skill(s): s for s in resume_skills}
    jd_norm = {normalize_skill(s): s for s in jd_skills}

    matched = set()

    for r_norm, r_orig in resume_norm.items():
        if r_norm in jd_norm:
            matched.add(r_orig)

    # ---------- MISSING ----------
    missing = set()

    for jd_skill in jd_skills:
        if normalize_skill(jd_skill) not in resume_norm:
            missing.add(jd_skill)

    return {
        "ats_score": round((len(matched) / max(1, len(jd_skills))) * 100, 2),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "total_resume_skills": sorted(resume_skills),
        "total_jd_skills": sorted(jd_skills)
    }