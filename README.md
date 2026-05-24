# HireMinds: Multi Modal Resume ATS Advisor

HireMinds is an Al-powered multi-modal Applicant Tracking System (ATS) and advisory platform designed to enhance the recruitment process for both job seekers and recruiters. Moving beyond traditional keyword-based filtering, HireMinds integrates Natural Language Processing (NLP), fuzzy matching techniques, and Large Language Models (LLMs) to provide an intelligent, semantic evaluation of candidate profiles.

## 🚀 Core Features

* **Hybrid ATS Scoring Engine:** Calculates a comprehensive compatibility score using a weighted formula that combines deterministic rule-based NLP skill matching (70% weight) with transformer-based semantic embedding similarity (30% weight).
* **Intelligent Resume Advisor:** Leverages LLMs to provide job seekers with a qualitative review, generating structured, actionable feedback on missing skills, project descriptions, and formatting.
* **Comprehensive Readability Framework:** Automatically evaluates text parsability, section completeness (e.g., contact info, education), and grammatical accuracy.
* **Multi-Resume Screening:** Allows recruiters to upload and evaluate multiple candidate resumes simultaneously, ranking them in descending order based on their hybrid ATS scores against a specific job description.
* **Video Resume Gap Analyzer:** Transcribes spoken video introductions using OpenAI's open-source Whisper model, analyzing the extracted text to evaluate communication clarity and alignment with role requirements.

## 🛠️ Technology Stack

**Frontend**
* Next.js (React-based user interface)

**Backend**
* FastAPI (High-performance asynchronous REST endpoints)
* Python 3.10+

**AI & Machine Learning Pipeline**
* **Multi-Model LLM Support:** Seamless orchestration across OpenAI, Mistral, Gemini, and Groq.
* **Embeddings & Similarity:** `text-embedding-3-small`, `mistral-embed`, and Hugging Face Transformers.
* **Frameworks:** LangChain for RAG pipelines and model orchestration, PyTorch/TensorFlow for core deep learning.
* **NLP & Extraction:** spaCy for Named Entity Recognition (NER), PyMuPDF, and python-docx for document parsing.
* **Speech-to-Text:** OpenAI Whisper.

---

## ⚙️ Setup Guide

### 1. Clone the Repository
'''bash
git clone [https://github.com/SohamBagayatkar/HireMinds.git](https://github.com/SohamBagayatkar/HireMinds.git)
cd HireMinds

cd backend
python -m venv venv

# Activate Virtual Environment
venv\Scripts\activate        # For Windows
# source venv/bin/activate   # For macOS/Linux

# Install Dependencies
pip install -r requirements.txt

# Run the FastAPI Server
uvicorn main:app --reload
cd ../frontend
npm install
npm run dev

👥 Contributors
Developed in partial fulfillment of the Bachelor of Technology in Information Technology.

Soham Bagayatkar

Sahil Sunil Naik

Pavankumar Singh

