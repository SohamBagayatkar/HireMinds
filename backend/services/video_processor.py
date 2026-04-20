import os
import re
import json
import ffmpeg
from faster_whisper import WhisperModel

# Load Whisper
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# -------------------------------
# 📂 Load Skills List
# -------------------------------

SKILLS_FILE = os.path.join(os.path.dirname(__file__), "skills_list.json")

with open(SKILLS_FILE, "r", encoding="utf-8") as f:
    SKILLS = json.load(f)

# -------------------------------
# 🔧 Normalization Helpers
# -------------------------------

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\.]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------
# 🧠 Build Skill Variations (CORE)
# -------------------------------

def generate_variations(skill: str):
    """
    Generate possible spoken/transcription variations for a skill.
    """
    skill_lower = skill.lower()

    variations = set()

    # Base
    variations.add(skill_lower)

    # Remove dots (next.js → nextjs)
    variations.add(skill_lower.replace(".", ""))

    # Replace dots with space (next js)
    variations.add(skill_lower.replace(".", " "))

    # Split camel case / PascalCase
    split = re.sub(r'([a-z])([A-Z])', r'\1 \2', skill).lower()
    variations.add(split)

    # Remove spaces (lang chain → langchain)
    variations.add(split.replace(" ", ""))

    # Space version (fastapi → fast api)
    spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', skill).lower()
    variations.add(spaced)

    # Special manual phonetic fixes
    if "langchain" in skill_lower:
        variations.add("long chain")

    if "streamlit" in skill_lower:
        variations.add("stream lit")

    if "tensorflow" in skill_lower:
        variations.add("tensor flow")

    return {normalize(v) for v in variations}


# Build variation map
VARIATION_MAP = {}

for skill in SKILLS:
    for variant in generate_variations(skill):
        VARIATION_MAP[variant] = skill.lower()


# -------------------------------
# 🔥 Skill-aware Fuzzy Correction
# -------------------------------

def fix_transcript(text: str) -> str:
    """
    Replace spoken variations with canonical skill forms.
    """
    text = normalize(text)

    for variant, canonical in VARIATION_MAP.items():
        if variant in text:
            text = re.sub(rf"\b{re.escape(variant)}\b", canonical, text)

    return text


# -------------------------------
# 🎯 Audio Extraction
# -------------------------------

def extract_audio(video_path: str) -> str:
    audio_path = video_path + ".wav"

    (
        ffmpeg
        .input(video_path)
        .output(audio_path, format="wav", acodec="pcm_s16le", ac=1, ar="16000")
        .overwrite_output()
        .run(quiet=True)
    )

    return audio_path


# -------------------------------
# 🧹 Cleaning
# -------------------------------

def clean_transcript(text: str) -> str:
    text = text.lower()

    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -------------------------------
# 🧠 Optional LLM Enhancement
# -------------------------------

def llm_correct_transcript(text: str) -> str:
    """
    Optional advanced correction layer.
    Plug your LLM here if needed.
    """
    return text


# -------------------------------
# 🎤 Main Pipeline
# -------------------------------

def transcribe_video(video_path: str) -> str:
    audio_path = extract_audio(video_path)

    # 🌍 Domain-agnostic Whisper prompt
    segments, _ = whisper_model.transcribe(
        audio_path,
        initial_prompt=(
            "This is a technical interview discussing software engineering, programming, "
            "web development, mobile apps, cloud computing, DevOps, cybersecurity, data science, "
            "machine learning, and IT tools. Technologies may include Python, Java, JavaScript, React, "
            "Next.js, Node.js, FastAPI, Django, Flutter, Android, AWS, Azure, Docker, Kubernetes, "
            "TensorFlow, SQL, MongoDB, Git, APIs, and modern frameworks."
        )
    )

    transcript = " ".join(segment.text for segment in segments)

    os.remove(audio_path)

    # 🔥 Step 1: Skill-aware correction
    transcript = fix_transcript(transcript)

    # 🧹 Step 2: Clean
    transcript = clean_transcript(transcript)

    # 🧠 Step 3 (optional LLM)
    # transcript = llm_correct_transcript(transcript)

    return transcript