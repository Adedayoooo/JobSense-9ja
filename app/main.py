# app/main.py

from fastapi import FastAPI, HTTPException
from app.schemas import AnalyzeRequest, AnalyzeResponse
from src.pipeline import jobsense
from src.config import APP_TITLE, APP_DESCRIPTION, VERSION

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=VERSION
)


@app.get("/")
def root():
    return {
        "app": APP_TITLE,
        "version": VERSION,
        "status": "running",
        "endpoints": {
            "analyze": "POST /analyze",
            "health":  "GET /health",
            "docs":    "GET /docs"
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    """
    Main endpoint. Takes job description + CV, returns full report.
    """
    try:
        result = jobsense(
            job_description=request.job_description,
            cv_text=request.cv_text
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
