# PAIMANA Sentinel AI

## Product Requirements Document

### Hackathon

Smart India Hackathon

### Problem Statement

Develop an AI-powered Predictive Analytics and Early Warning System for PAIMANA using only open-source software and publicly available datasets.

## Objectives

- Predict project delays.
- Predict cost overruns.
- Generate project risk scores.
- Provide explainable AI.
- Build an interactive monitoring dashboard.
- Integrate a local LLM assistant.

## Constraints

- No paid APIs.
- No hardware.
- No government login.
- Only open-source tools.
- Only public datasets.

## Tech Stack

- React
- FastAPI
- Python
- XGBoost
- LightGBM
- SHAP
- SQLite
- Plotly
- Leaflet
- Ollama
- Llama 3.2

## User Personas

### MoSPI Officer

Needs:

- High-risk projects
- Alerts
- Ministry comparisons

### Ministry Administrator

Needs:

- Project explanations
- Delay predictions
- Cost forecasts

## Features

### MVP

- Delay prediction
- Cost overrun prediction
- Risk score
- Early warning alerts
- SHAP explanations
- Dashboard
- India risk map

### Bonus

- LLM Assistant
- Ministry benchmarking
- Sector analytics

## ML Pipeline

1. Clean data.
2. Feature engineering.
3. Train XGBoost.
4. Train LightGBM.
5. SHAP explanations.
6. Risk scoring.

## Feature Engineering

- Cost Escalation Ratio
- Financial Completion
- Project Age
- Progress Gap
- Burn Rate

## Deliverables

- Web dashboard
- FastAPI backend
- ML models
- SQLite database
- Local LLM assistant
- Documentation

## 3-Day Plan

### Day 1

- Project setup
- Data cleaning
- Feature engineering
- Delay model

### Day 2

- Cost model
- SHAP
- Dashboard

### Day 3

- LLM
- Integration
- Polish
- Demo

## Free Data Sources

### Primary

- PAIMANA Monthly Flash Reports
- PAIMANA Public Dashboard

### Secondary

- data.gov.in
- NHAI Reports
- Railway Reports
- Ministry Reports

## Success Metrics

- Delay prediction accuracy
- Cost prediction MAE
- SHAP explanations
- Dashboard response under 2 seconds
- Fully local deployment