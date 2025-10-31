import numpy as np
from typing import Dict, Optional
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_mistralai import MistralAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from services.skill_extractor import compare_skills  # Skill extraction module

def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_embedding_model(
    user_model: str,
    openai_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    mistral_api_key: Optional[str] = None,
    groq_api_key: Optional[str] = None
):
    """
    Returns an embedding model based on the user's selection:
    - openai -> OpenAI embeddings
    - mistral -> Mistral embeddings
    - groq -> HuggingFace embeddings (since Groq has no native embeddings)
    - gemini -> Google Generative AI embeddings
    """
    user_model = (user_model or "").lower()

    if user_model == "openai":
        if not openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI embeddings.")
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_api_key
        )

    elif user_model == "gemini":
        if not gemini_api_key:
            raise ValueError("Gemini API key is required when using Gemini embeddings.")
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api_key
        )

    elif user_model == "groq":
        # Groq has no embeddings → fallback to HuggingFace
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    elif user_model == "mistral":
        if not mistral_api_key:
            raise ValueError("Mistral API key is required when using Mistral embeddings.")
        return MistralAIEmbeddings(
            model="mistral-embed",
            api_key=mistral_api_key
        )

    else:
        raise ValueError(f"Unsupported model: {user_model}")

def calculate_gap_score(
    resume_text: str,
    jd_text: str,
    user_model: str,
    openai_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    mistral_api_key: Optional[str] = None,
    groq_api_key: Optional[str] = None
) -> Dict:
    """
    Calculates ATS score using a hybrid approach:
    - Skill-based matching (70% weight)
    - Embedding similarity (30% weight)
    """
    # --- Step 1: Skill extraction & comparison ---
    skill_data = compare_skills(resume_text, jd_text, user_model, openai_api_key)

    matched_count = len(skill_data["matched_skills"])
    total_jd_skills = len(skill_data["total_jd_skills"])
    skill_score = round((matched_count / max(1, total_jd_skills)) * 100, 2)

    # --- Step 2: Embedding-based similarity ---
    embedder = get_embedding_model(user_model, openai_api_key, gemini_api_key, mistral_api_key, groq_api_key)
    resume_vec = embedder.embed_query(resume_text)
    jd_vec = embedder.embed_query(jd_text)

    embedding_similarity = _cosine_similarity(np.array(resume_vec), np.array(jd_vec))
    embedding_score = round(embedding_similarity * 100, 2)

    # --- Step 3: Hybrid ATS Score ---
    final_score = round((0.7 * skill_score) + (0.3 * embedding_score), 2)

    # --- Step 4: Return structured result ---
    return {
        "score": final_score,
        "skill_score": skill_score,
        "embedding_score": embedding_score,
        "matched_skills": skill_data["matched_skills"],
        "missing_skills": skill_data["missing_skills"],
        "total_resume_skills": len(skill_data["total_resume_skills"]),
        "total_jd_skills": total_jd_skills,
    }
