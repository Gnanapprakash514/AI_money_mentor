import json
import os
import re
import time
from datetime import datetime

from .crew import FIRECrew, FeedCrew, HealthCrew, TaxCrew

PROFILE_PATH = "outputs/financial_profile.json"
DEMO_MODE = False
_DEMO_ANSWERS = iter(
    [
        "Rahul",
        "28",
        "Bengaluru",
        "salaried",
        "single",
        "2",
        "80000",
        "0",
        "100000",
        "25000",
        "15000",
        "50000",
        "250000",
        "100000",
        "180000",
        "5000",
        "40000",
        "120000",
        "0",
        "20000",
        "80000",
        "0",
        "1200000",
        "0",
        "0",
        "0",
        "0",
        "12000",
        "Buy flat in 5 years",
        "1500000",
        str(datetime.now().year + 5),
        "50",
        "yes",
        "moderate",
        "intermediate",
        "3",
        "no",
        "yes 500000",
    ]
)


def _to_float(text: str, default: float = 0.0) -> float:
    t = text.lower().replace(",", "").strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(k|lakh|lac|cr|crore)?", t)
    if not match:
        return default
    value = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        return value * 1_000
    if suffix in {"lakh", "lac"}:
        return value * 100_000
    if suffix in {"cr", "crore"}:
        return value * 10_000_000
    return value


def _to_int(text: str, default: int = 0) -> int:
    m = re.search(r"\b([1-9]\d?)\b", text)
    return int(m.group(1)) if m else default


def _yes(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in ["yes", "y", "have", "covered", "done"])


def _ask(prompt: str) -> str:
    print(f"\nAgent: {prompt}")
    if DEMO_MODE:
        answer = next(_DEMO_ANSWERS, "0")
        print(f"You: {answer}")
        return answer.strip()
    try:
        return input("You: ").strip()
    except EOFError:
        print("You: [no stdin detected -> switching to demo answers]")
        return next(_DEMO_ANSWERS, "0").strip()


def _kickoff_with_retry(label: str, fn, inputs: dict, retries: int = 6) -> None:
    attempt = 0
    while True:
        attempt += 1
        try:
            fn().crew().kickoff(inputs=inputs)
            return
        except Exception as exc:
            msg = str(exc).lower()
            transient = any(k in msg for k in ["rate limit", "429", "timeout", "ssl", "connection", "eof"])
            if attempt >= retries or not transient:
                raise
            wait_s = min(60, 10 * attempt)
            print(f"Agent: {label} hit transient API issue. Retrying in {wait_s}s (attempt {attempt}/{retries})...")
            time.sleep(wait_s)


def _build_profile() -> dict:
    print("\n" + "=" * 70)
    print(" AI Money Mentor - Conversational Onboarding (Terminal)")
    print(" " + datetime.now().strftime("%d %b %Y, %I:%M %p"))
    print("=" * 70)

    profile = {
        "personal": {},
        "income": {},
        "expenses": {},
        "assets": {},
        "liabilities": {},
        "insurance": {},
        "derived": {},
        "goals": [],
        "retirement_age_target": 50,
        "fire_interest": True,
        "risk_profile": {},
        "data_quality": {"completeness_percent": 100, "missing_fields": [], "estimated_fields": []},
    }

    name = _ask("Hey! I am your AI Money Mentor. What is your full name?")
    profile["personal"]["name"] = name or "User"

    age_raw = _ask(f"Nice to meet you, {profile['personal']['name']}! How old are you?")
    age = _to_int(age_raw, 30)
    profile["personal"]["age"] = age

    city = _ask("Which city do you live in?")
    profile["personal"]["city"] = city or "Unknown"

    emp = _ask("Are you salaried, self-employed, or business owner?")
    emp_l = emp.lower()
    if "self" in emp_l:
        employment = "self_employed"
    elif "business" in emp_l:
        employment = "business"
    else:
        employment = "salaried"
    profile["personal"]["employment_type"] = employment

    ms = _ask("What is your marital status? (single/married/other)")
    profile["personal"]["marital_status"] = ms or "single"

    deps = _ask("How many dependents do you have?")
    profile["personal"]["dependents"] = _to_int(deps, 0)

    income = _ask("What is your monthly take-home income?")
    monthly_take_home = _to_float(income, 0)
    profile["income"]["monthly_take_home"] = monthly_take_home

    other_income = _ask("Any other monthly income (freelance/rent/dividend)? If none, type 0.")
    profile["income"]["other_monthly_income"] = _to_float(other_income, 0)

    bonus = _ask("Any annual bonus/variable pay? If none, type 0.")
    profile["income"]["annual_bonus"] = _to_float(bonus, 0)
    profile["income"]["monthly_gross"] = monthly_take_home + profile["income"]["other_monthly_income"]

    fixed_exp = _ask("What are your monthly fixed expenses (rent/EMI/fees/premiums)?")
    variable_exp = _ask("What are your monthly variable expenses (food/travel/shopping/etc)?")
    annual_one = _ask("Any large annual one-time expenses? If none, type 0.")
    profile["expenses"]["monthly_fixed"] = _to_float(fixed_exp, 0)
    profile["expenses"]["monthly_variable"] = _to_float(variable_exp, 0)
    profile["expenses"]["annual_one_time"] = _to_float(annual_one, 0)
    profile["expenses"]["monthly_total"] = profile["expenses"]["monthly_fixed"] + profile["expenses"]["monthly_variable"]

    savings = _ask("Current savings + current account balance?")
    fd = _ask("Total Fixed Deposits value?")
    mf = _ask("Current mutual funds value?")
    sip = _ask("Current monthly SIP amount?")
    ppf = _ask("Current PPF corpus?")
    epf = _ask("Current EPF corpus?")
    nps = _ask("Current NPS corpus?")
    stocks = _ask("Current direct stocks value?")
    gold = _ask("Current gold value?")
    re = _ask("Current real estate value? If none, type 0.")

    profile["assets"]["savings_account"] = _to_float(savings, 0)
    profile["assets"]["fixed_deposits"] = _to_float(fd, 0)
    profile["assets"]["mutual_funds_value"] = _to_float(mf, 0)
    profile["assets"]["monthly_sip"] = _to_float(sip, 0)
    profile["assets"]["ppf"] = _to_float(ppf, 0)
    profile["assets"]["epf"] = _to_float(epf, 0)
    profile["assets"]["nps"] = _to_float(nps, 0)
    profile["assets"]["stocks"] = _to_float(stocks, 0)
    profile["assets"]["gold_value"] = _to_float(gold, 0)
    profile["assets"]["real_estate"] = _to_float(re, 0)
    profile["assets"]["total_assets"] = (
        profile["assets"]["savings_account"]
        + profile["assets"]["fixed_deposits"]
        + profile["assets"]["mutual_funds_value"]
        + profile["assets"]["ppf"]
        + profile["assets"]["epf"]
        + profile["assets"]["nps"]
        + profile["assets"]["stocks"]
        + profile["assets"]["gold_value"]
        + profile["assets"]["real_estate"]
    )

    hl = _ask("Home loan outstanding principal? If none, type 0.")
    car = _ask("Car loan outstanding principal? If none, type 0.")
    pl = _ask("Personal loan outstanding principal? If none, type 0.")
    el = _ask("Education loan outstanding principal? If none, type 0.")
    cc = _ask("Credit card outstanding dues? If none, type 0.")
    emi = _ask("Total monthly EMI across all loans?")

    profile["liabilities"]["home_loan"] = _to_float(hl, 0)
    profile["liabilities"]["car_loan"] = _to_float(car, 0)
    profile["liabilities"]["personal_loan"] = _to_float(pl, 0)
    profile["liabilities"]["education_loan"] = _to_float(el, 0)
    profile["liabilities"]["credit_card_dues"] = _to_float(cc, 0)
    profile["liabilities"]["monthly_emi_total"] = _to_float(emi, 0)
    profile["liabilities"]["total_debt"] = (
        profile["liabilities"]["home_loan"]
        + profile["liabilities"]["car_loan"]
        + profile["liabilities"]["personal_loan"]
        + profile["liabilities"]["education_loan"]
        + profile["liabilities"]["credit_card_dues"]
    )

    goal1 = _ask("Tell me your top goal (example: Buy a flat in 5 years).")
    goal1_amt = _ask("Target amount needed for this goal?")
    goal1_year = _ask("Target year for this goal?")
    profile["goals"].append(
        {
            "name": goal1 or "Primary goal",
            "target_amount": _to_float(goal1_amt, 0),
            "target_year": _to_int(goal1_year, datetime.now().year + 5),
            "years_remaining": max(_to_int(goal1_year, datetime.now().year + 5) - datetime.now().year, 1),
        }
    )

    fire_age = _ask("At what age do you want to retire?")
    profile["retirement_age_target"] = _to_int(fire_age, 50)
    fire_interest = _ask("Are you interested in FIRE (retire early)? yes/no")
    profile["fire_interest"] = _yes(fire_interest)

    risk = _ask("Risk tolerance: conservative/moderate/aggressive?")
    exp = _ask("Investment experience: beginner/intermediate/experienced?")
    ef = _ask("How many months of emergency fund do you currently have?")
    profile["risk_profile"]["tolerance"] = (risk or "moderate").lower()
    profile["risk_profile"]["experience"] = (exp or "beginner").lower()
    profile["risk_profile"]["emergency_fund_months"] = _to_float(ef, 0)

    life = _ask("Do you have life insurance? If yes, how much cover?")
    life_cover = _to_float(life, 0) if _yes(life) else 0
    health = _ask("Do you have health insurance? If yes, how much cover?")
    health_cover = _to_float(health, 0) if _yes(health) else 0
    profile["insurance"]["life_cover"] = life_cover
    profile["insurance"]["life_type"] = "term" if life_cover > 0 else "none"
    profile["insurance"]["health_cover"] = health_cover
    profile["insurance"]["health_type"] = "family_floater" if health_cover > 0 else "none"

    profile["derived"]["net_worth"] = profile["assets"]["total_assets"] - profile["liabilities"]["total_debt"]
    profile["derived"]["monthly_surplus"] = (
        profile["income"]["monthly_take_home"]
        + profile["income"]["other_monthly_income"]
        - profile["expenses"]["monthly_total"]
        - profile["liabilities"]["monthly_emi_total"]
    )
    if profile["income"]["monthly_take_home"] > 0:
        profile["derived"]["savings_rate_percent"] = (
            profile["derived"]["monthly_surplus"] / profile["income"]["monthly_take_home"] * 100
        )
        profile["derived"]["emi_to_income_ratio"] = (
            profile["liabilities"]["monthly_emi_total"] / profile["income"]["monthly_take_home"] * 100
        )
    else:
        profile["derived"]["savings_rate_percent"] = 0
        profile["derived"]["emi_to_income_ratio"] = 0
    if profile["assets"]["total_assets"] > 0:
        profile["derived"]["debt_to_asset_ratio"] = round(
            profile["liabilities"]["total_debt"] / profile["assets"]["total_assets"], 2
        )
    else:
        profile["derived"]["debt_to_asset_ratio"] = 0

    return profile


def run_terminal_e2e(demo_mode: bool = False) -> None:
    global DEMO_MODE
    DEMO_MODE = demo_mode
    os.makedirs("outputs", exist_ok=True)
    profile = _build_profile()
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print("\nAgent: Great, your profile is built and saved.")
    print(f"Saved: {PROFILE_PATH}")

    profile_str = json.dumps(profile)

    print("\nRunning FIRE crew...")
    _kickoff_with_retry("FIRE crew", FIRECrew, {"profile": profile_str})
    print("Saved: outputs/fire_roadmap.md")
    time.sleep(2)

    print("\nRunning Tax crew...")
    _kickoff_with_retry("Tax crew", TaxCrew, {"profile": profile_str})
    print("Saved: outputs/tax_analysis.md")
    time.sleep(2)

    print("\nRunning Health Score crew...")
    _kickoff_with_retry("Health crew", HealthCrew, {"profile": profile_str})
    print("Saved: outputs/health_score.md")
    time.sleep(2)

    print("\nRunning Daily Feed crew...")
    _kickoff_with_retry("Feed crew", FeedCrew, {"profile": profile_str})
    print("Saved: outputs/daily_feed.md")

    print("\nDone: end-to-end terminal flow complete.")
