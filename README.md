# AI Money Mentor

AI Money Mentor is a full-stack personal-finance assistant built with a React frontend and a FastAPI + CrewAI backend. The app collects onboarding answers, builds a structured financial profile, and uses that profile across all planner agents:

- Onboarding Agent
- FIRE Planner Agent
- Tax Agent
- Health Score Agent
- Daily Feed Agent
- Couple Planner Agent

## Features

- Conversational onboarding flow based on backend-managed questions
- Shared profile persistence and reuse across all planners
- Frontend dashboards reflecting onboarding and planner data
- Multi-agent backend orchestration with CrewAI
- FastAPI REST API for frontend integration

## Tech Stack

- Backend: Python, FastAPI, CrewAI, uv
- Frontend: React, Vite, react-router-dom
- Package Managers: uv (Python), npm (Node)

## Project Structure

```text
agents/
	frontend/
		src/
			api/
				client.js
			components/
				Layout.jsx
			pages/
				Onboarding.jsx
				Dashboard.jsx
				FIREPlanner.jsx
				TaxWizard.jsx
				HealthScore.jsx
				CouplePlanner.jsx
			App.jsx
			main.jsx
		package.json
		vite.config.js
	src/
		agents/
			api.py
			crew.py
			e2e_terminal.py
			main.py
			config/
				agents.yaml
				tasks_onboarding.yaml
				tasks_fire.yaml
				tasks_tax.yaml
				tasks_health.yaml
				tasks_feed.yaml
			tools/
				tools.py
				custom_tool.py
	knowledge/
	outputs/
	pyproject.toml
	requirements.txt
```

## Architecture

### High-Level Flow

1. User answers onboarding questions in frontend chat.
2. Backend onboarding endpoint maps answers to profile fields.
3. Profile is saved to outputs/financial_profile.json.
4. Planner endpoints resolve this saved profile by default.
5. Planner results are returned to frontend pages.

### Backend Layers

- api.py: FastAPI routes, profile persistence, merge and orchestration logic
- crew.py: CrewAI agent/task definitions and output generation
- config/*.yaml: Agent role/task prompt configuration
- e2e_terminal.py: Reference onboarding and planner pipeline flow

### Frontend Layers

- src/api/client.js: API calls, profile storage, onboarding helpers
- pages/*: Route-specific planners and dashboards
- components/Layout.jsx: App shell and navigation

## Installation

### Prerequisites

- Python 3.10 to 3.13
- Node.js 18+
- npm 9+
- uv installed globally

Install uv (if needed):

```powershell
pip install uv
```

### 1) Backend Setup

From agents root:

```powershell
Set-Location C:\Users\BHARANIDHARAN.S\Downloads\gen_ai\gen_ai\Money\agents
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
uv sync
```

Alternative pip install using requirements file:

```powershell
pip install -r requirements.txt
```

### 2) Frontend Setup

```powershell
Set-Location C:\Users\BHARANIDHARAN.S\Downloads\gen_ai\gen_ai\Money\agents\frontend
npm install
```

## Environment Variables

Create or update .env in agents root with provider keys used by CrewAI and your configured LLM provider.

Typical values include:

- OPENAI_API_KEY or GROQ_API_KEY (depending on your model config)
- Any other keys required by your agent tools

Do not commit .env.

## How To Run

Use two terminals.

### Terminal A: Backend

```powershell
Set-Location C:\Users\BHARANIDHARAN.S\Downloads\gen_ai\gen_ai\Money\agents
. .\.venv\Scripts\Activate.ps1
uv run uvicorn src.agents.api:app --host 127.0.0.1 --port 8010 --reload
```

### Terminal B: Frontend

```powershell
Set-Location C:\Users\BHARANIDHARAN.S\Downloads\gen_ai\gen_ai\Money\agents\frontend
$env:VITE_API_BASE_URL="http://127.0.0.1:8010"
npm run dev
```

Open:

- Frontend: http://127.0.0.1:5173 (or next free Vite port shown in terminal)
- Backend docs: http://127.0.0.1:8010/docs

## API Endpoints

- POST /api/onboarding
	- Receives incremental onboarding chat history
	- Returns next question or completion payload with built profile
- GET /api/profile
	- Returns saved onboarding profile
- POST /api/fire
	- Runs FIRE planner using saved profile (or merged input profile)
- POST /api/tax
	- Runs tax analysis
- POST /api/health
	- Runs health analysis and returns score
- POST /api/feed
	- Runs daily feed generation
- POST /api/couple
	- Runs couple planning using merged profile + page inputs

## Data Consistency Model

The app uses a shared profile model:

- Onboarding creates and persists the canonical profile
- Planner routes auto-load saved profile when request profile is empty
- Planner routes deep-merge incoming page values over saved profile
- Frontend stores a local profile copy and refreshes from /api/profile

This ensures onboarding values are reused across all pages and agents.

## Build Commands

Frontend production build:

```powershell
Set-Location C:\Users\BHARANIDHARAN.S\Downloads\gen_ai\gen_ai\Money\agents\frontend
npm run build
```

## Troubleshooting

### 1) npm run dev fails with ENOENT package.json

Cause: Wrong terminal directory.

Fix:

```powershell
Set-Location C:\Users\BHARANIDHARAN.S\Downloads\gen_ai\gen_ai\Money\agents\frontend
npm run dev
```

### 2) Uvicorn fails to bind port

Cause: Port already in use or permission conflict.

Fix: Start on a different port, then match frontend API base URL.

### 3) Planner returns rate limit exceeded

Cause: LLM provider quota exceeded (for example Groq daily token limits).

Fix options:

- Wait for reset window
- Upgrade provider tier
- Switch model/provider key in environment/config

### 4) Frontend opens but values look stale

Cause: Old local profile data or onboarding incomplete.

Fix options:

- Complete onboarding again
- Call GET /api/profile to verify saved data
- Hard refresh browser

## Notes For Deployment

- Keep backend and frontend base URL aligned via VITE_API_BASE_URL.
- Store secrets in environment variables, never in repository.
- Ensure outputs/ and node_modules/ are ignored in git.

## License

Internal/Project-specific. Add your preferred license file if publishing publicly.
