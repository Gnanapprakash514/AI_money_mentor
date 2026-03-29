from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import json
import os
import re
from datetime import datetime

from .crew import FIRECrew, TaxCrew, HealthCrew, FeedCrew

app = FastAPI(title="AI Money Mentor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProfileInput(BaseModel):
    profile: Dict[str, Any]


PROFILE_PATH = "outputs/financial_profile.json"

ONBOARDING_FIELDS = [
    "name",
    "age",
    "city",
    "employment_type_raw",
    "marital_status",
    "dependents",
    "monthly_take_home",
    "other_monthly_income",
    "annual_bonus",
    "monthly_fixed",
    "monthly_variable",
    "annual_one_time",
    "savings_account",
    "fixed_deposits",
    "mutual_funds_value",
    "monthly_sip",
    "ppf",
    "epf",
    "nps",
    "stocks",
    "gold_value",
    "real_estate",
    "home_loan",
    "car_loan",
    "personal_loan",
    "education_loan",
    "credit_card_dues",
    "monthly_emi_total",
    "goal_name",
    "goal_target_amount",
    "goal_target_year",
    "retirement_age_target",
    "fire_interest_raw",
    "risk_tolerance",
    "risk_experience",
    "emergency_fund_months",
    "life_cover_raw",
    "health_cover_raw",
]


def _next_question(answers: Dict[str, Any], index: int) -> str:
    questions = [
        "Hey! I am your AI Money Mentor. What is your full name?",
        f"Nice to meet you, {answers.get('name', 'there')}! How old are you?",
        "Which city do you live in?",
        "Are you salaried, self-employed, or business owner?",
        "What is your marital status? (single/married/other)",
        "How many dependents do you have?",
        "What is your monthly take-home income?",
        "Any other monthly income (freelance/rent/dividend)? If none, type 0.",
        "Any annual bonus/variable pay? If none, type 0.",
        "What are your monthly fixed expenses (rent/EMI/fees/premiums)?",
        "What are your monthly variable expenses (food/travel/shopping/etc)?",
        "Any large annual one-time expenses? If none, type 0.",
        "Current savings + current account balance?",
        "Total Fixed Deposits value?",
        "Current mutual funds value?",
        "Current monthly SIP amount?",
        "Current PPF corpus?",
        "Current EPF corpus?",
        "Current NPS corpus?",
        "Current direct stocks value?",
        "Current gold value?",
        "Current real estate value? If none, type 0.",
        "Home loan outstanding principal? If none, type 0.",
        "Car loan outstanding principal? If none, type 0.",
        "Personal loan outstanding principal? If none, type 0.",
        "Education loan outstanding principal? If none, type 0.",
        "Credit card outstanding dues? If none, type 0.",
        "Total monthly EMI across all loans?",
        "Tell me your top goal (example: Buy a flat in 5 years).",
        "Target amount needed for this goal?",
        "Target year for this goal?",
        "At what age do you want to retire?",
        "Are you interested in FIRE (retire early)? yes/no",
        "Risk tolerance: conservative/moderate/aggressive?",
        "Investment experience: beginner/intermediate/experienced?",
        "How many months of emergency fund do you currently have?",
        "Do you have life insurance? If yes, how much cover?",
        "Do you have health insurance? If yes, how much cover?",
    ]
    return questions[index]


def _result_text(result: Any) -> str:
    return str(result.raw if hasattr(result, "raw") else str(result))


def _to_int(value: Any, default: int = 0) -> int:
    try:
        m = re.search(r"-?\d+", str(value).replace(",", ""))
        return int(m.group(0)) if m else default
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        t = str(value).lower().replace(",", "").strip()
        match = re.search(r"(\d+(?:\.\d+)?)\s*(k|lakh|lac|cr|crore)?", t)
        if not match:
            return default
        amount = float(match.group(1))
        suffix = match.group(2)
        if suffix == "k":
            return amount * 1_000
        if suffix in {"lakh", "lac"}:
            return amount * 100_000
        if suffix in {"cr", "crore"}:
            return amount * 10_000_000
        return amount
    except Exception:
        return default


def _yes(value: Any) -> bool:
    t = str(value).lower()
    return any(k in t for k in ["yes", "y", "have", "covered", "done"])


def _build_profile_from_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    employment_raw = str(answers.get("employment_type_raw", "salaried")).lower()
    if "self" in employment_raw:
        employment_type = "self_employed"
    elif "business" in employment_raw:
        employment_type = "business"
    else:
        employment_type = "salaried"

    monthly_take_home = _to_float(answers.get("monthly_take_home"), 0.0)
    other_monthly_income = _to_float(answers.get("other_monthly_income"), 0.0)

    monthly_fixed = _to_float(answers.get("monthly_fixed"), 0.0)
    monthly_variable = _to_float(answers.get("monthly_variable"), 0.0)
    monthly_total = monthly_fixed + monthly_variable

    assets = {
        "savings_account": _to_float(answers.get("savings_account"), 0.0),
        "fixed_deposits": _to_float(answers.get("fixed_deposits"), 0.0),
        "mutual_funds_value": _to_float(answers.get("mutual_funds_value"), 0.0),
        "monthly_sip": _to_float(answers.get("monthly_sip"), 0.0),
        "ppf": _to_float(answers.get("ppf"), 0.0),
        "epf": _to_float(answers.get("epf"), 0.0),
        "nps": _to_float(answers.get("nps"), 0.0),
        "stocks": _to_float(answers.get("stocks"), 0.0),
        "gold_value": _to_float(answers.get("gold_value"), 0.0),
        "real_estate": _to_float(answers.get("real_estate"), 0.0),
    }
    total_assets = (
        assets["savings_account"]
        + assets["fixed_deposits"]
        + assets["mutual_funds_value"]
        + assets["ppf"]
        + assets["epf"]
        + assets["nps"]
        + assets["stocks"]
        + assets["gold_value"]
        + assets["real_estate"]
    )
    assets["total_assets"] = total_assets

    liabilities = {
        "home_loan": _to_float(answers.get("home_loan"), 0.0),
        "car_loan": _to_float(answers.get("car_loan"), 0.0),
        "personal_loan": _to_float(answers.get("personal_loan"), 0.0),
        "education_loan": _to_float(answers.get("education_loan"), 0.0),
        "credit_card_dues": _to_float(answers.get("credit_card_dues"), 0.0),
        "monthly_emi_total": _to_float(answers.get("monthly_emi_total"), 0.0),
    }
    total_debt = (
        liabilities["home_loan"]
        + liabilities["car_loan"]
        + liabilities["personal_loan"]
        + liabilities["education_loan"]
        + liabilities["credit_card_dues"]
    )
    liabilities["total_debt"] = total_debt

    life_cover_raw = answers.get("life_cover_raw", "")
    health_cover_raw = answers.get("health_cover_raw", "")
    life_cover = _to_float(life_cover_raw, 0) if _yes(life_cover_raw) else 0
    health_cover = _to_float(health_cover_raw, 0) if _yes(health_cover_raw) else 0

    monthly_surplus = monthly_take_home + other_monthly_income - monthly_total - liabilities["monthly_emi_total"]
    savings_rate = (monthly_surplus / monthly_take_home * 100) if monthly_take_home > 0 else 0

    goal_year = _to_int(answers.get("goal_target_year"), datetime.now().year + 5)
    retirement_age = _to_int(answers.get("retirement_age_target"), 50)

    return {
        "personal": {
            "name": answers.get("name", "User"),
            "age": _to_int(answers.get("age"), 30),
            "city": answers.get("city", "Unknown"),
            "employment_type": employment_type,
            "marital_status": str(answers.get("marital_status", "single")).lower(),
            "dependents": _to_int(answers.get("dependents"), 0),
        },
        "income": {
            "monthly_take_home": monthly_take_home,
            "other_monthly_income": other_monthly_income,
            "annual_bonus": _to_float(answers.get("annual_bonus"), 0.0),
            "monthly_gross": monthly_take_home + other_monthly_income,
        },
        "expenses": {
            "monthly_fixed": monthly_fixed,
            "monthly_variable": monthly_variable,
            "annual_one_time": _to_float(answers.get("annual_one_time"), 0.0),
            "monthly_total": monthly_total,
        },
        "assets": assets,
        "liabilities": liabilities,
        "insurance": {
            "life_cover": life_cover,
            "life_type": "term" if life_cover > 0 else "none",
            "health_cover": health_cover,
            "health_type": "family_floater" if health_cover > 0 else "none",
        },
        "derived": {
            "net_worth": total_assets - total_debt,
            "monthly_surplus": monthly_surplus,
            "savings_rate_percent": round(savings_rate, 2),
            "emi_to_income_ratio": round((liabilities["monthly_emi_total"] / monthly_take_home * 100), 2) if monthly_take_home > 0 else 0,
            "debt_to_asset_ratio": round(total_debt / total_assets, 2) if total_assets > 0 else 0,
        },
        "goals": [
            {
                "name": answers.get("goal_name", "Primary goal"),
                "target_amount": _to_float(answers.get("goal_target_amount"), 0.0),
                "target_year": goal_year,
                "years_remaining": max(goal_year - datetime.now().year, 1),
            }
        ],
        "retirement_age_target": retirement_age,
        "fire_interest": _yes(answers.get("fire_interest_raw", "yes")),
        "risk_profile": {
            "tolerance": str(answers.get("risk_tolerance", "moderate")).lower(),
            "experience": str(answers.get("risk_experience", "beginner")).lower(),
            "emergency_fund_months": _to_float(answers.get("emergency_fund_months"), 0.0),
        },
        "data_quality": {
            "completeness_percent": 100,
            "missing_fields": [],
            "estimated_fields": [],
        },
    }


def _persist_profile(profile: Dict[str, Any]) -> None:
    os.makedirs("outputs", exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def _load_profile() -> Dict[str, Any]:
    if not os.path.exists(PROFILE_PATH):
        return {}
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback: tolerate markdown-fenced JSON written by earlier flows.
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if text.startswith("```"):
                lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
                cleaned = "\n".join(lines).strip()
                return json.loads(cleaned)
        except Exception:
            return {}
    return {}


def _resolve_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    saved = _load_profile()
    base = saved if isinstance(saved, dict) else {}
    incoming = profile if isinstance(profile, dict) else {}

    if not base:
        return incoming
    if not incoming:
        return base

    def _deep_merge(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(left)
        for key, value in right.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    return _deep_merge(base, incoming)


def _safe_kickoff(crew_class, inputs: dict):
    try:
        result = crew_class().crew().kickoff(inputs=inputs)
        return {"success": True, "output": _result_text(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/onboarding")
def run_onboarding(data: ProfileInput):
    profile_payload = data.profile or {}
    history = profile_payload.get("history", [])
    user_answers = [
        item.get("text", "") for item in history
        if isinstance(item, dict) and item.get("type") == "user"
    ]

    if not user_answers:
        return {
            "success": True,
            "done": False,
            "progress": 0,
            "reply": _next_question({}, 0),
        }

    mapped_answers: Dict[str, Any] = {}
    for idx, answer in enumerate(user_answers[: len(ONBOARDING_FIELDS)]):
        mapped_answers[ONBOARDING_FIELDS[idx]] = answer

    next_index = len(user_answers)
    if next_index < len(ONBOARDING_FIELDS):
        progress = int((next_index / len(ONBOARDING_FIELDS)) * 100)
        return {
            "success": True,
            "done": False,
            "progress": progress,
            "reply": _next_question(mapped_answers, next_index),
        }

    built_profile = _build_profile_from_answers(mapped_answers)
    _persist_profile(built_profile)

    return {
        "success": True,
        "done": True,
        "progress": 100,
        "reply": "Perfect. Your financial profile is ready. I can now generate FIRE, Tax, Health, and Feed insights using this profile.",
        "profile": built_profile,
    }


@app.get("/api/profile")
def get_profile():
    profile = _load_profile()
    if profile:
        return {"success": True, "profile": profile}
    return {"success": False, "error": "No saved profile found. Please complete onboarding."}

@app.post("/api/fire")
def run_fire(data: ProfileInput):
    profile = _resolve_profile(data.profile)
    profile_str = json.dumps(profile)
    # Replicating e2e_terminal logic
    try:
        years_to_retire = max(1, profile.get("retirement_age_target", 50) - profile.get("personal", {}).get("age", 30))
        target_income = profile.get("expenses", {}).get("monthly_total", 50000)
    except:
        years_to_retire = 20
        target_income = 50000

    return _safe_kickoff(FIRECrew, {
        "profile": profile_str,
        "years": years_to_retire,
        "target_income": target_income,
        "inflation": 6.0
    })

@app.post("/api/tax")
def run_tax(data: ProfileInput):
    profile = _resolve_profile(data.profile)
    profile_str = json.dumps(profile)
    try:
        deductions = profile.get("assets", {}).get("ppf", 0) + profile.get("assets", {}).get("epf", 0)
    except:
        deductions = 0

    return _safe_kickoff(TaxCrew, {
        "profile": profile_str,
        "regime": "new",
        "deductions": deductions
    })

@app.post("/api/health")
def run_health(data: ProfileInput):
    profile = _resolve_profile(data.profile)
    profile_str = json.dumps(profile)
    try:
        emergency_fund = profile.get("risk_profile", {}).get("emergency_fund_months", 3) * profile.get("expenses", {}).get("monthly_total", 50000)
        savings_rate = profile.get("derived", {}).get("savings_rate_percent", 0)
    except:
        emergency_fund = 150000
        savings_rate = 20
    # Lightweight backend score so the frontend gauge can render real API data.
    emergency_months = profile.get("risk_profile", {}).get("emergency_fund_months", 3)
    score = 40
    score += min(25, max(0, int(savings_rate * 0.8)))
    score += min(20, max(0, int(emergency_months * 3)))
    score += 15 if profile.get("liabilities", {}).get("credit_card_dues", 0) == 0 else 5
    score = max(0, min(100, score))

    try:
        result = HealthCrew().crew().kickoff(inputs={
            "profile": profile_str,
            "emergency_fund": emergency_fund,
            "savings_rate": savings_rate
        })
        return {"success": True, "score": score, "output": _result_text(result)}
    except Exception as e:
        return {"success": False, "score": score, "error": str(e)}

@app.post("/api/feed")
def run_feed(data: ProfileInput):
    profile = _resolve_profile(data.profile)
    profile_str = json.dumps(profile)
    return _safe_kickoff(FeedCrew, {"profile": profile_str})


@app.post("/api/couple")
def run_couple(data: ProfileInput):
    profile = _resolve_profile(data.profile)

    partner1_income = profile.get("partner1_income", 0)
    partner2_income = profile.get("partner2_income", 0)
    combined_income = partner1_income + partner2_income

    goals = profile.get("goals", [])
    goals_text = ", ".join(goals) if isinstance(goals, list) and goals else "House"

    output = (
        "# Joint Financial Blueprint\n"
        f"Combined monthly income considered: Rs {combined_income:,.0f}.\n\n"
        "## Immediate Actions\n"
        "1. Build a shared emergency fund account with 6 months of joint expenses.\n"
        "2. Automate two SIPs: one for long-term wealth and one for short-term goals.\n"
        "3. Review insurance cover jointly and remove overlap in policies.\n\n"
        "## Shared Goals\n"
        f"Prioritized goals: {goals_text}.\n"
        "Use a monthly money meeting to track progress and rebalance contributions."
    )

    return {"success": True, "output": output}

# Ensure the frontend directory exists
os.makedirs("frontend", exist_ok=True)

# Mount the frontend directory to serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")
