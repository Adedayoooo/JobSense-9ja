__JobSense Nigeria 🇳🇬__

An AI-powered job application assistant for Nigerian tech job seekers. Paste a job description and your CV — get a match score, skill gap analysis, and a tailored cover letter in seconds.

---

## What It Does

- **Job Analysis** — extracts required skills, seniority, red flags, and responsibilities from any JD
- **CV Analysis** — parses your CV into structured data without inferring skills you don't have
- **Gap Analysis** — scores your match (0–100%), lists what you have, what's missing, and quick wins
- **Cover Letter** — writes a tailored letter specific to the company and role using RAG-retrieved company knowledge
- **Company Knowledge Base** — built-in intelligence on Nigerian tech companies (Flutterwave, Paystack, Kuda, Andela, and more)

---

## Tech Stack
```
| Layer | Technology |
|---|---|
| LLM | Groq API (LLaMA 3) |
| Vector DB | ChromaDB |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| API | FastAPI |
| Containerization | Docker |

---

## Project Structure

jobsense-nigeria/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI routes
│   └── schemas.py       # Pydantic request/response models
├── src/
│   ├── __init__.py
│   ├── config.py        # API keys and constants
│   ├── analyzers.py     # LLM client + JD and CV analyzers
│   ├── rag.py           # ChromaDB + company knowledge base
│   └── pipeline.py      # Gap analysis + cover letter + main jobsense() function
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```
---

## Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/Adedayoooo/jobsense-nigeria.git
cd jobsense-nigeria
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
Open `src/config.py` and replace:
```python
GROQ_API_KEY = "paste-your-key-here"
```
Get a free key at [console.groq.com](https://console.groq.com) — no credit card needed.

### 4. Run the API
```bash
uvicorn app.main:app --reload
```

### 5. Try it
Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | App info and available endpoints |
| GET | `/health` | Health check |
| POST | `/analyze` | Full analysis — JD + CV → report + cover letter |

### Example Request
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Flutterwave is hiring an ML Engineer...",
    "cv_text": "ADEBAYO ADEYEMI ADEBAYO..."
  }'
```

### Example Response
```json
{
  "job": {
    "company_name": "Flutterwave",
    "role_title": "Machine Learning Engineer",
    "seniority": "mid",
    "required_skills": ["Python", "scikit-learn", "Docker", "SQL"]
  },
  "gap": {
    "match_score": 73,
    "verdict": "Decent Match",
    "should_apply": true,
    "matched_skills": ["python", "docker", "sql"],
    "missing_skills": ["kubernetes", "kafka"],
    "quick_wins": ["Add 'distributed systems' to CV summary"],
    "honest_advice": "Strong ML fundamentals..."
  },
  "cover_letter": "Dear Hiring Manager at Flutterwave..."
}
```

---

## Run with Docker

```bash
docker build -t jobsense-nigeria .
docker run -p 7860:7860 jobsense-nigeria
```

## Built By

**Adedayo Adeyemi Adebayo**
- GitHub: [github.com/Adedayoooo](https://github.com/Adedayoooo)
- LinkedIn: [linkedin.com/in/adebayo-adebayo-64b23226b](https://linkedin.com/in/adebayo-adebayo-64b23226b)

---

## License

MIT
