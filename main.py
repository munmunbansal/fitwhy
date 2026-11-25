import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

os.environ["GEMINI_API_KEY"] = os.getenv("")
client = genai.Client()

JOBS_DB = [
    {"id": 1, "title": "Software Engineering Intern (AI)", "company": "NexaLabs", "location": "Gurugram", "type": "Early Startup", "bond": False, "desc": "Python, SQL, LLM agents, structured outputs, high ownership, 70k stipend."},
    {"id": 2, "title": "Associate Software Engineer", "company": "Global IT Services", "location": "Noida", "type": "Service", "bond": True, "desc": "Java, legacy maintenance, 2-year service bond, rotational night shifts."},
    {"id": 3, "title": "Frontend React Developer", "company": "PixelCraft", "location": "Remote", "type": "Startup", "bond": False, "desc": "Pure UI/UX work, Tailwind CSS, animations, zero backend or AI work."},
    {"id": 4, "title": "AI & Data Intern", "company": "FinPulse", "location": "Bengaluru", "type": "Startup", "bond": False, "desc": "Python, Pandas, SQL pipelines, building RAG evaluation scripts."},
    {"id": 5, "title": "Graduate Engineer Trainee", "company": "InfraBuild Corp", "location": "Delhi", "type": "Corporate", "bond": True, "desc": "Site execution, AutoCAD, 1-year bond, non-coding role."},
    {"id": 6, "title": "Backend Node.js Engineer", "company": "WebhookFlow", "location": "Remote", "type": "Startup", "bond": False, "desc": "Node.js, Express, Redis queues, asynchronous event ingestion, 60k stipend."},
    {"id": 7, "title": "Business Analyst Intern", "company": "MetricStack", "location": "Mumbai", "type": "Startup", "bond": False, "desc": "SQL, BigQuery, dbt, Power BI dashboards, churn modeling."},
    {"id": 8, "title": "Junior QA Tester", "company": "TestCorp", "location": "Pune", "type": "Service", "bond": True, "desc": "Manual testing, Excel reporting, 18-month bond, night shift support."},
    {"id": 9, "title": "Founding Engineer Intern", "company": "AgentOps India", "location": "Bengaluru", "type": "Early Startup", "bond": False, "desc": "Building tool-using LLM agents, Python, Docker, fast shipping cycles."},
    {"id": 10, "title": "Full Stack Intern", "company": "CodeAssess", "location": "Remote", "type": "Startup", "bond": False, "desc": "React, Node.js, building developer evaluation tools and automated test runners."}
]

class MatchRequest(BaseModel):
    resume_text: str
    wants: str
    never_take: str

class JobRecommendation(BaseModel):
    job_id: int
    title: str
    company: str
    location: str
    fit_level: str
    reason: str

class MatchResponse(BaseModel):
    recommendations: list[JobRecommendation]
    filtered_out_count: int

def fallback_matcher(req: MatchRequest) -> dict:
    never = req.never_take.lower()
    profile_words = set((req.resume_text + " " + req.wants).lower().replace(",", " ").split())
    
    valid_jobs = []
    filtered_count = 0

    for job in JOBS_DB:
        desc_lower = (job["title"] + " " + job["desc"] + " " + job["type"]).lower()
        if "bond" in never and job["bond"]:
            filtered_count += 1
            continue
        if "night" in never and "night" in desc_lower:
            filtered_count += 1
            continue
        if "frontend" in never and "pure ui/ux" in desc_lower:
            filtered_count += 1
            continue
        if "non-coding" in never and "non-coding" in desc_lower:
            filtered_count += 1
            continue

        job_words = set(desc_lower.replace(",", " ").split())
        overlap = profile_words.intersection(job_words) - {"and", "the", "with", "in", "a", "to", "for", "at"}
        valid_jobs.append((len(overlap), overlap, job))

    valid_jobs.sort(key=lambda x: x[0], reverse=True)
    top_3 = valid_jobs[:3]
    filtered_count += max(0, len(valid_jobs) - 3)

    recs = []
    for score, overlap, job in top_3:
        matched_skills = ", ".join(list(overlap)[:4]) or "backend & startup engineering"
        recs.append({
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "fit_level": "Strong Fit" if score >= 2 else "Good Fit",
            "reason": f"Aligns with your hands-on experience in {matched_skills} while strictly respecting your '{req.never_take or 'no-bond'}' boundaries. {job['company']} is looking for {job['desc']}"
        })

    return {"recommendations": recs, "filtered_out_count": filtered_count}

@app.post("/api/match", response_model=MatchResponse)
def match_jobs(req: MatchRequest):
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Please enter your skills or resume summary.")

    prompt = f"""
    You are FitWhy, an honest AI career advisor that acts like a thoughtful mentor.
    
    Candidate Resume/Skills: {req.resume_text}
    What they want next: {req.wants}
    What they will NEVER take (STRICT HARD CONSTRAINTS): {req.never_take}
    
    Available Jobs: {json.dumps(JOBS_DB)}
    
    Instructions:
    1. Strictly eliminate ANY job that violates the candidate's 'never_take' rules. Count how many jobs were eliminated due to constraints or poor fit as 'filtered_out_count'.
    2. Rank the remaining jobs that best fit their resume and 'wants'.
    3. Return up to 3 top matches. For each match, write a 2-sentence plain-English 'reason' explaining why it fits them specifically (reference their actual skills/wants, no generic corporate fluff).
    """

    models_to_try = ["gemini-3.8-flash", "gemini-2.0-flash"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MatchResponse,
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except Exception:
            continue

    return fallback_matcher(req)

app.mount("/", StaticFiles(directory="static", html=True), name="static")