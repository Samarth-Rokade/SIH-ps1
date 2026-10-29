# PAIMANA Sentinel AI – Complete Implementation Guide (3-Day MVP)

> AI-powered Predictive Analytics & Early Warning System for Government Infrastructure Projects

## Smart India Hackathon 2026

---

# 1. Project Goal

Build a **software-only**, **open-source**, **AI-powered** monitoring platform that predicts:

- Project delays
- Cost overruns
- Project risk scores
- Early warning alerts

using publicly available PAIMANA report structures and government datasets.

---

# 2. Development Constraints

- ✅ No hardware
- ✅ No paid APIs
- ✅ No proprietary software
- ✅ Open-source tools only
- ✅ Public datasets only
- ✅ Local deployment

---

# 3. Final Deliverables

By the end of Day 3, the project should include:

- React dashboard
- FastAPI backend
- ML prediction engine
- Risk scoring system
- SHAP explainability
- India risk map
- LLM Project Assistant (local)
- SQLite database
- Complete documentation

---

# 4. Tech Stack

## Frontend

- React
- Vite
- TailwindCSS
- Plotly
- Leaflet
- React Router

## Backend

- FastAPI
- SQLAlchemy
- SQLite

## Machine Learning

- Python
- Pandas
- NumPy
- XGBoost
- LightGBM
- Scikit-learn
- SHAP

## Local AI

- Ollama
- Llama 3.2 (3B)

---

# 5. Project Structure

```
PAIMANA-Sentinel/

frontend/
    src/
        pages/
        components/
        charts/
        map/
        services/

backend/
    api/
    models/
    services/
    database/

ml/
    training/
    prediction/
    explainability/
    models/

data/
    raw/
    processed/
    synthetic/

docs/

README.md
```

---

# 6. Free Data Sources

## Primary

### PAIMANA Portal

Purpose:
- Understand CUF fields
- Project schema

### PAIMANA Monthly Reports

Purpose:
- Sample project records
- Cost and progress fields

### Public Dashboard

Purpose:
- Ministry statistics
- Sector statistics

## Secondary

- data.gov.in
- NHAI Reports
- Indian Railways Reports
- Power Ministry Reports

---

# 7. Development Phases

---

# PHASE 1 — Environment Setup

**Estimated Time:** 2 Hours

## Goal

Create the project foundation.

## Tasks

### Backend

- Create FastAPI project.
- Create virtual environment.
- Install dependencies.

Dependencies:

```
fastapi
uvicorn
sqlalchemy
pandas
numpy
xgboost
lightgbm
scikit-learn
shap
```

### Frontend

Create React app.

Install:

```
react-router
tailwindcss
plotly
leaflet
axios
```

## Deliverable

Project runs with:

- Frontend
- Backend
- Empty dashboard

---

# PHASE 2 — Dataset Creation

**Estimated Time:** 3 Hours

## Goal

Create a realistic PAIMANA-style dataset.

## Step 1

Create `projects.csv`

Fields:

| Column |
|---------|
| Project Name |
| Ministry |
| State |
| Sector |
| Original Cost |
| Revised Cost |
| Expenditure |
| Start Date |
| Planned Completion |
| Physical Progress |
| Status |

## Step 2

Generate additional synthetic projects.

Target:

- 5,000 records

Keep distributions realistic.

Example:

- Roads
- Railways
- Power
- Water
- Metro

## Step 3

Create labels.

### Delay Label

```
Delay > 3 months → 1
Else → 0
```

### Cost Overrun Label

```
Escalation > 20% → 1
Else → 0
```

## Deliverable

Clean training dataset.

---

# PHASE 3 — Feature Engineering

**Estimated Time:** 3 Hours

## Goal

Create intelligent features.

### Feature 1

Cost Escalation Ratio

```
Revised Cost / Original Cost
```

### Feature 2

Financial Completion

```
Expenditure / Revised Cost
```

### Feature 3

Project Age

```
Current Date - Start Date
```

### Feature 4

Progress Gap

Expected Progress:

```
Elapsed Time / Planned Duration
```

Gap:

```
Expected - Actual
```

### Feature 5

Burn Rate

```
Expenditure / Project Age
```

## Deliverable

Model-ready dataset.

---

# PHASE 4 — Delay Prediction Model

**Estimated Time:** 3 Hours

## Goal

Predict future delays.

## Model

XGBoost Classifier.

Inputs:

- Ministry
- Sector
- Progress Gap
- Project Age
- Financial Completion
- Burn Rate

Output:

- Delay probability

Example:

```
Delay Risk: 87%
```

## Save model.

```
delay_model.pkl
```

## Deliverable

Working prediction API.

---

# PHASE 5 — Cost Overrun Model

**Estimated Time:** 2 Hours

## Goal

Predict cost escalation.

Model:

XGBoost Regressor.

Output:

```
Predicted Revised Cost
```

Also calculate:

```
Expected Escalation %
```

Save:

```
cost_model.pkl
```

---

# PHASE 6 — Explainable AI

**Estimated Time:** 2 Hours

## Goal

Explain every prediction.

Use SHAP.

Display:

- Progress Gap contribution
- Expenditure contribution
- Ministry contribution

Output example:

```
Risk: 82

Top Reasons

+31 Progress Gap
+18 Low Spending
+12 Previous Escalation
```

## Deliverable

Explanation JSON.

---

# PHASE 7 — Risk Scoring Engine

**Estimated Time:** 2 Hours

## Goal

Convert predictions into easy scores.

Formula:

```
Risk =
40% Delay Probability
30% Cost Risk
20% Progress Gap
10% Spending Gap
```

Levels:

| Score | Level |
|---------|--------|
|0-30|Low|
|31-60|Medium|
|61-80|High|
|81-100|Critical|

## Deliverable

Risk score endpoint.

---

# PHASE 8 — Early Warning Engine

**Estimated Time:** 2 Hours

## Goal

Generate alerts.

Rules:

### Critical

- Risk >80

### High

- Risk 60-80

### Medium

- Risk 30-60

Alert Example

```
Metro Phase III

Critical

Delay Probability: 91%

Reasons

- Low Progress
- Low Spending
```

---

# PHASE 9 — Dashboard Development

**Estimated Time:** 4 Hours

## Goal

Build interactive dashboard.

### Home Page

Cards:

- Total Projects
- High Risk
- Average Delay
- Cost Escalation

### Charts

- Ministry Ranking
- Sector Comparison
- Cost Trend
- Delay Trend

### India Map

Use Leaflet.

Markers:

- Green
- Yellow
- Red

### Project Table

Columns:

- Name
- Ministry
- Risk
- Delay
- Cost

Sorting enabled.

---

# PHASE 10 — AI Assistant

**Estimated Time:** 2 Hours

## Goal

Build local chatbot.

Install:

```
Ollama
```

Run:

```
llama3.2
```

Backend sends project context.

Example Questions

> Why is NH-48 risky?

> Which ministry has highest delays?

> Show critical railway projects.

No internet required.

---

# PHASE 11 — What-if Simulator (Bonus Feature)

**Estimated Time:** 2 Hours

## Goal

Allow officers to test interventions.

Inputs:

- Increase expenditure
- Increase progress
- Reduce delay

AI recalculates risk.

Example

Before

```
Risk: 84
```

After

```
Risk: 46
```

This becomes the strongest demo feature.

---

# 8. API Endpoints

## Prediction

```
POST /predict
```

Returns

```json
{
  "delay_probability":87,
  "cost_risk":74,
  "risk_score":82
}
```

---

## Explain

```
GET /explain/{id}
```

Returns SHAP values.

---

## Dashboard

```
GET /dashboard
```

Returns KPIs.

---

## Alerts

```
GET /alerts
```

Returns critical projects.

---

# 9. Frontend Pages

| Page | Purpose |
|--------|-----------|
|Dashboard|Overview|
|Projects|Project list|
|Project Details|AI explanation|
|Risk Map|Geographical view|
|Analytics|Charts|
|AI Assistant|Chat|
|What-if Simulator|Intervention testing|

---

# 10. Demo Script

## Step 1

Open dashboard.

Show:

- 1,981 monitored projects (demo dataset).

## Step 2

Click high-risk project.

Show:

- Delay prediction
- Cost prediction

## Step 3

Open explanation.

Show SHAP.

## Step 4

Open What-if Simulator.

Increase expenditure.

Risk decreases.

## Step 5

Ask AI Assistant:

> Why is this project delayed?

LLM explains.

---

# 11. Success Criteria

| Feature | Done |
|------------|-------|
|Delay Prediction|☐|
|Cost Prediction|☐|
|Risk Score|☐|
|Alerts|☐|
|Dashboard|☐|
|India Map|☐|
|SHAP|☐|
|LLM Assistant|☐|
|What-if Simulator|☐|

---

# 12. Future Scope

- Live PAIMANA API integration
- Ministry login
- Contractor analytics
- Satellite progress verification
- Automatic report generation
- RAG over government reports