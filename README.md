# AI Money Mentor

AI Money Mentor is a full-stack personal-finance assistant built with a React frontend and a FastAPI + CrewAI backend. The app collects onboarding answers, builds a structured financial profile, and uses that profile across all planner agents.

---

## Features

* Conversational onboarding flow based on backend-managed questions
* Shared profile persistence and reuse across all planners
* Frontend dashboards reflecting onboarding and planner data
* Multi-agent backend orchestration with CrewAI
* FastAPI REST API for frontend integration

---

## Agents

* Onboarding Agent
* FIRE Planner Agent
* Tax Agent
* Health Score Agent
* Daily Feed Agent
* Couple Planner Agent

---

## Tech Stack

**Backend:** Python, FastAPI, CrewAI, uv
**Frontend:** React, Vite, react-router-dom
**Package Managers:** uv (Python), npm (Node)

---

## Project Structure

```
agents/
  frontend/
    src/
      api/
      components/
      pages/
    package.json
    vite.config.js
  src/
    agents/
      api.py
      crew.py
      main.py
      config/
      tools/
  knowledge/
  outputs/
  pyproject.toml
  requirements.txt
```

---

## Architecture

### High-Level Flow

1. User answers onboarding questions in frontend chat
2. Backend maps answers to profile fields
3. Profile is stored in `outputs/financial_profile.json`
4. Planner agents reuse this profile
5. Results are returned to frontend dashboards

---

## Installation

### Prerequisites

* Python 3.10 – 3.13
* Node.js 18+
* npm 9+
* uv installed globally

---

### Backend Setup

```bash
python -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
```

---

### Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the App

### Backend

```bash
uvicorn src.agents.api:app --reload --port 8010
```

### Frontend

```bash
npm run dev
```

---

##  API Endpoints

* `POST /api/onboarding`
* `GET /api/profile`
* `POST /api/fire`
* `POST /api/tax`
* `POST /api/health`
* `POST /api/feed`
* `POST /api/couple`

---

##  Data Model

* Centralized financial profile
* Shared across all agents
* Automatically merged with user inputs
* Persisted and reused

---

##  Troubleshooting

* Ensure correct working directory before running commands
* Check LLM API limits if planners fail
* Verify `.env` configuration
* Restart frontend if stale data appears

---

##  Contributors

* Bharanidharan
* Gnanapprakash
* Anish
* Bhuvanesh

---

##  Notes

* Keep secrets in `.env`
* Do not commit sensitive data
* Ensure `.gitignore` includes `outputs/` and `node_modules/`

---
