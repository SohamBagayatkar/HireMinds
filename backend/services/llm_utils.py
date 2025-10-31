import os
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq  # Groq integration (Llama 3 models)

# Supported models mapping
MODEL_MAP = {
    "openai": "gpt-4o-mini",
    "mistral": "mistral-small-latest",
    "gemini": "gemini-2.5-flash",
    "groq": "llama-3.3-70b-versatile"  # Default Groq model
}

def get_llm(
    model_name: str,
    openai_api_key: str = None,
    gemini_api_key: str = None,
    groq_api_key: str = None,
    mistral_api_key: str = None  # <-- new parameter
):
    model_name = (model_name or "").strip().lower()

    if model_name == "openai":
        if not openai_api_key:
            raise ValueError("OpenAI API key required for OpenAI models.")
        return ChatOpenAI(model=MODEL_MAP["openai"], temperature=0.4, openai_api_key=openai_api_key)

    elif model_name == "mistral":
        key = mistral_api_key or os.getenv("MISTRAL_API_KEY")
        if not key:
            raise ValueError("Mistral API key required for Mistral models.")
        return ChatMistralAI(model=MODEL_MAP["mistral"], temperature=0.4, api_key=key)

    elif model_name == "gemini":
        key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API key required for Gemini models.")
        return ChatGoogleGenerativeAI(model=MODEL_MAP["gemini"], temperature=0.4, google_api_key=key)

    elif model_name == "groq":
        key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("Groq API key required for Groq models.")
        return ChatGroq(model=MODEL_MAP["groq"], temperature=0.4, api_key=key)

    else:
        raise ValueError(f"Unsupported model: {model_name}. Choose from openai, mistral, gemini, groq.")
