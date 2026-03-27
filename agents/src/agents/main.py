#!/usr/bin/env python
# =============================================================================
# main.py — AI Money Mentor entry point
# Routes to all 5 crews: Onboarding, FIRE, Tax, Health, Feed
# =============================================================================

import sys
import json
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Ensure Windows terminals handle Unicode from CrewAI logs/tools (₹, emoji, arrows).
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


def detect_intent(user_text: str) -> str:
    text = user_text.lower()
    if any(k in text for k in ["onboard", "start", "new user", "profile setup"]):
        return "onboarding"
    if any(k in text for k in ["retire", "fire", "sip", "corpus"]):
        return "fire"
    if any(k in text for k in ["tax", "80c", "deduction", "regime"]):
        return "tax"
    if any(k in text for k in ["health score", "money health", "financial health"]):
        return "health"
    if any(k in text for k in ["daily", "feed", "market update", "today update"]):
        return "feed"
    return "onboarding"


def route_intent(intent: str):
    mapping = {
        "onboarding": run_onboarding,
        "fire": run_fire,
        "tax": run_tax,
        "health": run_health,
        "feed": run_feed,
    }
    return mapping[intent]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_profile() -> str:
    """Load the financial profile JSON. Raises if not found."""
    if not os.path.exists(PROFILE_PATH):
        raise FileNotFoundError(
            f"No profile found at '{PROFILE_PATH}'.\n"
            "Run onboarding first:  python main.py onboarding"
        )
    with open(PROFILE_PATH, "r") as f:
        return f.read()


def _ensure_outputs_dir():
    """Create the outputs/ directory if it doesn't exist."""
    os.makedirs("outputs", exist_ok=True)


def _banner(crew_name: str):
    print(f"\n{'='*60}")
    print(f"  AI Money Mentor — {crew_name}")
    print(f"  {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    print(f"{'='*60}\n")


# ── Crew runners ─────────────────────────────────────────────────────────────

def run_onboarding():
    """
    Run the Onboarding crew.
    Interviews the user and saves a financial profile to outputs/.
    """
    _banner("Onboarding")
    _ensure_outputs_dir()
    try:
        result = OnboardingCrew().crew().kickoff()
        print("\n✅ Onboarding complete. Profile saved to outputs/financial_profile.json")
        print("\nNext steps:")
        print("  python main.py fire     — FIRE retirement plan")
        print("  python main.py tax      — Tax analysis")
        print("  python main.py health   — Health score")
        print("  python main.py feed     — Today's personalised feed")
        return result
    except Exception as e:
        raise Exception(f"Onboarding crew failed: {e}")


def run_fire():
    """
    Run the FIRE Planner crew.
    Requires outputs/financial_profile.json from onboarding.
    """
    _banner("FIRE Planner")
    _ensure_outputs_dir()
    profile = _load_profile()
    try:
        result = FIRECrew().crew().kickoff(inputs={"profile": profile})
        print("\n✅ FIRE plan saved to outputs/fire_roadmap.md")
        return result
    except Exception as e:
        raise Exception(f"FIRE crew failed: {e}")


def run_tax():
    """
    Run the Tax Wizard crew.
    Requires outputs/financial_profile.json from onboarding.
    """
    _banner("Tax Wizard")
    _ensure_outputs_dir()
    profile = _load_profile()
    try:
        result = TaxCrew().crew().kickoff(inputs={"profile": profile})
        print("\n✅ Tax analysis saved to outputs/tax_analysis.md")
        return result
    except Exception as e:
        raise Exception(f"Tax crew failed: {e}")


def run_health():
    """
    Run the Health Score crew.
    Requires outputs/financial_profile.json from onboarding.
    """
    _banner("Health Score")
    _ensure_outputs_dir()
    profile = _load_profile()
    try:
        result = HealthCrew().crew().kickoff(inputs={"profile": profile})
        print("\n✅ Health score saved to outputs/health_score.md")
        return result
    except Exception as e:
        raise Exception(f"Health crew failed: {e}")


def run_feed():
    """
    Run the Daily Feed crew.
    Requires outputs/financial_profile.json from onboarding.
    """
    _banner("Daily Feed")
    _ensure_outputs_dir()
    profile = _load_profile()
    try:
        result = FeedCrew().crew().kickoff(inputs={"profile": profile})
        print("\n✅ Daily feed saved to outputs/daily_feed.md")
        return result
    except Exception as e:
        raise Exception(f"Feed crew failed: {e}")


def run_all():
    """
    Run all crews in sequence: Onboarding → FIRE → Tax → Health → Feed.
    Useful for a full end-to-end demo.
    """
    _banner("Full Run — All Crews")
    _ensure_outputs_dir()

    print("Step 1/5 — Onboarding")
    run_onboarding()

    profile = _load_profile()

    print("\nStep 2/5 — FIRE Planner")
    FIRECrew().crew().kickoff(inputs={"profile": profile})

    print("\nStep 3/5 — Tax Wizard")
    TaxCrew().crew().kickoff(inputs={"profile": profile})

    print("\nStep 4/5 — Health Score")
    HealthCrew().crew().kickoff(inputs={"profile": profile})

    print("\nStep 5/5 — Daily Feed")
    FeedCrew().crew().kickoff(inputs={"profile": profile})

    print("\n✅ All crews complete. Check the outputs/ folder:")
    for f in [
        "financial_profile.json",
        "fire_roadmap.md",
        "tax_analysis.md",
        "health_score.md",
        "daily_feed.md",
    ]:
        path = f"outputs/{f}"
        status = "✅" if os.path.exists(path) else "❌"
        print(f"  {status} {path}")


# ── pyproject.toml script entry points ───────────────────────────────────────
# These map to the [project.scripts] entries in pyproject.toml

def run():
    """Default run — shows crew menu if no arg, else routes to crew."""
    crews = {
        "onboarding": run_onboarding,
        "fire":       run_fire,
        "tax":        run_tax,
        "health":     run_health,
        "feed":       run_feed,
        "all":        run_all,
        "route":      None,
        "e2e":        run_terminal_e2e,
    }

    # If called via pyproject script with no args, show menu
    if len(sys.argv) < 2:
        print("\n🤖 AI Money Mentor — CrewAI Backend\n")
        print("Usage:  python main.py <crew>\n")
        print("Available crews:")
        print("  onboarding  — Interview user and build financial profile")
        print("  fire        — FIRE retirement plan and SIP allocation")
        print("  tax         — Tax analysis and regime comparison")
        print("  health      — 6-dimension health score and 90-day plan")
        print("  feed        — Today's personalised market feed")
        print("  all         — Run all crews end to end")
        print("  route       — Detect intent and route to a crew\n")
        print("  e2e         — Full conversational onboarding + all crews\n")
        print("Example:")
        print("  python main.py onboarding")
        print('  python main.py route "need help with 80C tax saving"')
        print("  python main.py e2e")
        return

    crew_name = sys.argv[1].lower()
    if crew_name not in crews:
        print(f"\n❌ Unknown crew: '{crew_name}'")
        print(f"Available: {', '.join(crews.keys())}")
        sys.exit(1)
    if crew_name == "route":
        if len(sys.argv) < 3:
            print('Usage: python main.py route "<user request text>"')
            sys.exit(1)
        intent = detect_intent(" ".join(sys.argv[2:]))
        print(f"🧭 Detected intent: {intent}")
        route_intent(intent)()
        return
    if crew_name == "e2e":
        run_terminal_e2e(demo_mode="--demo" in sys.argv)
        return
    crews[crew_name]()


def train():
    """Train a crew for a given number of iterations."""
    if len(sys.argv) < 4:
        print("Usage: train <crew> <n_iterations> <output_filename>")
        sys.exit(1)

    crew_name   = sys.argv[1].lower()
    n_iter      = int(sys.argv[2])
    output_file = sys.argv[3]

    crew_map = {
        "onboarding": OnboardingCrew,
        "fire":       FIRECrew,
        "tax":        TaxCrew,
        "health":     HealthCrew,
        "feed":       FeedCrew,
    }

    if crew_name not in crew_map:
        print(f"Unknown crew: {crew_name}. Available: {', '.join(crew_map.keys())}")
        sys.exit(1)

    profile_str = _load_profile() if crew_name != "onboarding" else "{}"
    inputs = {} if crew_name == "onboarding" else {"profile": profile_str}

    try:
        crew_map[crew_name]().crew().train(
            n_iterations=n_iter,
            filename=output_file,
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"Training failed: {e}")


def replay():
    """Replay a crew execution from a specific task ID."""
    if len(sys.argv) < 2:
        print("Usage: replay <task_id>")
        sys.exit(1)
    try:
        # Replay uses last run's crew — default to onboarding
        OnboardingCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Replay failed: {e}")


def test():
    """Test crew execution and return results."""
    if len(sys.argv) < 4:
        print("Usage: test <crew> <n_iterations> <eval_llm>")
        sys.exit(1)

    crew_name = sys.argv[1].lower()
    n_iter    = int(sys.argv[2])
    eval_llm  = sys.argv[3]

    crew_map = {
        "onboarding": OnboardingCrew,
        "fire":       FIRECrew,
        "tax":        TaxCrew,
        "health":     HealthCrew,
        "feed":       FeedCrew,
    }

    if crew_name not in crew_map:
        print(f"Unknown crew: {crew_name}. Available: {', '.join(crew_map.keys())}")
        sys.exit(1)

    profile_str = _load_profile() if crew_name != "onboarding" else "{}"
    inputs = {} if crew_name == "onboarding" else {"profile": profile_str}

    try:
        crew_map[crew_name]().crew().test(
            n_iterations=n_iter,
            eval_llm=eval_llm,
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"Test failed: {e}")


def run_with_trigger():
    """Run a crew from an external trigger payload (JSON string as CLI arg)."""
    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided.\n"
            'Usage: run_with_trigger \'{"crew": "fire", "profile": "..."}\''
        )
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload.")

    crew_name = payload.get("crew", "onboarding").lower()
    profile   = payload.get("profile", "")

    crew_map = {
        "onboarding": (OnboardingCrew, {}),
        "fire":       (FIRECrew,       {"profile": profile}),
        "tax":        (TaxCrew,        {"profile": profile}),
        "health":     (HealthCrew,     {"profile": profile}),
        "feed":       (FeedCrew,       {"profile": profile}),
    }

    if crew_name not in crew_map:
        raise Exception(f"Unknown crew in payload: '{crew_name}'")

    CrewClass, inputs = crew_map[crew_name]
    try:
        result = CrewClass().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"Trigger run failed: {e}")


# ── Direct execution ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    run()