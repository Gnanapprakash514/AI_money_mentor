# AI Money Mentor

An AI-powered personal finance assistant for Indian investors. Built with [CrewAI](https://crewai.com) multi-agent framework and served via a FastAPI backend.

Five specialised AI crews analyse your financial profile and generate personalised reports on FIRE planning, tax optimisation, financial health, and daily market insights.

---

## Features

| Crew | Endpoint | Output |
|---|---|---|
| Onboarding | `POST /onboarding` | Structured financial profile (JSON) |
| FIRE Planner | `POST /fire` | Retirement corpus plan & SIP roadmap |
| Tax Wizard | `POST /tax` | Old vs new regime comparison & year-end action plan |
| Health Score | `POST /health` | 6-dimension financial health score & 90-day plan |
| Daily Feed | `POST /feed` | Personalised market insights & portfolio alerts |

---

## Tech Stack

- **AI Agents** — [CrewAI](https://crewai.com) with `llama-3.3-70b-versatile` via Groq
- **Backend** — FastAPI + Uvicorn
- **Tools** — Custom SIP calculator, FIRE calculator, Indian tax rules engine, live market data (yfinance)
- **Package manager** — [uv](https://docs.astral.sh/uv/)

---

## Setup

**Prerequisites:** Python 3.10–3.13, [uv](https://docs.astral.sh/uv/)

```bash
# 1. Install dependencies
pip install uv
uv sync

# 2. Configure environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 3. Start the server
python run_server.py
```

API docs available at `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```
MODEL=groq/llama-3.3-70b-versatile
GROQ_API_KEY=your_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## API Usage

### 1. Create a profile (required first)

```bash
curl -X POST http://localhost:8000/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "marital_status": "single",
    "age": 28,
    "occupation": "Software Engineer",
    "annual_income": 1200000,
    "monthly_take_home_salary": 80000,
    "monthly_expenses": {
      "housing": 15000, "groceries": 8000, "transportation": 5000,
      "utilities": 3000, "entertainment": 5000, "savings": 20000,
      "debt_repayment": 0, "other": 2000
    },
    "risk_appetite": "Moderate"
  }'
```

### 2. Run an analysis crew

Analysis endpoints return a `job_id` immediately (crews run in the background):

```bash
# FIRE planning
curl -X POST http://localhost:8000/fire \
  -H "Content-Type: application/json" \
  -d '{"years": 27, "target_income": 80000, "inflation": 6.0}'

# Tax optimisation
curl -X POST http://localhost:8000/tax \
  -H "Content-Type: application/json" \
  -d '{"regime": "new", "deductions": 150000}'

# Financial health score
curl -X POST http://localhost:8000/health \
  -H "Content-Type: application/json" \
  -d '{"emergency_fund": 300000, "savings_rate": 25.0}'

# Daily feed (no body required)
curl -X POST http://localhost:8000/feed
```

### 3. Poll for results

```bash
curl http://localhost:8000/jobs/<job_id>
```

### 4. Retrieve generated reports

```bash
curl http://localhost:8000/outputs/fire    # fire | tax | health | feed
```

---

## Project Structure

```
agents/
├── src/agents/
│   ├── backend/
│   │   └── app.py              # FastAPI app — all endpoints
│   ├── config/
│   │   ├── agents.yaml         # Agent role/goal/backstory definitions
│   │   ├── tasks.yaml          # Detailed task prompts for all 5 crews
│   │   ├── tasks_fire.yaml
│   │   ├── tasks_tax.yaml
│   │   ├── tasks_health.yaml
│   │   ├── tasks_feed.yaml
│   │   └── tasks_onboarding.yaml
│   ├── tools/
│   │   └── custom_tool.py      # SIP, FIRE, Tax, Market Data tools
│   ├── crew.py                 # All 5 CrewAI crew definitions
│   ├── main.py                 # CLI entry point
│   └── e2e_terminal.py         # Interactive terminal onboarding flow
├── knowledge/                  # Drop domain knowledge files here
├── outputs/                    # Generated reports land here (git-ignored)
├── tests/
├── run_server.py               # Server launcher (python run_server.py)
├── pyproject.toml
└── .env
```

---

## Running via CLI

```bash
# Run a specific crew interactively
uv run agents onboarding
uv run agents fire
uv run agents tax
uv run agents health
uv run agents feed

# Full end-to-end conversational flow
uv run agents e2e
```

---

## Notes

- The free Groq tier has a 12,000 TPM rate limit. Avoid firing multiple crews simultaneously.
- All monetary values are in Indian Rupees (INR).
- Generated reports are saved to `outputs/` and are git-ignored.
