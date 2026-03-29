#!/usr/bin/env python

import sys
import json
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from .crew import (
    OnboardingCrew,
    FIRECrew,
    TaxCrew,
    HealthCrew,
    FeedCrew,
)
from .e2e_terminal import run_terminal_e2e

PROFILE_PATH = "outputs/financial_profile.json"


# ================= USER INPUT =================

def collect_user_input():
    print("\n=== Enter Your Financial Details ===\n")

    profile = {
        "marital_status": input("Marital Status: "),
        "age": int(input("Age: ")),
        "occupation": input("Occupation: "),
        "annual_income": int(input("Annual Income: ")),

        "monthly_take_home_salary": int(input("Monthly Salary: ")),

        "monthly_expenses": {
            "housing": int(input("Housing expense: ")),
            "groceries": int(input("Groceries: ")),
            "transportation": int(input("Transportation: ")),
            "utilities": int(input("Utilities: ")),
            "entertainment": int(input("Entertainment: ")),
            "savings": int(input("Savings: ")),
            "debt_repayment": int(input("Debt repayment: ")),
            "other": int(input("Other expenses: "))
        },

        "risk_appetite": input("Risk Appetite (Conservative/Moderate/Aggressive): ")
    }

    return profile


# ================= HELPERS =================

def _load_profile():
    if not os.path.exists(PROFILE_PATH):
        raise FileNotFoundError(
            f"No profile found at '{PROFILE_PATH}'. Run onboarding first."
        )
    with open(PROFILE_PATH, "r") as f:
        return f.read()


def _ensure_outputs_dir():
    os.makedirs("outputs", exist_ok=True)


def _banner(crew_name: str):
    print(f"\n{'='*60}")
    print(f"  AI Money Mentor — {crew_name}")
    print(f"  {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    print(f"{'='*60}\n")


# ================= CREWS =================

def run_onboarding():
    _banner("Onboarding")
    _ensure_outputs_dir()

    try:
        user_data = collect_user_input()

        result = OnboardingCrew().crew().kickoff(
            inputs={"user_profile": user_data}
        )

        print("\n✅ Onboarding complete. Profile saved.")
        return result

    except Exception as e:
        raise Exception(f"Onboarding crew failed: {e}")


def run_fire():
    _banner("FIRE Planner")
    _ensure_outputs_dir()

    profile = _load_profile()

    print("\n=== FIRE Planning Inputs ===\n")
    years = int(input("Years to retirement: "))
    target_income = int(input("Target monthly income after retirement: "))
    inflation = float(input("Expected inflation rate (%): "))

    result = FIRECrew().crew().kickoff(
        inputs={
            "profile": profile,
            "years": years,
            "target_income": target_income,
            "inflation": inflation
        }
    )

    print("\n✅ FIRE plan generated.")
    return result


def run_tax():
    _banner("Tax Wizard")
    _ensure_outputs_dir()

    profile = _load_profile()

    print("\n=== Tax Inputs ===\n")
    regime = input("Preferred tax regime (old/new): ")
    deductions = int(input("Total planned deductions (₹): "))

    result = TaxCrew().crew().kickoff(
        inputs={
            "profile": profile,
            "regime": regime,
            "deductions": deductions
        }
    )

    print("\n✅ Tax analysis generated.")
    return result


def run_health():
    _banner("Health Score")
    _ensure_outputs_dir()

    profile = _load_profile()

    print("\n=== Financial Health Inputs ===\n")
    emergency_fund = int(input("Emergency fund available (₹): "))
    savings_rate = float(input("Savings rate (%): "))

    result = HealthCrew().crew().kickoff(
        inputs={
            "profile": profile,
            "emergency_fund": emergency_fund,
            "savings_rate": savings_rate
        }
    )

    print("\n✅ Health score generated.")
    return result


def run_feed():
    _banner("Daily Feed")
    _ensure_outputs_dir()

    profile = _load_profile()

    result = FeedCrew().crew().kickoff(inputs={"profile": profile})
    print("\n✅ Daily feed generated.")
    return result


def run_all():
    _banner("Full Run — All Crews")
    _ensure_outputs_dir()

    print("Step 1/5 — Onboarding")
    run_onboarding()

    profile = _load_profile()

    print("\nStep 2/5 — FIRE Planner")
    run_fire()

    print("\nStep 3/5 — Tax Wizard")
    run_tax()

    print("\nStep 4/5 — Health Score")
    run_health()

    print("\nStep 5/5 — Daily Feed")
    run_feed()

    print("\n✅ All crews complete. Check outputs/")


# ================= MAIN =================

def run():
    crews = {
        "onboarding": run_onboarding,
        "fire": run_fire,
        "tax": run_tax,
        "health": run_health,
        "feed": run_feed,
        "all": run_all,
        "e2e": run_terminal_e2e,
    }

    if len(sys.argv) < 2:
        print("\n🤖 AI Money Mentor\n")
        print("Usage: python main.py <crew>\n")
        print("Available:", ", ".join(crews.keys()))
        return

    crew_name = sys.argv[1].lower()

    if crew_name not in crews:
        print(f"\n❌ Unknown crew: {crew_name}")
        return

    if crew_name == "e2e":
        run_terminal_e2e()
        return

    crews[crew_name]()


if __name__ == "__main__":
    run()