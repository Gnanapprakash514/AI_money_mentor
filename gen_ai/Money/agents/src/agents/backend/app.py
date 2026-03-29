# =============================================================================
# app.py — Detailed FastAPI backend for AI Money Mentor
# =============================================================================

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

# ── Path setup ───────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]   # src/
sys.path.insert(0, str(ROOT))

# ── Load .env before any CrewAI/LLM imports ──────────────────────────────────
_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
if _ENV_PATH.exists():
    for _line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from agents.crew import FIRECrew, FeedCrew, HealthCrew, OnboardingCrew, TaxCrew

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUTS_DIR  = Path(__file__).resolve().parents[3] / "outputs"
PROFILE_PATH = OUTPUTS_DIR / "financial_profile.json"
JOBS_PATH    = OUTPUTS_DIR / "jobs.json"

OUTPUT_FILES = {
    "fire":    OUTPUTS_DIR / "fire_roadmap.md",
    "tax":     OUTPUTS_DIR / "tax_analysis.md",
    "health":  OUTPUTS_DIR / "health_score.md",
    "feed":    OUTPUTS_DIR / "daily_feed.md",
    "profile": PROFILE_PATH,
}

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Money Mentor API",
    version="2.0.0",
    description="Backend API for AI-powered personal finance planning using CrewAI agents.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Job store (file-backed) ───────────────────────────────────────────────────

def _load_jobs() -> Dict[str, Any]:
    if JOBS_PATH.exists():
        return json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return {}


def _save_jobs(jobs: Dict[str, Any]) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(jobs, indent=2), encoding="utf-8")


def _update_job(job_id: str, **kwargs) -> None:
    jobs = _load_jobs()
    jobs.setdefault(job_id, {}).update(kwargs)
    _save_jobs(jobs)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_profile() -> str:
    if not PROFILE_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="No financial profile found. Complete /onboarding first.",
        )
    return PROFILE_PATH.read_text(encoding="utf-8")


def _crew_result(result) -> str:
    return str(result.raw) if hasattr(result, "raw") else str(result)


def _new_job(crew_type: str) -> str:
    job_id = str(uuid.uuid4())[:8]
    _update_job(job_id, crew=crew_type, status="running", started_at=datetime.utcnow().isoformat(), result=None, error=None)
    return job_id


# ── Request models ────────────────────────────────────────────────────────────

class MonthlyExpenses(BaseModel):
    housing:        int = Field(0, ge=0)
    groceries:      int = Field(0, ge=0)
    transportation: int = Field(0, ge=0)
    utilities:      int = Field(0, ge=0)
    entertainment:  int = Field(0, ge=0)
    savings:        int = Field(0, ge=0)
    debt_repayment: int = Field(0, ge=0)
    other:          int = Field(0, ge=0)


class OnboardingRequest(BaseModel):
    marital_status:           str            = Field(..., examples=["single"])
    age:                      int            = Field(..., ge=18, le=100)
    occupation:               str
    annual_income:            int            = Field(..., ge=0)
    monthly_take_home_salary: int            = Field(..., ge=0)
    monthly_expenses:         MonthlyExpenses
    risk_appetite:            str            = Field(..., examples=["Conservative", "Moderate", "Aggressive"])

    @field_validator("risk_appetite")
    @classmethod
    def validate_risk(cls, v: str) -> str:
        allowed = {"conservative", "moderate", "aggressive"}
        if v.lower() not in allowed:
            raise ValueError(f"risk_appetite must be one of {allowed}")
        return v.capitalize()


class FIRERequest(BaseModel):
    years:         int   = Field(..., ge=1, le=60, description="Years until target retirement")
    target_income: int   = Field(..., ge=0, description="Desired monthly income post-retirement (INR)")
    inflation:     float = Field(..., ge=0.0, le=20.0, description="Expected annual inflation rate (%)")


class TaxRequest(BaseModel):
    regime:     str = Field(..., examples=["old", "new"])
    deductions: int = Field(..., ge=0, description="Total planned deductions (INR)")

    @field_validator("regime")
    @classmethod
    def validate_regime(cls, v: str) -> str:
        if v.lower() not in {"old", "new"}:
            raise ValueError("regime must be 'old' or 'new'")
        return v.lower()


class HealthRequest(BaseModel):
    emergency_fund: int   = Field(..., ge=0, description="Emergency fund available (INR)")
    savings_rate:   float = Field(..., ge=0.0, le=100.0, description="Current savings rate (%)")


# ── Background runners ────────────────────────────────────────────────────────

def _run_fire_bg(job_id: str, profile: str, data: FIRERequest):
    try:
        result = FIRECrew().crew().kickoff(inputs={
            "profile": profile,
            "years": data.years,
            "target_income": data.target_income,
            "inflation": data.inflation,
        })
        _update_job(job_id, status="completed", result=_crew_result(result), finished_at=datetime.utcnow().isoformat())
    except Exception as e:
        _update_job(job_id, status="failed", error=str(e), finished_at=datetime.utcnow().isoformat())


def _run_tax_bg(job_id: str, profile: str, data: TaxRequest):
    try:
        result = TaxCrew().crew().kickoff(inputs={
            "profile": profile,
            "regime": data.regime,
            "deductions": data.deductions,
        })
        _update_job(job_id, status="completed", result=_crew_result(result), finished_at=datetime.utcnow().isoformat())
    except Exception as e:
        _update_job(job_id, status="failed", error=str(e), finished_at=datetime.utcnow().isoformat())


def _run_health_bg(job_id: str, profile: str, data: HealthRequest):
    try:
        result = HealthCrew().crew().kickoff(inputs={
            "profile": profile,
            "emergency_fund": data.emergency_fund,
            "savings_rate": data.savings_rate,
        })
        _update_job(job_id, status="completed", result=_crew_result(result), finished_at=datetime.utcnow().isoformat())
    except Exception as e:
        _update_job(job_id, status="failed", error=str(e), finished_at=datetime.utcnow().isoformat())


def _run_feed_bg(job_id: str, profile: str):
    try:
        result = FeedCrew().crew().kickoff(inputs={"profile": profile})
        _update_job(job_id, status="completed", result=_crew_result(result), finished_at=datetime.utcnow().isoformat())
    except Exception as e:
        _update_job(job_id, status="failed", error=str(e), finished_at=datetime.utcnow().isoformat())


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/", tags=["General"])
def root():
    """Health check — confirms the API is running."""
    return {
        "service": "AI Money Mentor API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/status", tags=["General"])
def status():
    """Returns which output files exist and whether a profile is loaded."""
    return {
        "profile_exists": PROFILE_PATH.exists(),
        "outputs": {name: path.exists() for name, path in OUTPUT_FILES.items()},
    }


# ── Profile ───────────────────────────────────────────────────────────────────

@app.get("/profile", tags=["Profile"])
def get_profile():
    """Return the stored financial profile as JSON."""
    raw = _load_profile()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Profile may be wrapped in markdown code fences by the LLM
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw": raw}


@app.delete("/profile", tags=["Profile"])
def delete_profile():
    """Delete the stored financial profile."""
    if not PROFILE_PATH.exists():
        raise HTTPException(status_code=404, detail="No profile to delete.")
    PROFILE_PATH.unlink()
    return {"message": "Profile deleted."}


@app.post("/onboarding", tags=["Profile"])
def onboarding(data: OnboardingRequest):
    """
    Run the Onboarding crew to build and persist a structured financial profile.
    This must be called before any analysis endpoint.
    """
    try:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        result = OnboardingCrew().crew().kickoff(inputs={"user_profile": data.model_dump()})
        return {
            "status": "success",
            "message": "Financial profile created and saved.",
            "result": _crew_result(result),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Analysis endpoints (async via BackgroundTasks) ────────────────────────────

@app.post("/fire", tags=["Analysis"])
def fire(data: FIRERequest, background_tasks: BackgroundTasks):
    """
    Launch the FIRE (Financial Independence, Retire Early) planning crew.
    Returns a job_id — poll /jobs/{job_id} for the result.
    """
    profile = _load_profile()
    job_id = _new_job("fire")
    background_tasks.add_task(_run_fire_bg, job_id, profile, data)
    return {"status": "accepted", "job_id": job_id, "poll": f"/jobs/{job_id}"}


@app.post("/tax", tags=["Analysis"])
def tax(data: TaxRequest, background_tasks: BackgroundTasks):
    """
    Launch the Tax Optimisation crew.
    Returns a job_id — poll /jobs/{job_id} for the result.
    """
    profile = _load_profile()
    job_id = _new_job("tax")
    background_tasks.add_task(_run_tax_bg, job_id, profile, data)
    return {"status": "accepted", "job_id": job_id, "poll": f"/jobs/{job_id}"}


@app.post("/health", tags=["Analysis"])
def health(data: HealthRequest, background_tasks: BackgroundTasks):
    """
    Launch the Financial Health Score crew.
    Returns a job_id — poll /jobs/{job_id} for the result.
    """
    profile = _load_profile()
    job_id = _new_job("health")
    background_tasks.add_task(_run_health_bg, job_id, profile, data)
    return {"status": "accepted", "job_id": job_id, "poll": f"/jobs/{job_id}"}


@app.post("/feed", tags=["Analysis"])
def feed(background_tasks: BackgroundTasks):
    """
    Launch the Daily Financial Feed crew.
    Returns a job_id — poll /jobs/{job_id} for the result.
    """
    profile = _load_profile()
    job_id = _new_job("feed")
    background_tasks.add_task(_run_feed_bg, job_id, profile)
    return {"status": "accepted", "job_id": job_id, "poll": f"/jobs/{job_id}"}


# ── Job tracking ──────────────────────────────────────────────────────────────

@app.get("/jobs/{job_id}", tags=["Jobs"])
def get_job(job_id: str):
    """Poll the status and result of a background crew job."""
    jobs = _load_jobs()
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return jobs[job_id]


@app.get("/jobs", tags=["Jobs"])
def list_jobs(limit: int = Query(20, ge=1, le=100)):
    """List recent background jobs (most recent first)."""
    jobs = _load_jobs()
    sorted_jobs = sorted(jobs.items(), key=lambda x: x[1].get("started_at", ""), reverse=True)
    return [{"job_id": jid, **info} for jid, info in sorted_jobs[:limit]]


# ── Output file retrieval ─────────────────────────────────────────────────────

@app.get("/outputs/{report}", tags=["Outputs"])
def get_output(report: str):
    """
    Retrieve a generated report as raw text.
    Valid values: fire, tax, health, feed
    """
    if report not in OUTPUT_FILES:
        raise HTTPException(status_code=400, detail=f"Unknown report '{report}'. Valid: {list(OUTPUT_FILES.keys())}")
    path = OUTPUT_FILES[report]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Report '{report}' has not been generated yet.")
    return {"report": report, "content": path.read_text(encoding="utf-8")}


@app.get("/outputs/{report}/download", tags=["Outputs"])
def download_output(report: str):
    """Download a generated report file directly."""
    if report not in OUTPUT_FILES:
        raise HTTPException(status_code=400, detail=f"Unknown report '{report}'.")
    path = OUTPUT_FILES[report]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Report '{report}' has not been generated yet.")
    return FileResponse(path=str(path), filename=path.name, media_type="text/markdown")
