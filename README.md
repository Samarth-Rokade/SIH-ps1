# PAIMANA Sentinel AI

AI-powered predictive analytics and early-warning system for central-sector infrastructure projects
(Smart India Hackathon). It predicts project **delays** and **cost overruns**, produces an explainable
**risk score** per project, raises **early-warning alerts**, and lets officers test **what-if interventions**
and ask questions of a **local AI assistant**. Fully open-source, fully local, no paid APIs.

## Features

| Area | What it does |
|---|---|
| Command Center | KPIs, India risk map (all projects, canvas-rendered), risk distribution, risk trend, priority projects |
| Risk Radar | Delay-probability vs cost-risk scatter of **every** project (canvas, instant hover/click), filters, clusters |
| Projects / Project Intelligence | Searchable table; per-project risk score, delay + cost prediction, SHAP risk drivers, progress and cost history, timeline, peer benchmark |
| Early Warnings | Rule-based alerts with severity/status filters, detail panel, acknowledge / resolve workflow |
| Analytics | Ministry, sector and state benchmarking |
| Cost Intelligence | Cost totals, escalation, sector breakdown, highest forecast exposure |
| What-if Simulator | Change progress / expenditure / milestone recovery and re-score the project with the trained models |
| AI Assistant | Question answering grounded in the database; uses a local Ollama model when available, built-in answer engine otherwise |
| Reports | Portfolio and per-project PDF reports |
| Settings | System / data / model status, theme |

## Tech stack

React 19 + Vite + Tailwind 4 + Recharts + Leaflet (frontend) · FastAPI + SQLAlchemy + SQLite (backend) ·
XGBoost / SHAP / scikit-learn (ML) · reportlab (PDF) · Ollama + Llama 3.2 (optional local LLM).

## Quick start

### 1. Backend (Python 3.13+)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000 · interactive docs: http://127.0.0.1:8000/docs · health: `/api/health`

The repository ships a ready-to-run `backend/paimana.db` and trained models in `ml/models/`, so no setup
beyond the above is needed.

### 2. Frontend (Node 20+)

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (http://127.0.0.1:5173 by default). The API base URL is set in `frontend/.env`
(`VITE_API_BASE_URL=http://localhost:8000/api/v1`). The backend accepts any `localhost` / `127.0.0.1` port.

### 3. Optional: local LLM for the assistant

The assistant works out of the box with a deterministic, database-grounded answer engine. To have a local
model phrase the answers instead:

```powershell
# install Ollama from https://ollama.com, then
ollama pull llama3.2
```

The backend detects it automatically (Settings page shows the status). Override with the `OLLAMA_URL`
(default `http://localhost:11434`) and `OLLAMA_MODEL` (default `llama3.2`) environment variables. The model
only receives facts retrieved from the database and is instructed not to invent statistics.

## How it works

```
data/projects.csv  ──►  ml/features.py  ──►  XGBoost delay + cost models (ml/training/*.py → ml/models/*.pkl)
                                                   │
                       backend/app/ml/seed.py ─────┘  scores every project, SHAP drivers, alerts  ──►  backend/paimana.db
                                                                                                         │
React dashboard  ◄──  FastAPI (/api/v1/*)  ◄──  services (SQL queries, simulator re-scoring, assistant, reports)
```

Risk score = 50 % delay probability + 25 % cost-overrun probability + 15 % progress gap + 10 % spend/progress
mismatch; levels: low ≤ 30 < medium ≤ 60 < high ≤ 80 < critical. These are prototype decision-support weights.

### Regenerating data and models

```powershell
python data/build_dataset.py            # rebuild data/projects.csv (see data/README.md)
python ml/training/train_delay_model.py # retrain delay models
python ml/training/train_cost_model.py  # retrain cost models
python -m backend.app.ml.seed           # re-score everything and rebuild backend/paimana.db
```

(run from the project root with the backend virtualenv active; `seed` resets alert statuses.)

## API overview (`/api/v1`)

`dashboard/*` · `risk/radar|summary|filters` · `projects` and `projects/{id}/…`
(`risk`, `prediction/delay`, `prediction/cost`, `risk-drivers`, `progress`, `cost-history`, `timeline`, `benchmark`) ·
`alerts` (`GET`, `GET /{id}`, `PATCH /{id}`) · `analytics/ministries|sectors|states|cost` ·
`simulator/{id}/parameters`, `simulator/run` · `assistant/chat|suggestions` ·
`reports` (`GET`, `POST project/{id}`, `POST dashboard`, `GET {id}/download`) · `system/status|data-info|models`.
Full contract: `docs/PAIMANA_Sentinel_AI_Backend_API_Specification.md`. Every response uses the
`{success, data, meta}` / `{success:false, error:{code,message}}` envelope.

## Data and honesty notes

- The dataset is 1,800 real records from the MoSPI PAIMANA Flash Report (July 2026) plus 1,800 synthetic
  records derived from them (see `data/README.md`). Map coordinates are state centroids with jitter.
- The source is a single monthly snapshot, so the **risk trend**, **progress history** and **cost history**
  are *modeled* series that end exactly at each project's real current values; the API flags this
  (`meta.modeled`) and the UI labels it.
- Simulator and prediction outputs are model-based scenario estimates, not guaranteed outcomes.
  "Milestone recovery" is a modeled assumption (share of schedule slippage recovered: 10 / 25 / 40 %).
- Generated PDF reports are stored in `backend/reports/` (git-ignored).

## Repository layout

```
backend/   FastAPI app (api/, services/, ml/, database/, utils/), paimana.db, reports/
frontend/  React app (pages/, components/, api/, hooks/, theme/)
ml/        feature engineering, training scripts, trained models
data/      dataset build scripts and projects.csv
docs/      PRD, implementation guide, API specification
```
