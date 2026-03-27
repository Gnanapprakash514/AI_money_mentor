# =============================================================================
# tools.py — All custom tools for AI Money Mentor
# Drop this single file into src/agents/tools/tools.py
#
# Tools included:
#   1. SIPCalculatorTool    — SIP maturity, step-up, milestones
#   2. FIRECalculatorTool   — FIRE corpus, gap, years to retire
#   3. MarketDataTool       — Nifty, Sensex, gold, forex, MF NAV
#   4. TaxRulesTool         — Tax liability, regime comparison, HRA, capital gains
#
# Import in crew files:
#   from tools.tools import SIPCalculatorTool, FIRECalculatorTool, MarketDataTool, TaxRulesTool
# =============================================================================

from crewai.tools import BaseTool
from typing import Type, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# =============================================================================
# TOOL 1 — SIP CALCULATOR
# =============================================================================

class SIPCalculatorInput(BaseModel):
    """Input schema for SIPCalculatorTool."""
    monthly_sip: float = Field(..., description="Monthly SIP amount in INR.")
    annual_return_percent: float = Field(..., description="Expected annual return percentage. E.g. 12 for 12%.")
    years: int = Field(..., description="Investment duration in years.")
    step_up_percent: float = Field(0.0, description="Annual SIP step-up percentage. E.g. 10 for 10% yearly increase. Default is 0 (flat SIP).")
    existing_corpus: float = Field(0.0, description="Existing corpus already invested in INR. Default is 0.")


class SIPCalculatorTool(BaseTool):
    name: str = "SIP Calculator"
    description: str = (
        "Calculates the maturity value of a SIP (Systematic Investment Plan) "
        "given monthly investment amount, expected annual return, and duration. "
        "Also supports step-up SIP (annual increase in SIP amount) and accounts "
        "for an existing corpus. Returns total invested, maturity value, wealth "
        "gained, and a year-by-year milestone table. Use this for FIRE planning, "
        "goal corpus calculations, and SIP allocation recommendations."
    )
    args_schema: Type[BaseModel] = SIPCalculatorInput

    def _run(
        self,
        monthly_sip: float,
        annual_return_percent: float,
        years: int,
        step_up_percent: float = 0.0,
        existing_corpus: float = 0.0,
    ) -> str:
        monthly_rate = annual_return_percent / 100 / 12
        step_up_rate = step_up_percent / 100

        corpus = existing_corpus
        total_invested = existing_corpus
        current_sip = monthly_sip
        milestones = {}
        milestone_targets = [100000, 250000, 500000, 1000000, 2500000, 5000000, 10000000]
        reached = set()
        yearly_table = []

        for year in range(1, years + 1):
            for month in range(12):
                corpus = corpus * (1 + monthly_rate) + current_sip
                total_invested += current_sip
                for target in milestone_targets:
                    if target not in reached and corpus >= target:
                        reached.add(target)
                        milestones[target] = f"Year {year}, Month {month + 1}"
            current_sip = current_sip * (1 + step_up_rate)
            yearly_table.append({
                "year": year,
                "corpus": round(corpus),
                "invested": round(total_invested),
                "gain": round(corpus - total_invested),
            })

        wealth_gained = corpus - total_invested

        def fmt(n):
            if n >= 10000000:
                return f"₹{n/10000000:.2f} Cr"
            elif n >= 100000:
                return f"₹{n/100000:.2f} L"
            else:
                return f"₹{n:,.0f}"

        lines = []
        lines.append("## SIP Calculation Result\n")
        lines.append(f"- **Monthly SIP:** {fmt(monthly_sip)}")
        if step_up_percent > 0:
            lines.append(f"- **Annual Step-Up:** {step_up_percent}%")
        lines.append(f"- **Expected Return:** {annual_return_percent}% p.a.")
        lines.append(f"- **Duration:** {years} years")
        if existing_corpus > 0:
            lines.append(f"- **Existing Corpus:** {fmt(existing_corpus)}")
        lines.append("")
        lines.append(f"### Final Corpus: {fmt(corpus)}")
        lines.append(f"- Total Invested: {fmt(total_invested)}")
        lines.append(f"- Wealth Gained:  {fmt(wealth_gained)}")
        lines.append(f"- Return Multiple: {corpus / total_invested:.2f}x")
        lines.append("")
        lines.append("### Year-by-Year Milestones")
        lines.append("| Year | Corpus | Invested | Gain |")
        lines.append("|------|--------|----------|------|")
        for row in yearly_table:
            lines.append(
                f"| {row['year']} | {fmt(row['corpus'])} | {fmt(row['invested'])} | {fmt(row['gain'])} |"
            )
        if milestones:
            lines.append("")
            lines.append("### Corpus Milestones")
            for target in sorted(milestones):
                lines.append(f"- {fmt(target)}: reached at {milestones[target]}")

        return "\n".join(lines)


# =============================================================================
# TOOL 2 — FIRE CALCULATOR
# =============================================================================

class FIRECalculatorInput(BaseModel):
    """Input schema for FIRECalculatorTool."""
    monthly_expenses: float = Field(..., description="Current monthly expenses in INR.")
    current_age: int = Field(..., description="Current age of the user in years.")
    target_retirement_age: int = Field(..., description="Age at which the user wants to retire.")
    current_corpus: float = Field(..., description="Total current invested corpus in INR (mutual funds + PPF + EPF + NPS + stocks + FD).")
    monthly_savings: float = Field(..., description="Current monthly savings / investment amount in INR.")
    inflation_rate: float = Field(6.0, description="Expected annual inflation rate in percent. Default is 6% for India.")
    pre_retirement_return: float = Field(12.0, description="Expected annual return on investments before retirement in percent. Default 12%.")
    post_retirement_return: float = Field(7.0, description="Expected annual return on corpus after retirement in percent. Default 7%.")
    life_expectancy: int = Field(85, description="Life expectancy in years. Default is 85.")
    withdrawal_rate: float = Field(4.0, description="Safe withdrawal rate in percent per year. Default is 4% (standard FIRE rule).")


class FIRECalculatorTool(BaseTool):
    name: str = "FIRE Calculator"
    description: str = (
        "Calculates everything needed for FIRE (Financial Independence Retire Early) planning. "
        "Given current expenses, age, target retirement age, existing corpus, and savings rate, "
        "it returns: required retirement corpus (inflation-adjusted), years to FIRE, "
        "whether the user is on track, additional monthly savings needed, and a "
        "year-by-year projection table. Adjusted for Indian inflation and market conditions. "
        "Use this for FIRE analysis, retirement planning, and gap identification."
    )
    args_schema: Type[BaseModel] = FIRECalculatorInput

    def _run(
        self,
        monthly_expenses: float,
        current_age: int,
        target_retirement_age: int,
        current_corpus: float,
        monthly_savings: float,
        inflation_rate: float = 6.0,
        pre_retirement_return: float = 12.0,
        post_retirement_return: float = 7.0,
        life_expectancy: int = 85,
        withdrawal_rate: float = 4.0,
    ) -> str:
        years_to_retire = target_retirement_age - current_age
        retirement_duration = life_expectancy - target_retirement_age

        annual_expenses_now = monthly_expenses * 12
        annual_expenses_at_retirement = annual_expenses_now * (
            (1 + inflation_rate / 100) ** years_to_retire
        )

        corpus_by_withdrawal_rate = annual_expenses_at_retirement / (withdrawal_rate / 100)
        corpus_by_pv = annual_expenses_at_retirement * (
            (1 - (1 + post_retirement_return / 100) ** -retirement_duration)
            / (post_retirement_return / 100)
        )
        required_corpus = max(corpus_by_withdrawal_rate, corpus_by_pv)

        monthly_rate = pre_retirement_return / 100 / 12
        projected_corpus = current_corpus
        for _ in range(years_to_retire * 12):
            projected_corpus = projected_corpus * (1 + monthly_rate) + monthly_savings

        gap = required_corpus - projected_corpus
        on_track = gap <= 0

        fire_age = None
        corpus_check = current_corpus
        for month in range((life_expectancy - current_age) * 12):
            corpus_check = corpus_check * (1 + monthly_rate) + monthly_savings
            annual_exp_then = annual_expenses_now * ((1 + inflation_rate / 100) ** (month / 12))
            needed_then = annual_exp_then / (withdrawal_rate / 100)
            if corpus_check >= needed_then and fire_age is None:
                fire_age = round(current_age + month / 12, 1)
                break

        additional_monthly = 0.0
        if not on_track and years_to_retire > 0:
            n = years_to_retire * 12
            r = monthly_rate
            if r > 0:
                additional_monthly = gap / (((1 + r) ** n - 1) / r)
            else:
                additional_monthly = gap / n

        yearly = []
        corpus_iter = current_corpus
        for year in range(1, years_to_retire + 1):
            for _ in range(12):
                corpus_iter = corpus_iter * (1 + monthly_rate) + monthly_savings
            yearly.append({"year": year, "age": current_age + year, "corpus": round(corpus_iter)})

        def fmt(n):
            if n >= 10000000:
                return f"₹{n/10000000:.2f} Cr"
            elif n >= 100000:
                return f"₹{n/100000:.2f} L"
            else:
                return f"₹{n:,.0f}"

        lines = []
        lines.append("## FIRE Calculator Result\n")
        lines.append("### Inputs")
        lines.append(f"- Current age: {current_age} | Target retirement age: {target_retirement_age}")
        lines.append(f"- Monthly expenses today: {fmt(monthly_expenses)}")
        lines.append(f"- Monthly expenses at retirement (inflation-adjusted): {fmt(annual_expenses_at_retirement / 12)}")
        lines.append(f"- Current corpus: {fmt(current_corpus)}")
        lines.append(f"- Monthly savings: {fmt(monthly_savings)}")
        lines.append("")
        lines.append("### FIRE Corpus Required")
        lines.append(f"- **Standard (4% rule):** {fmt(corpus_by_withdrawal_rate)}")
        lines.append(f"- **Conservative (PV method):** {fmt(corpus_by_pv)}")
        lines.append(f"- **Using (higher/safer):** {fmt(required_corpus)}")
        lines.append("")
        lines.append("### Trajectory")
        lines.append(f"- Projected corpus at age {target_retirement_age}: {fmt(projected_corpus)}")
        lines.append(f"- Required corpus: {fmt(required_corpus)}")
        if on_track:
            surplus = projected_corpus - required_corpus
            lines.append(f"- **Status: ON TRACK** — surplus of {fmt(surplus)}")
        else:
            lines.append(f"- **Status: GAP IDENTIFIED** — shortfall of {fmt(abs(gap))}")
            lines.append(f"- Additional monthly savings needed: {fmt(additional_monthly)}")
        if fire_age:
            lines.append(f"- Actual FIRE age at current savings rate: **{fire_age} years**")
        else:
            lines.append("- At current savings rate, FIRE corpus may not be reached within life expectancy.")
        lines.append("")
        lines.append("### Year-by-Year Corpus Projection")
        lines.append("| Year | Age | Projected Corpus |")
        lines.append("|------|-----|-----------------|")
        for row in yearly:
            marker = " ← Target" if row["age"] == target_retirement_age else ""
            lines.append(f"| {row['year']} | {row['age']} | {fmt(row['corpus'])}{marker} |")

        return "\n".join(lines)


# =============================================================================
# TOOL 3 — MARKET DATA
# =============================================================================

class MarketDataInput(BaseModel):
    """Input schema for MarketDataTool."""
    data_type: Literal[
        "indices",
        "gold",
        "forex",
        "stock",
        "mutual_fund_nav",
        "all",
    ] = Field(
        ...,
        description=(
            "Type of market data to fetch. Options: "
            "'indices' — Nifty 50, Sensex, Bank Nifty, Nifty IT; "
            "'gold' — Gold price in INR per 10g; "
            "'forex' — USD/INR exchange rate; "
            "'stock' — a specific NSE stock (requires symbol); "
            "'mutual_fund_nav' — fetch NAV via MFAPI (requires scheme_code); "
            "'all' — fetch indices + gold + forex together."
        ),
    )
    symbol: str = Field(
        "",
        description=(
            "NSE stock ticker symbol for 'stock' data type. "
            "Append '.NS' for NSE stocks. E.g. 'RELIANCE.NS', 'INFY.NS', 'HDFCBANK.NS'."
        ),
    )
    scheme_code: str = Field(
        "",
        description=(
            "MFAPI scheme code for mutual fund NAV. "
            "E.g. '120503' for Axis Bluechip Fund Direct Growth."
        ),
    )


class MarketDataTool(BaseTool):
    name: str = "Market Data Tool"
    description: str = (
        "Fetches live Indian financial market data. "
        "Can retrieve: Nifty 50 and Sensex index levels and day change, "
        "gold price in INR per 10 grams, USD/INR forex rate, "
        "individual NSE stock price and day performance, "
        "and mutual fund NAV via MFAPI. "
        "Use this in the Daily Feed crew for market intelligence and "
        "in the FIRE crew for current portfolio valuation."
    )
    args_schema: Type[BaseModel] = MarketDataInput

    def _run(
        self,
        data_type: str,
        symbol: str = "",
        scheme_code: str = "",
    ) -> str:
        try:
            import yfinance as yf
        except ImportError:
            return "Error: yfinance is not installed. Run: pip install yfinance"

        def fetch_ticker(ticker_symbol: str, label: str) -> dict:
            try:
                t = yf.Ticker(ticker_symbol)
                hist = t.history(period="2d")
                if hist.empty:
                    return {"label": label, "error": "No data"}
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]
                price = latest["Close"]
                change = price - prev["Close"]
                pct = (change / prev["Close"]) * 100
                return {
                    "label": label,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(pct, 2),
                    "high": round(latest["High"], 2),
                    "low": round(latest["Low"], 2),
                    "date": hist.index[-1].strftime("%Y-%m-%d"),
                }
            except Exception as e:
                return {"label": label, "error": str(e)}

        def fmt_ticker(d: dict) -> str:
            if "error" in d:
                return f"- **{d['label']}**: Data unavailable ({d['error']})"
            arrow = "▲" if d["change"] >= 0 else "▼"
            sign = "+" if d["change"] >= 0 else ""
            return (
                f"- **{d['label']}**: {d['price']:,.2f} "
                f"{arrow} {sign}{d['change']:,.2f} ({sign}{d['change_pct']:.2f}%) "
                f"| High: {d['high']:,.2f} | Low: {d['low']:,.2f} | Date: {d['date']}"
            )

        lines = [f"## Market Data ({datetime.now().strftime('%d %b %Y, %I:%M %p')})\n"]

        if data_type in ("indices", "all"):
            lines.append("### Indian Market Indices")
            for sym, label in [
                ("^NSEI",    "Nifty 50"),
                ("^BSESN",   "BSE Sensex"),
                ("^NSEBANK", "Bank Nifty"),
                ("^CNXIT",   "Nifty IT"),
                ("^CNXFMCG", "Nifty FMCG"),
            ]:
                lines.append(fmt_ticker(fetch_ticker(sym, label)))
            lines.append("")

        if data_type in ("gold", "all"):
            lines.append("### Gold Price (INR)")
            try:
                gold = yf.Ticker("GC=F")
                forex = yf.Ticker("INR=X")
                g_hist = gold.history(period="2d")
                f_hist = forex.history(period="1d")
                if not g_hist.empty and not f_hist.empty:
                    gold_usd = g_hist.iloc[-1]["Close"]
                    usd_inr = f_hist.iloc[-1]["Close"]
                    gold_inr_10g = gold_usd * usd_inr / 31.1035 * 10
                    prev_gold = g_hist.iloc[-2]["Close"] if len(g_hist) >= 2 else gold_usd
                    prev_inr_10g = prev_gold * usd_inr / 31.1035 * 10
                    change = gold_inr_10g - prev_inr_10g
                    pct = (change / prev_inr_10g) * 100
                    arrow = "▲" if change >= 0 else "▼"
                    sign = "+" if change >= 0 else ""
                    lines.append(
                        f"- **Gold (10g):** ₹{gold_inr_10g:,.0f} "
                        f"{arrow} {sign}₹{change:,.0f} ({sign}{pct:.2f}%)"
                    )
                    lines.append(f"- Gold USD/oz: ${gold_usd:,.2f} | USD/INR: {usd_inr:.2f}")
                else:
                    lines.append("- Gold data unavailable")
            except Exception as e:
                lines.append(f"- Gold data error: {e}")
            lines.append("")

        if data_type in ("forex", "all"):
            lines.append("### Forex Rates")
            for sym, label in [
                ("INR=X",    "USD/INR"),
                ("EURINR=X", "EUR/INR"),
                ("GBPINR=X", "GBP/INR"),
            ]:
                lines.append(fmt_ticker(fetch_ticker(sym, label)))
            lines.append("")

        if data_type == "stock":
            if not symbol:
                return "Error: 'symbol' is required for data_type='stock'. E.g. 'RELIANCE.NS'"
            lines.append(f"### Stock: {symbol}")
            lines.append(fmt_ticker(fetch_ticker(symbol, symbol)))
            try:
                t = yf.Ticker(symbol)
                info = t.info
                pe = info.get("trailingPE", "N/A")
                mcap = info.get("marketCap", None)
                mcap_str = f"₹{mcap/10000000:,.0f} Cr" if mcap else "N/A"
                lines.append(f"- P/E Ratio: {pe} | Market Cap: {mcap_str}")
            except Exception:
                pass
            lines.append("")

        if data_type == "mutual_fund_nav":
            if not scheme_code:
                return "Error: 'scheme_code' is required for data_type='mutual_fund_nav'."
            try:
                import urllib.request
                import json
                url = f"https://api.mfapi.in/mf/{scheme_code}"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    data = json.loads(resp.read())
                meta = data.get("meta", {})
                navs = data.get("data", [])
                latest = navs[0] if navs else {}
                prev = navs[1] if len(navs) > 1 else {}
                lines.append(f"### Mutual Fund: {meta.get('scheme_name', scheme_code)}")
                lines.append(f"- **NAV:** ₹{latest.get('nav', 'N/A')} (as of {latest.get('date', 'N/A')})")
                if prev:
                    try:
                        change = float(latest["nav"]) - float(prev["nav"])
                        pct = change / float(prev["nav"]) * 100
                        arrow = "▲" if change >= 0 else "▼"
                        lines.append(f"- 1-day change: {arrow} ₹{change:+.4f} ({pct:+.2f}%)")
                    except Exception:
                        pass
                lines.append(f"- Fund house: {meta.get('fund_house', 'N/A')}")
                lines.append(f"- Category: {meta.get('scheme_category', 'N/A')}")
            except Exception as e:
                lines.append(f"- MF NAV fetch error: {e}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# TOOL 4 — INDIAN TAX RULES
# =============================================================================

class TaxRulesInput(BaseModel):
    """Input schema for TaxRulesTool."""
    calculation_type: Literal[
        "tax_liability",
        "regime_comparison",
        "hra_exemption",
        "capital_gains",
        "deduction_summary",
    ] = Field(
        ...,
        description=(
            "Type of tax calculation. Options: "
            "'tax_liability' — compute tax for a given income and deductions; "
            "'regime_comparison' — compare old vs new regime side by side; "
            "'hra_exemption' — compute HRA exemption using least of 3 rules; "
            "'capital_gains' — compute LTCG / STCG tax on equity or debt; "
            "'deduction_summary' — summarise all 80C/80D/80CCD deduction limits and usage."
        ),
    )
    annual_gross_income: float = Field(0.0, description="Annual gross income in INR.")
    is_salaried: bool = Field(True, description="True if the user is a salaried employee.")
    section_80c: float = Field(0.0, description="Total Section 80C investments in INR. Max ₹1,50,000.")
    section_80d: float = Field(0.0, description="Health insurance premium paid in INR. Max ₹25,000 self (₹50,000 if parents are senior citizens).")
    section_80ccd1b: float = Field(0.0, description="Additional NPS contribution under 80CCD(1B) in INR. Max ₹50,000.")
    home_loan_interest: float = Field(0.0, description="Home loan interest paid in INR. Max ₹2,00,000 under Section 24(b).")
    hra_exemption: float = Field(0.0, description="HRA exemption amount in INR. Use 'hra_exemption' type to compute.")
    other_deductions: float = Field(0.0, description="Other deductions in INR: 80G, 80E, LTA, etc.")
    basic_salary: float = Field(0.0, description="Monthly basic salary in INR. Required for HRA calculation.")
    hra_received: float = Field(0.0, description="Monthly HRA received from employer in INR.")
    rent_paid: float = Field(0.0, description="Monthly rent paid in INR.")
    is_metro: bool = Field(False, description="True if user lives in a metro city (Mumbai, Delhi, Kolkata, Chennai).")
    equity_ltcg: float = Field(0.0, description="Long-term capital gains from equity held > 1 year in INR.")
    equity_stcg: float = Field(0.0, description="Short-term capital gains from equity held < 1 year in INR.")
    debt_gains: float = Field(0.0, description="Gains from debt mutual funds in INR (taxed as per income slab).")


class TaxRulesTool(BaseTool):
    name: str = "Indian Tax Rules Tool"
    description: str = (
        "Computes Indian income tax calculations based on current tax rules. "
        "Can calculate: income tax liability under old and new regime, "
        "old vs new regime comparison with exact INR savings, "
        "HRA exemption using the least of 3 rules, "
        "LTCG and STCG tax on equity and debt investments, "
        "and a full deduction summary showing 80C/80D/80CCD utilisation and gaps. "
        "All calculations include 4% cess and follow current Income Tax Act rules. "
        "Use this in the Tax Wizard crew for all tax-related tasks."
    )
    args_schema: Type[BaseModel] = TaxRulesInput

    def _compute_tax_old_regime(self, taxable_income: float) -> float:
        tax = 0.0
        slabs = [
            (250000, 0.00),
            (500000, 0.05),
            (1000000, 0.20),
            (float("inf"), 0.30),
        ]
        prev = 0
        for limit, rate in slabs:
            if taxable_income <= prev:
                break
            taxable_in_slab = min(taxable_income, limit) - prev
            tax += taxable_in_slab * rate
            prev = limit
        if taxable_income <= 500000:
            tax = max(0, tax - 12500)
        return tax

    def _compute_tax_new_regime(self, taxable_income: float) -> float:
        tax = 0.0
        slabs = [
            (300000, 0.00),
            (600000, 0.05),
            (900000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float("inf"), 0.30),
        ]
        prev = 0
        for limit, rate in slabs:
            if taxable_income <= prev:
                break
            taxable_in_slab = min(taxable_income, limit) - prev
            tax += taxable_in_slab * rate
            prev = limit
        if taxable_income <= 700000:
            tax = 0
        return tax

    def _add_cess(self, tax: float) -> float:
        return tax * 1.04

    def _run(
        self,
        calculation_type: str,
        annual_gross_income: float = 0.0,
        is_salaried: bool = True,
        section_80c: float = 0.0,
        section_80d: float = 0.0,
        section_80ccd1b: float = 0.0,
        home_loan_interest: float = 0.0,
        hra_exemption: float = 0.0,
        other_deductions: float = 0.0,
        basic_salary: float = 0.0,
        hra_received: float = 0.0,
        rent_paid: float = 0.0,
        is_metro: bool = False,
        equity_ltcg: float = 0.0,
        equity_stcg: float = 0.0,
        debt_gains: float = 0.0,
    ) -> str:

        def fmt(n):
            if abs(n) >= 10000000:
                return f"₹{n/10000000:.2f} Cr"
            elif abs(n) >= 100000:
                return f"₹{n/100000:.2f} L"
            else:
                return f"₹{n:,.0f}"

        lines = []

        if calculation_type == "tax_liability":
            std_deduction    = 50000 if is_salaried else 0
            d_80c            = min(section_80c, 150000)
            d_80d            = min(section_80d, 75000)
            d_80ccd1b        = min(section_80ccd1b, 50000)
            d_24b            = min(home_loan_interest, 200000)
            total_deductions = (
                std_deduction + d_80c + d_80d + d_80ccd1b +
                d_24b + hra_exemption + other_deductions
            )
            taxable   = max(0, annual_gross_income - total_deductions)
            tax_raw   = self._compute_tax_old_regime(taxable)
            tax_final = self._add_cess(tax_raw)

            lines.append("## Tax Liability — Old Regime\n")
            lines.append(f"- Gross Income: {fmt(annual_gross_income)}")
            lines.append(f"- Standard Deduction: {fmt(std_deduction)}")
            lines.append(f"- 80C: {fmt(d_80c)} | 80D: {fmt(d_80d)} | 80CCD(1B): {fmt(d_80ccd1b)}")
            lines.append(f"- Section 24(b) home loan interest: {fmt(d_24b)}")
            lines.append(f"- HRA Exemption: {fmt(hra_exemption)}")
            lines.append(f"- Other deductions: {fmt(other_deductions)}")
            lines.append(f"- **Total Deductions: {fmt(total_deductions)}**")
            lines.append(f"- **Taxable Income: {fmt(taxable)}**")
            lines.append(f"- Tax before cess: {fmt(tax_raw)}")
            lines.append(f"- **Final Tax (incl. 4% cess): {fmt(tax_final)}**")
            if annual_gross_income:
                lines.append(f"- Effective Tax Rate: {(tax_final/annual_gross_income*100):.2f}%")

        elif calculation_type == "regime_comparison":
            std_ded = 50000 if is_salaried else 0
            old_deductions = (
                std_ded +
                min(section_80c, 150000) +
                min(section_80d, 75000) +
                min(section_80ccd1b, 50000) +
                min(home_loan_interest, 200000) +
                hra_exemption + other_deductions
            )
            old_taxable = max(0, annual_gross_income - old_deductions)
            old_tax     = self._add_cess(self._compute_tax_old_regime(old_taxable))
            new_taxable = max(0, annual_gross_income - std_ded)
            new_tax     = self._add_cess(self._compute_tax_new_regime(new_taxable))
            saving      = new_tax - old_tax
            better      = "Old Regime" if saving > 0 else "New Regime"

            lines.append("## Old vs New Tax Regime Comparison\n")
            lines.append("| | Old Regime | New Regime |")
            lines.append("|---|---|---|")
            lines.append(f"| Gross Income | {fmt(annual_gross_income)} | {fmt(annual_gross_income)} |")
            lines.append(f"| Total Deductions | {fmt(old_deductions)} | {fmt(std_ded)} |")
            lines.append(f"| Taxable Income | {fmt(old_taxable)} | {fmt(new_taxable)} |")
            lines.append(f"| Tax Payable (incl. cess) | {fmt(old_tax)} | {fmt(new_tax)} |")
            if annual_gross_income:
                lines.append(
                    f"| Effective Rate | {old_tax/annual_gross_income*100:.2f}% | {new_tax/annual_gross_income*100:.2f}% |"
                )
            lines.append("")
            lines.append(f"### Verdict: **{better}** saves {fmt(abs(saving))} per year")
            if better == "Old Regime":
                lines.append(
                    f"\nStay on the old regime. Your deductions ({fmt(old_deductions)}) "
                    "are large enough to justify the complexity."
                )
            else:
                lines.append(
                    f"\nSwitch to the new regime. Your deductions ({fmt(old_deductions)}) "
                    "are insufficient to offset the lower new-regime slabs."
                )

        elif calculation_type == "hra_exemption":
            annual_basic   = basic_salary * 12
            annual_hra_rcv = hra_received * 12
            annual_rent    = rent_paid * 12
            hra_pct        = 0.50 if is_metro else 0.40
            rule1          = annual_hra_rcv
            rule2          = annual_basic * hra_pct
            rule3          = max(0, annual_rent - annual_basic * 0.10)
            exemption      = min(rule1, rule2, rule3)
            taxable_hra    = annual_hra_rcv - exemption

            lines.append("## HRA Exemption Calculation\n")
            lines.append(f"- Annual Basic Salary: {fmt(annual_basic)}")
            lines.append(f"- Annual HRA Received: {fmt(annual_hra_rcv)}")
            lines.append(f"- Annual Rent Paid: {fmt(annual_rent)}")
            lines.append(f"- City type: {'Metro' if is_metro else 'Non-Metro'}")
            lines.append("")
            lines.append("### Least of 3 Rules:")
            lines.append(f"1. Actual HRA received: {fmt(rule1)}")
            lines.append(f"2. {int(hra_pct*100)}% of basic salary: {fmt(rule2)}")
            lines.append(f"3. Rent paid minus 10% of basic: {fmt(rule3)}")
            lines.append("")
            lines.append(f"**HRA Exemption (least of above): {fmt(exemption)}**")
            lines.append(f"Taxable HRA: {fmt(taxable_hra)}")

        elif calculation_type == "capital_gains":
            ltcg_exempt  = 100000
            ltcg_taxable = max(0, equity_ltcg - ltcg_exempt)
            ltcg_tax     = ltcg_taxable * 0.125
            stcg_tax     = equity_stcg * 0.20
            total_cg_tax = self._add_cess(ltcg_tax + stcg_tax)

            lines.append("## Capital Gains Tax (FY 2024-25)\n")
            lines.append("### Equity (Stocks and Equity MF)")
            lines.append(f"- LTCG (held > 1 year): {fmt(equity_ltcg)}")
            lines.append(f"  - Exempt (first ₹1L): {fmt(min(equity_ltcg, ltcg_exempt))}")
            lines.append(f"  - Taxable LTCG: {fmt(ltcg_taxable)} @ 12.5%")
            lines.append(f"  - **LTCG Tax: {fmt(ltcg_tax)}**")
            lines.append(f"- STCG (held < 1 year): {fmt(equity_stcg)} @ 20%")
            lines.append(f"  - **STCG Tax: {fmt(stcg_tax)}**")
            if debt_gains > 0:
                lines.append("")
                lines.append("### Debt Mutual Funds (post April 2023)")
                lines.append(f"- Gains: {fmt(debt_gains)} — taxed as per income slab (no indexation)")
            lines.append(f"\n**Total Capital Gains Tax (incl. 4% cess): {fmt(total_cg_tax)}**")
            lines.append("\n**Tax Loss Harvesting Tip:** Book unrealised losses before 31st March to offset gains.")

        elif calculation_type == "deduction_summary":
            c80c_used  = min(section_80c, 150000)
            c80c_gap   = max(0, 150000 - section_80c)
            c80d_used  = min(section_80d, 25000)
            c80d_gap   = max(0, 25000 - section_80d)
            nps_used   = min(section_80ccd1b, 50000)
            nps_gap    = max(0, 50000 - section_80ccd1b)
            hl_used    = min(home_loan_interest, 200000)
            hl_gap     = max(0, 200000 - home_loan_interest)
            total_used = c80c_used + c80d_used + nps_used + hl_used + hra_exemption
            total_poss = 150000 + 25000 + 50000 + 200000

            lines.append("## Deduction Summary\n")
            lines.append("| Section | Limit | Used | Gap | Best Instrument to Fill Gap |")
            lines.append("|---------|-------|------|-----|-----------------------------|")
            lines.append(f"| 80C | ₹1,50,000 | {fmt(c80c_used)} | {fmt(c80c_gap)} | ELSS mutual fund |")
            lines.append(f"| 80D (self) | ₹25,000 | {fmt(c80d_used)} | {fmt(c80d_gap)} | Top-up health insurance |")
            lines.append(f"| 80CCD(1B) NPS | ₹50,000 | {fmt(nps_used)} | {fmt(nps_gap)} | NPS Tier-1 contribution |")
            lines.append(f"| 24(b) Home Loan Int. | ₹2,00,000 | {fmt(hl_used)} | {fmt(hl_gap)} | N/A (depends on loan) |")
            lines.append(f"| HRA Exemption | Computed | {fmt(hra_exemption)} | — | Ensure rent receipts filed |")
            lines.append("")
            lines.append(f"**Total deductions used: {fmt(total_used)}**")
            lines.append(f"**Maximum possible (excl. HRA): {fmt(total_poss)}**")
            lines.append(f"**Deduction utilisation: {total_used/total_poss*100:.1f}%**")

        else:
            lines.append(f"Unknown calculation_type: {calculation_type}")

        return "\n".join(lines)