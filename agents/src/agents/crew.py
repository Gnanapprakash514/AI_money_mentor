# =============================================================================
# crew.py — AI Money Mentor | All 5 Crews in one file
# =============================================================================
# CREWS:
#   1. OnboardingCrew   — Interviews user and builds financial profile
#   2. FIRECrew         — FIRE analysis and SIP plan
#   3. TaxCrew          — Tax research and regime comparison
#   4. HealthCrew       — 6-dimension health score and 90-day plan
#   5. FeedCrew         — Daily personalised market feed
#
# USAGE:
#   from crew import OnboardingCrew, FIRECrew, TaxCrew, HealthCrew, FeedCrew
#
#   # Onboarding (no profile needed — it creates one)
#   result = OnboardingCrew().crew().kickoff()
#
#   # All other crews need a profile string
#   profile = open("outputs/financial_profile.json").read()
#   result  = FIRECrew().crew().kickoff(inputs={"profile": profile})
# =============================================================================
import json
import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from .tools.tools import (
    SIPCalculatorTool,
    FIRECalculatorTool,
    MarketDataTool,
    TaxRulesTool,
)

# Instantiate tools once — shared across crews
sip_tool    = SIPCalculatorTool()
fire_tool   = FIRECalculatorTool()
market_tool = MarketDataTool()
tax_tool    = TaxRulesTool()


# =============================================================================
# CREW 1 — ONBOARDING
# Interviews the user and builds a complete JSON financial profile.
# No profile input required. Output: outputs/financial_profile.json
# =============================================================================

@CrewBase
class OnboardingCrew():
    """
    Onboarding Crew — Runs a warm conversational interview with the user
    and converts their answers into a complete financial profile JSON.

    Kickoff:
        result = OnboardingCrew().crew().kickoff()
    """

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks_onboarding.yaml"

    agents: list[BaseAgent]
    tasks:  list[Task]

    @agent
    def interviewer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["interviewer_agent"],
            verbose=True,
        )

    @agent
    def profile_builder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["profile_builder_agent"],
            verbose=True,
            tools=[sip_tool, fire_tool, tax_tool],   # used to validate derived fields
        )

    @task
    def interview_task(self) -> Task:
        return Task(
            config=self.tasks_config["interview_task"],
        )

    @task
    def build_profile_task(self) -> Task:
        return Task(
            config=self.tasks_config["build_profile_task"],
            output_file="outputs/financial_profile.json",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# CREW 2 — FIRE PLANNER
# Analyses the financial profile and builds a FIRE roadmap + SIP plan.
# Input:  {"profile": "<json string from outputs/financial_profile.json>"}
# Output: outputs/fire_roadmap.md
# =============================================================================

@CrewBase
class FIRECrew():
    """
    FIRE Crew — Calculates retirement corpus, gap analysis, and
    builds a month-by-month SIP allocation plan.

    Kickoff:
        profile = open("outputs/financial_profile.json").read()
        result  = FIRECrew().crew().kickoff(inputs={"profile": profile})
    """

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks_fire.yaml"

    agents: list[BaseAgent]
    tasks:  list[Task]

    @agent
    def fire_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["fire_analyst_agent"],
            verbose=True,
            tools=[fire_tool, sip_tool],
        )

    @agent
    def sip_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["sip_planner_agent"],
            verbose=True,
            tools=[sip_tool, fire_tool],
        )

    @task
    def fire_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["fire_analysis_task"],
        )

    @task
    def sip_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["sip_plan_task"],
            output_file="outputs/fire_roadmap.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# CREW 3 — TAX WIZARD
# Researches tax opportunities and compares old vs new regime.
# Input:  {"profile": "<json string from outputs/financial_profile.json>"}
# Output: outputs/tax_analysis.md
# =============================================================================

@CrewBase
class TaxCrew():
    """
    Tax Crew — Finds every applicable deduction, compares old vs new
    regime, and produces a prioritised year-end action plan.

    Kickoff:
        profile = open("outputs/financial_profile.json").read()
        result  = TaxCrew().crew().kickoff(inputs={"profile": profile})
    """

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks_tax.yaml"

    agents: list[BaseAgent]
    tasks:  list[Task]

    @agent
    def tax_researcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["tax_researcher_agent"],
            verbose=True,
            tools=[tax_tool],
        )

    @agent
    def regime_advisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["regime_advisor_agent"],
            verbose=True,
            tools=[tax_tool],
        )

    @task
    def tax_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["tax_research_task"],
        )

    @task
    def tax_regime_task(self) -> Task:
        return Task(
            config=self.tasks_config["tax_regime_task"],
            output_file="outputs/tax_analysis.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# CREW 4 — HEALTH SCORE
# Scores the user across 6 dimensions and builds a 90-day improvement plan.
# Input:  {"profile": "<json string from outputs/financial_profile.json>"}
# Output: outputs/health_score.md
# =============================================================================

@CrewBase
class HealthCrew():
    """
    Health Score Crew — Scores financial health across 6 dimensions
    and produces a concrete, number-driven 90-day improvement plan.

    Kickoff:
        profile = open("outputs/financial_profile.json").read()
        result  = HealthCrew().crew().kickoff(inputs={"profile": profile})
    """

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks_health.yaml"

    agents: list[BaseAgent]
    tasks:  list[Task]

    @agent
    def scorer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["scorer_agent"],
            verbose=True,
            tools=[sip_tool, fire_tool, tax_tool],
        )

    @agent
    def advisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["advisor_agent"],
            verbose=True,
            tools=[sip_tool, tax_tool],
        )

    @task
    def score_task(self) -> Task:
        return Task(
            config=self.tasks_config["score_task"],
        )

    @task
    def advice_task(self) -> Task:
        return Task(
            config=self.tasks_config["advice_task"],
            output_file="outputs/health_score.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# CREW 5 — DAILY FEED
# Fetches live market data and composes a personalised daily brief.
# Input:  {"profile": "<json string from outputs/financial_profile.json>"}
# Output: outputs/daily_feed.md
# =============================================================================

@CrewBase
class FeedCrew():
    """
    Daily Feed Crew — Fetches live market data and filters it down
    to only what is relevant for this specific user's portfolio and goals.

    Kickoff:
        profile = open("outputs/financial_profile.json").read()
        result  = FeedCrew().crew().kickoff(inputs={"profile": profile})
    """

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks_feed.yaml"

    agents: list[BaseAgent]
    tasks:  list[Task]

    @agent
    def market_watcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["market_watcher_agent"],
            verbose=True,
            tools=[market_tool],
        )

    @agent
    def feed_composer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["feed_composer_agent"],
            verbose=True,
            tools=[market_tool, sip_tool],
        )

    @task
    def market_watch_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_watch_task"],
        )

    @task
    def feed_compose_task(self) -> Task:
        return Task(
            config=self.tasks_config["feed_compose_task"],
            output_file="outputs/daily_feed.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# QUICK TEST — run this file directly to smoke-test all crews
# python crew.py
# =============================================================================

if __name__ == "__main__":
    import sys

    crew_map = {
        "onboarding": (OnboardingCrew, {}),
        "fire":       (FIRECrew,       {"profile": "{}"}),
        "tax":        (TaxCrew,        {"profile": "{}"}),
        "health":     (HealthCrew,     {"profile": "{}"}),
        "feed":       (FeedCrew,       {"profile": "{}"}),
    }

    # Load real profile if it exists
    profile_path = "outputs/financial_profile.json"
    profile_str  = "{}"
    if os.path.exists(profile_path):
        with open(profile_path) as f:
            profile_str = f.read()
        print(f"✅ Loaded profile from {profile_path}")
    else:
        print(f"⚠️  No profile found at {profile_path} — using empty profile for tests")

    target = sys.argv[1] if len(sys.argv) > 1 else "onboarding"

    if target not in crew_map:
        print(f"Unknown crew: {target}")
        print(f"Available: {', '.join(crew_map.keys())}")
        sys.exit(1)

    CrewClass, default_inputs = crew_map[target]
    inputs = default_inputs if target == "onboarding" else {"profile": profile_str}

    print(f"\n🚀 Running {target.upper()} crew...\n")
    result = CrewClass().crew().kickoff(inputs=inputs)
    print(f"\n✅ {target.upper()} crew complete.")
    print(result)