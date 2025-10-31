import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import routers
from routers import (
    gap_analyzer,
    resume_advisor,
    resume_screening,  # ✅ Added this line
)

# Initialize FastAPI app
app = FastAPI(
    title="ATS Smart Advisor & HR Assist API",
    description=(
        "Backend API for ATS (Resume Advisor, Gap Analyzer, Resume Screening, Interview Guide, Job Search) "
        "and HR Assist (JD Generator, Resume Screening)"
    ),
    version="1.0.0",
)

# Enable CORS for frontend (Next.js or any other)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ATS Routers
app.include_router(gap_analyzer.router, prefix="/api", tags=["Gap Analyzer"])
app.include_router(resume_advisor.router, prefix="/api", tags=["Resume Advisor"])
app.include_router(resume_screening.router, prefix="/api", tags=["Resume Screening"])  # ✅ Added this line

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "🚀 ATS Smart Advisor & HR Assist API is running successfully!"}
