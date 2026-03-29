# =============================================================================
# crew.py — FINAL WORKING VERSION (NO YAML, NO ERRORS, WITH expected_output)
# =============================================================================

from crewai import Agent, Crew, Process, Task

from .tools.tools import (
    SIPCalculatorTool,
    FIRECalculatorTool,
    MarketDataTool,
    TaxRulesTool,
)

# Tools
sip_tool    = SIPCalculatorTool()
fire_tool   = FIRECalculatorTool()
market_tool = MarketDataTool()
tax_tool    = TaxRulesTool()


# =============================================================================
# ONBOARDING CREW
# =============================================================================

class OnboardingCrew:

    def crew(self):

        agent = Agent(
            role="Financial Profile Architect",
            goal="Convert user input into structured JSON",
            backstory="Strict processor. Never invent values.",
            verbose=True,
        )

        task = Task(
            description="""
            Use ONLY the provided user_profile.

            DO NOT generate anything.
            DO NOT assume anything.

            INPUT:
            {user_profile}
            """,
            expected_output="Valid structured JSON financial profile",
            agent=agent,
            output_file="outputs/financial_profile.json",
        )

        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# FIRE CREW
# =============================================================================

class FIRECrew:

    def crew(self):

        agent = Agent(
            role="FIRE Planner",
            goal="Generate retirement plan",
            backstory="Expert financial planner who calculates retirement strategies accurately.",
            verbose=True,
            tools=[fire_tool, sip_tool],
        )

        task = Task(
            description="""
            Profile: {profile}
            Years: {years}
            Target Income: {target_income}
            Inflation: {inflation}

            Generate FIRE plan.
            """,
            expected_output="Detailed FIRE retirement plan",
            agent=agent,
            output_file="outputs/fire_roadmap.md",
        )

        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# TAX CREW
# =============================================================================

class TaxCrew:

    def crew(self):

        agent = Agent(
            role="Tax Advisor",
            goal="Optimize taxes",
            backstory="Expert in Indian tax laws who provides accurate tax optimization strategies.",
            verbose=True,
            tools=[tax_tool],
        )

        task = Task(
            description="""
            Profile: {profile}
            Regime: {regime}
            Deductions: {deductions}

            Generate tax optimization.
            """,
            expected_output="Tax optimization report",
            agent=agent,
            output_file="outputs/tax_analysis.md",
        )

        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# HEALTH CREW
# =============================================================================

class HealthCrew:

    def crew(self):

        agent = Agent(
            role="Financial Health Advisor",
            goal="Evaluate financial health",
            backstory="Financial advisor analyzing savings, risk, and financial stability.",
            verbose=True,
            tools=[sip_tool, tax_tool],
        )

        task = Task(
            description="""
            Profile: {profile}
            Emergency Fund: {emergency_fund}
            Savings Rate: {savings_rate}

            Generate health score and advice.
            """,
            expected_output="Financial health score and improvement plan",
            agent=agent,
            output_file="outputs/health_score.md",
        )

        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# FEED CREW
# =============================================================================

class FeedCrew:

    def crew(self):

        agent = Agent(
            role="Market Feed Generator",
            goal="Generate financial feed",
            backstory="A financial market analyst who tracks daily trends and generates personalized insights based on user profiles.",
            verbose=True,
            tools=[],   # 🔥 REMOVE market_tool
        )

        task = Task(
            description="""
            Profile: {profile}
            Generate a personalized daily financial feed including:
            - Market insights
            - Savings tips
            - Investment suggestions
            """,
            expected_output="Daily personalized financial market feed",
            agent=agent,
            output_file="outputs/daily_feed.md",
        )

        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )