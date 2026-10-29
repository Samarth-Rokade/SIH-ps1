# PAIMANA Sentinel AI --- Complete Backend API Specification

## 1. Purpose

This document defines the backend API contract required to build the
complete PAIMANA Sentinel AI frontend.

The system is a software-only, open-source prototype for predictive
infrastructure monitoring.

### Core capabilities

-   Project delay prediction
-   Cost-overrun prediction
-   Project risk scoring
-   Early-warning alerts
-   Explainable AI / SHAP
-   Project progress and cost history
-   Ministry / sector / state analytics
-   Project benchmarking
-   What-if simulation
-   Local AI assistant
-   Report generation
-   System and model status

### Recommended backend stack

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy
-   SQLite for MVP / PostgreSQL for production
-   Pandas / NumPy
-   Scikit-learn
-   XGBoost
-   LightGBM
-   SHAP
-   Ollama + local LLM
-   ChromaDB / Sentence Transformers for optional RAG

------------------------------------------------------------------------

# 2. API Base URL

``` text
/api/v1
```

Recommended local development URL:

``` text
http://localhost:8000/api/v1
```

Swagger documentation:

``` text
/docs
```

ReDoc:

``` text
/redoc
```

------------------------------------------------------------------------

# 3. API Module Structure

``` text
/api/v1
│
├── dashboard
├── projects
├── risk
├── predictions
├── alerts
├── analytics
├── simulator
├── assistant
├── reports
└── system
```

------------------------------------------------------------------------

# 4. Common Response Format

All JSON endpoints should use a consistent response structure.

## Success

``` json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2026-04-30T12:00:00Z"
  }
}
```

## Error

``` json
{
  "success": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project with ID P1247 was not found"
  }
}
```

------------------------------------------------------------------------

# 5. Complete Endpoint List

  --------------------------------------------------------------------------------------------------------
                 \# Method        Endpoint                                    Priority      Frontend
  ----------------- ------------- ------------------------------------------- ------------- --------------
                  1 GET           `/dashboard/overview`                       P0            Command Center

                  2 GET           `/dashboard/risk-map`                       P0            Command Center

                  3 GET           `/dashboard/risk-distribution`              P0            Command Center

                  4 GET           `/dashboard/risk-trend`                     P0            Command Center

                  5 GET           `/dashboard/priority-projects`              P0            Command Center

                  6 GET           `/risk/radar`                               P0            Risk Radar

                  7 GET           `/risk/summary`                             P0            Risk Radar

                  8 GET           `/projects`                                 P0            Projects

                  9 GET           `/projects/{project_id}`                    P0            Project
                                                                                            Intelligence

                 10 GET           `/projects/{project_id}/progress`           P1            Project
                                                                                            Intelligence

                 11 GET           `/projects/{project_id}/cost-history`       P1            Project
                                                                                            Intelligence

                 12 GET           `/projects/{project_id}/timeline`           P1            Project
                                                                                            Intelligence

                 13 GET           `/projects/{project_id}/risk`               P0            Project
                                                                                            Intelligence

                 14 GET           `/projects/{project_id}/prediction/delay`   P0            Project
                                                                                            Intelligence

                 15 GET           `/projects/{project_id}/prediction/cost`    P0            Project
                                                                                            Intelligence

                 16 GET           `/projects/{project_id}/risk-drivers`       P0            Risk
                                                                                            Explanation

                 17 GET           `/alerts`                                   P0            Early Warning

                 18 GET           `/alerts/summary`                           P0            Early Warning

                 19 GET           `/alerts/{alert_id}`                        P1            Alert Details

                 20 PATCH         `/alerts/{alert_id}`                        P1            Alert
                                                                                            Management

                 21 GET           `/analytics/ministries`                     P1            Analytics

                 22 GET           `/analytics/sectors`                        P1            Analytics

                 23 GET           `/analytics/states`                         P1            Analytics

                 24 GET           `/analytics/cost`                           P1            Cost
                                                                                            Intelligence

                 25 GET           `/projects/{project_id}/benchmark`          P1            Benchmarking

                 26 POST          `/simulator/run`                            P1            What-if
                                                                                            Simulator

                 27 GET           `/simulator/{project_id}/parameters`        P1            What-if
                                                                                            Simulator

                 28 POST          `/assistant/chat`                           P1            AI Assistant

                 29 GET           `/assistant/suggestions`                    P1            AI Assistant

                 30 POST          `/reports/project/{project_id}`             P2            Reports

                 31 GET           `/reports/{report_id}/download`             P2            Reports

                 32 POST          `/reports/dashboard`                        P2            Reports

                 33 GET           `/system/status`                            P1            Header /
                                                                                            Settings

                 34 GET           `/system/data-info`                         P1            Header /
                                                                                            Settings

                 35 GET           `/system/models`                            P1            Model
                                                                                            Information
  --------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 6. COMMAND CENTER APIs

## 6.1 Dashboard Overview

### Endpoint

``` http
GET /api/v1/dashboard/overview
```

### Purpose

Returns the primary KPI cards displayed on the dashboard.

### Response

``` json
{
  "success": true,
  "data": {
    "total_projects": 1981,
    "critical_projects": 42,
    "high_risk_projects": 205,
    "medium_risk_projects": 573,
    "low_risk_projects": 1161,
    "cost_exposure_crore": 248850,
    "average_delay_risk": 31.4,
    "projects_needing_intervention": 87,
    "data_as_of": "2026-04-30"
  }
}
```

### Frontend components

-   Total Projects
-   Critical Projects
-   High Risk Projects
-   Cost Exposure
-   Average Delay Risk
-   Projects Needing Intervention

------------------------------------------------------------------------

# 7. INDIA PROJECT RISK MAP

## 7.1 Risk Map

### Endpoint

``` http
GET /api/v1/dashboard/risk-map
```

### Query parameters

``` text
?risk_level=all
```

Optional values:

``` text
all
critical
high
medium
low
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "project_id": "P1247",
      "project_name": "Mumbai Coastal Road Project",
      "state": "Maharashtra",
      "latitude": 19.076,
      "longitude": 72.8777,
      "risk_score": 94,
      "risk_level": "critical",
      "delay_probability": 0.91
    },
    {
      "project_id": "P1290",
      "project_name": "Delhi Metro Phase IV",
      "state": "Delhi",
      "latitude": 28.6139,
      "longitude": 77.209,
      "risk_score": 91,
      "risk_level": "critical",
      "delay_probability": 0.89
    }
  ]
}
```

### Frontend

Use:

-   Leaflet
-   OpenStreetMap

Clicking a marker should open a project summary.

------------------------------------------------------------------------

# 8. RISK DISTRIBUTION

## 8.1 Risk Distribution

### Endpoint

``` http
GET /api/v1/dashboard/risk-distribution
```

### Response

``` json
{
  "success": true,
  "data": {
    "total": 1981,
    "distribution": [
      {
        "level": "critical",
        "count": 42,
        "percentage": 2.12
      },
      {
        "level": "high",
        "count": 205,
        "percentage": 10.35
      },
      {
        "level": "medium",
        "count": 573,
        "percentage": 28.92
      },
      {
        "level": "low",
        "count": 1161,
        "percentage": 58.61
      }
    ]
  }
}
```

### Frontend

Use for:

-   Donut chart
-   Risk legend
-   Summary cards

------------------------------------------------------------------------

# 9. RISK TREND

## 9.1 Risk Trend

### Endpoint

``` http
GET /api/v1/dashboard/risk-trend
```

### Query

``` text
?months=6
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "month": "2025-11",
      "critical": 31,
      "high": 174,
      "medium": 521,
      "low": 1255
    },
    {
      "month": "2025-12",
      "critical": 34,
      "high": 181,
      "medium": 538,
      "low": 1228
    },
    {
      "month": "2026-01",
      "critical": 36,
      "high": 190,
      "medium": 550,
      "low": 1205
    },
    {
      "month": "2026-04",
      "critical": 42,
      "high": 205,
      "medium": 573,
      "low": 1161
    }
  ]
}
```

------------------------------------------------------------------------

# 10. TOP PRIORITY PROJECTS

## 10.1 Priority Projects

### Endpoint

``` http
GET /api/v1/dashboard/priority-projects
```

### Query

``` text
?limit=10
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "project_id": "P1247",
      "project_name": "Mumbai Coastal Road Project",
      "ministry": "Road Transport & Highways",
      "risk_score": 94,
      "risk_level": "critical",
      "predicted_delay_months": 11,
      "trend": "increasing"
    },
    {
      "project_id": "P1290",
      "project_name": "Delhi Metro Phase IV",
      "ministry": "Housing & Urban Affairs",
      "risk_score": 91,
      "risk_level": "critical",
      "predicted_delay_months": 9,
      "trend": "increasing"
    }
  ]
}
```

------------------------------------------------------------------------

# 11. RISK RADAR APIs

## 11.1 Risk Radar

### Endpoint

``` http
GET /api/v1/risk/radar
```

### Query Parameters

``` text
?ministry=
&sector=
&state=
&risk_level=
&limit=1000
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "project_id": "P1247",
      "project_name": "Mumbai Coastal Road Project",
      "risk_score": 94,
      "delay_probability": 0.91,
      "cost_risk": 0.72,
      "sector": "Road Transport",
      "state": "Maharashtra"
    },
    {
      "project_id": "P1290",
      "project_name": "Delhi Metro Phase IV",
      "risk_score": 91,
      "delay_probability": 0.89,
      "cost_risk": 0.68,
      "sector": "Urban Development",
      "state": "Delhi"
    }
  ]
}
```

------------------------------------------------------------------------

## 11.2 Risk Summary

### Endpoint

``` http
GET /api/v1/risk/summary
```

### Response

``` json
{
  "success": true,
  "data": {
    "average_risk": 48.7,
    "critical": 42,
    "high": 205,
    "medium": 573,
    "low": 1161,
    "average_delay_probability": 0.314,
    "average_cost_risk": 0.276
  }
}
```

------------------------------------------------------------------------

# 12. PROJECT APIs

## 12.1 Project List

### Endpoint

``` http
GET /api/v1/projects
```

### Query Parameters

``` text
?page=1
&page_size=20
&search=
&ministry=
&sector=
&state=
&risk_level=
&status=
&sort_by=risk_score
&sort_order=desc
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "project_id": "P1247",
      "project_name": "Mumbai Coastal Road Project",
      "ministry": "Road Transport & Highways",
      "sector": "Transport",
      "state": "Maharashtra",
      "original_cost_crore": 1200,
      "current_cost_crore": 1420,
      "physical_progress": 48,
      "risk_score": 94,
      "risk_level": "critical",
      "predicted_delay_months": 11
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 1981,
    "total_pages": 100
  }
}
```

------------------------------------------------------------------------

# 13. PROJECT DETAILS

## 13.1 Project Details

### Endpoint

``` http
GET /api/v1/projects/{project_id}
```

### Response

``` json
{
  "success": true,
  "data": {
    "project_id": "P1247",
    "project_name": "Mumbai Coastal Road Project",
    "ministry": "Road Transport & Highways",
    "sector": "Transport",
    "state": "Maharashtra",
    "original_cost_crore": 1200,
    "current_cost_crore": 1420,
    "expenditure_crore": 540,
    "physical_progress": 48,
    "start_date": "2023-01-15",
    "original_completion_date": "2026-01-31",
    "current_completion_date": "2027-03-31",
    "status": "Ongoing",
    "risk_score": 94,
    "risk_level": "critical"
  }
}
```

------------------------------------------------------------------------

# 14. PROJECT PROGRESS HISTORY

## 14.1 Progress

### Endpoint

``` http
GET /api/v1/projects/{project_id}/progress
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "month": "2025-11",
      "planned_progress": 60,
      "actual_progress": 41
    },
    {
      "month": "2025-12",
      "planned_progress": 63,
      "actual_progress": 43
    },
    {
      "month": "2026-01",
      "planned_progress": 66,
      "actual_progress": 45
    },
    {
      "month": "2026-04",
      "planned_progress": 72,
      "actual_progress": 48
    }
  ]
}
```

------------------------------------------------------------------------

# 15. PROJECT COST HISTORY

## 15.1 Cost History

### Endpoint

``` http
GET /api/v1/projects/{project_id}/cost-history
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "month": "2025-11",
      "original_cost": 1200,
      "current_cost": 1380,
      "expenditure": 470
    },
    {
      "month": "2026-04",
      "original_cost": 1200,
      "current_cost": 1420,
      "expenditure": 540
    }
  ]
}
```

------------------------------------------------------------------------

# 16. PROJECT TIMELINE

## 16.1 Timeline

### Endpoint

``` http
GET /api/v1/projects/{project_id}/timeline
```

### Response

``` json
{
  "success": true,
  "data": {
    "start_date": "2023-01-15",
    "planned_end_date": "2026-01-31",
    "predicted_end_date": "2026-12-15",
    "events": [
      {
        "name": "Project Start",
        "date": "2023-01-15",
        "status": "completed"
      },
      {
        "name": "Milestone 1",
        "date": "2024-06-30",
        "status": "completed"
      },
      {
        "name": "Milestone 2",
        "date": "2025-12-31",
        "status": "delayed"
      }
    ]
  }
}
```

------------------------------------------------------------------------

# 17. PROJECT RISK

## 17.1 Risk Details

### Endpoint

``` http
GET /api/v1/projects/{project_id}/risk
```

### Response

``` json
{
  "success": true,
  "data": {
    "risk_score": 94,
    "risk_level": "critical",
    "delay_probability": 0.91,
    "cost_overrun_probability": 0.72,
    "progress_risk": 0.87,
    "financial_risk": 0.68,
    "confidence": 0.89
  }
}
```

------------------------------------------------------------------------

# 18. DELAY PREDICTION

## 18.1 Delay Prediction

### Endpoint

``` http
GET /api/v1/projects/{project_id}/prediction/delay
```

### Response

``` json
{
  "success": true,
  "data": {
    "delay_probability": 0.91,
    "predicted_delay_months": 11,
    "prediction_range": {
      "lower": 8,
      "upper": 14
    },
    "risk_level": "critical",
    "model": "XGBoost"
  }
}
```

### Important

The frontend should present this as a model estimate, not a guaranteed
outcome.

Example:

``` text
91% predicted probability
Estimated delay: 11 months
Likely range: 8–14 months
```

------------------------------------------------------------------------

# 19. COST PREDICTION

## 19.1 Cost Prediction

### Endpoint

``` http
GET /api/v1/projects/{project_id}/prediction/cost
```

### Response

``` json
{
  "success": true,
  "data": {
    "original_cost_crore": 1200,
    "current_cost_crore": 1420,
    "predicted_final_cost_crore": 1610,
    "expected_escalation_percentage": 34.17,
    "additional_exposure_crore": 190,
    "confidence": 0.82
  }
}
```

------------------------------------------------------------------------

# 20. SHAP / RISK DRIVERS

## 20.1 Risk Drivers

### Endpoint

``` http
GET /api/v1/projects/{project_id}/risk-drivers
```

### Response

``` json
{
  "success": true,
  "data": {
    "risk_score": 94,
    "drivers": [
      {
        "feature": "Progress Gap",
        "value": 24,
        "impact": 32,
        "direction": "increases"
      },
      {
        "feature": "Low Expenditure",
        "value": 38,
        "impact": 21,
        "direction": "increases"
      },
      {
        "feature": "Milestone Slippage",
        "value": 2,
        "impact": 14,
        "direction": "increases"
      },
      {
        "feature": "Cost Escalation",
        "value": 18.3,
        "impact": 10,
        "direction": "increases"
      }
    ]
  }
}
```

### Frontend

Display as:

``` text
Progress Gap          +32
Low Expenditure       +21
Milestone Slippage    +14
Cost Escalation       +10
```

------------------------------------------------------------------------

# 21. EARLY WARNING APIs

## 21.1 Alert List

### Endpoint

``` http
GET /api/v1/alerts
```

### Query Parameters

``` text
?page=1
&page_size=20
&severity=critical
&state=
&sector=
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "alert_id": "A1001",
      "project_id": "P1247",
      "project_name": "Mumbai Coastal Road Project",
      "severity": "critical",
      "risk_score": 94,
      "alert_type": "progress_stagnation",
      "message": "Project progress has significantly slowed.",
      "detected_at": "2026-04-30"
    }
  ],
  "meta": {
    "total": 42
  }
}
```

------------------------------------------------------------------------

# 22. ALERT SUMMARY

## 22.1 Alert Summary

### Endpoint

``` http
GET /api/v1/alerts/summary
```

### Response

``` json
{
  "success": true,
  "data": {
    "critical": 42,
    "high": 125,
    "medium": 213,
    "new": 18,
    "resolved": 7
  }
}
```

------------------------------------------------------------------------

# 23. ALERT DETAILS

## 23.1 Alert Details

### Endpoint

``` http
GET /api/v1/alerts/{alert_id}
```

### Response

``` json
{
  "success": true,
  "data": {
    "alert_id": "A1001",
    "project_id": "P1247",
    "severity": "critical",
    "type": "progress_stagnation",
    "title": "Progress velocity dropped",
    "description": "Physical progress remained nearly unchanged over the latest reporting periods.",
    "detected_at": "2026-04-30",
    "risk_before": 78,
    "risk_current": 94,
    "recommended_review": "Review upcoming milestone execution."
  }
}
```

------------------------------------------------------------------------

# 24. UPDATE ALERT

## 24.1 Acknowledge / Resolve Alert

### Endpoint

``` http
PATCH /api/v1/alerts/{alert_id}
```

### Request

``` json
{
  "status": "acknowledged"
}
```

Possible statuses:

``` text
new
acknowledged
resolved
```

### Response

``` json
{
  "success": true,
  "data": {
    "alert_id": "A1001",
    "status": "acknowledged"
  }
}
```

------------------------------------------------------------------------

# 25. ANALYTICS APIs

## 25.1 Ministry Analytics

### Endpoint

``` http
GET /api/v1/analytics/ministries
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "ministry": "Road Transport & Highways",
      "projects": 342,
      "average_risk": 72,
      "high_risk_percentage": 24,
      "average_delay_months": 7.2,
      "cost_escalation_percentage": 14.8
    },
    {
      "ministry": "Railways",
      "projects": 389,
      "average_risk": 61,
      "high_risk_percentage": 18,
      "average_delay_months": 5.6,
      "cost_escalation_percentage": 11.2
    }
  ]
}
```

------------------------------------------------------------------------

# 26. SECTOR ANALYTICS

## 26.1 Sector Analytics

### Endpoint

``` http
GET /api/v1/analytics/sectors
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "sector": "Transport",
      "projects": 642,
      "average_risk": 72,
      "high_risk_percentage": 24
    },
    {
      "sector": "Railways",
      "projects": 389,
      "average_risk": 61,
      "high_risk_percentage": 18
    }
  ]
}
```

------------------------------------------------------------------------

# 27. STATE ANALYTICS

## 27.1 State Analytics

### Endpoint

``` http
GET /api/v1/analytics/states
```

### Response

``` json
{
  "success": true,
  "data": [
    {
      "state": "Maharashtra",
      "projects": 180,
      "average_risk": 62,
      "critical_projects": 8
    },
    {
      "state": "Tamil Nadu",
      "projects": 142,
      "average_risk": 57,
      "critical_projects": 5
    }
  ]
}
```

------------------------------------------------------------------------

# 28. COST ANALYTICS

## 28.1 Cost Analytics

### Endpoint

``` http
GET /api/v1/analytics/cost
```

### Query

``` text
?sector=
&ministry=
&year=
```

### Response

``` json
{
  "success": true,
  "data": {
    "total_original_cost_crore": 3713000,
    "total_current_cost_crore": 4278000,
    "total_expenditure_crore": 2036000,
    "average_escalation_percentage": 15.2,
    "projects_with_escalation": 743
  }
}
```

------------------------------------------------------------------------

# 29. PROJECT BENCHMARKING

## 29.1 Benchmark Project

### Endpoint

``` http
GET /api/v1/projects/{project_id}/benchmark
```

### Response

``` json
{
  "success": true,
  "data": {
    "project": {
      "risk": 94,
      "progress": 48,
      "expenditure_percentage": 38
    },
    "similar_projects": {
      "count": 37,
      "average_risk": 51,
      "average_progress": 61,
      "average_expenditure_percentage": 54
    },
    "comparison": {
      "risk_difference": 43,
      "progress_difference": -13,
      "expenditure_difference": -16
    }
  }
}
```

------------------------------------------------------------------------

# 30. WHAT-IF SIMULATOR

## 30.1 Simulation Parameters

### Endpoint

``` http
GET /api/v1/simulator/{project_id}/parameters
```

### Response

``` json
{
  "success": true,
  "data": {
    "physical_progress": {
      "current": 48,
      "min": 0,
      "max": 100
    },
    "expenditure_percentage": {
      "current": 38,
      "min": 0,
      "max": 100
    },
    "milestone_recovery": {
      "options": [
        "low",
        "medium",
        "high"
      ]
    }
  }
}
```

------------------------------------------------------------------------

# 31. RUN WHAT-IF SIMULATION

## 31.1 Simulation

### Endpoint

``` http
POST /api/v1/simulator/run
```

### Request

``` json
{
  "project_id": "P1247",
  "physical_progress": 55,
  "monthly_expenditure": 52,
  "milestone_recovery": "high"
}
```

### Response

``` json
{
  "success": true,
  "data": {
    "baseline": {
      "risk_score": 94,
      "delay_probability": 0.91,
      "predicted_delay_months": 11,
      "predicted_cost_crore": 1610
    },
    "simulation": {
      "risk_score": 67,
      "delay_probability": 0.68,
      "predicted_delay_months": 6,
      "predicted_cost_crore": 1530
    },
    "change": {
      "risk_reduction": 27,
      "delay_reduction_months": 5,
      "cost_reduction_crore": 80
    }
  }
}
```

### Frontend

Show:

``` text
CURRENT                 SIMULATED

Risk 94                 Risk 67
Delay 11 months         Delay 6 months
Cost ₹1610 Cr           Cost ₹1530 Cr
```

The result must be labelled as a model-based scenario simulation, not a
guaranteed outcome.

------------------------------------------------------------------------

# 32. AI ASSISTANT

## 32.1 Chat

### Endpoint

``` http
POST /api/v1/assistant/chat
```

### Request

``` json
{
  "message": "Which projects need immediate intervention?",
  "conversation_id": "conv_001"
}
```

### Response

``` json
{
  "success": true,
  "data": {
    "conversation_id": "conv_001",
    "answer": "There are 42 projects currently classified as Critical. The highest priority projects include Mumbai Coastal Road Project, Delhi Metro Phase IV and Chennai Peripheral Ring Road.",
    "sources": [
      {
        "project_id": "P1247",
        "project_name": "Mumbai Coastal Road Project"
      },
      {
        "project_id": "P1290",
        "project_name": "Delhi Metro Phase IV"
      }
    ]
  }
}
```

### Important

The LLM should not invent project statistics.

Use:

``` text
User question
    ↓
Intent detection
    ↓
Database / analytics retrieval
    ↓
Relevant project data
    ↓
Local LLM
    ↓
Grounded response
```

------------------------------------------------------------------------

# 33. AI ASSISTANT SUGGESTIONS

## 33.1 Suggested Questions

### Endpoint

``` http
GET /api/v1/assistant/suggestions
```

### Response

``` json
{
  "success": true,
  "data": [
    "Which projects need immediate intervention?",
    "Which ministry has the highest risk?",
    "Show critical projects in Maharashtra.",
    "Which projects have high cost escalation?",
    "Why is Mumbai Coastal Road Project high risk?"
  ]
}
```

------------------------------------------------------------------------

# 34. REPORT APIs

## 34.1 Generate Project Report

### Endpoint

``` http
POST /api/v1/reports/project/{project_id}
```

### Request

``` json
{
  "format": "pdf"
}
```

### Response

``` json
{
  "success": true,
  "data": {
    "report_id": "R1001",
    "status": "generated",
    "download_url": "/api/v1/reports/R1001/download"
  }
}
```

------------------------------------------------------------------------

# 35. DOWNLOAD REPORT

## 35.1 Download

### Endpoint

``` http
GET /api/v1/reports/{report_id}/download
```

Returns the generated file.

------------------------------------------------------------------------

# 36. DASHBOARD REPORT

## 36.1 Generate Dashboard Report

### Endpoint

``` http
POST /api/v1/reports/dashboard
```

### Request

``` json
{
  "month": "2026-04",
  "format": "pdf"
}
```

------------------------------------------------------------------------

# 37. SYSTEM APIs

## 37.1 System Status

### Endpoint

``` http
GET /api/v1/system/status
```

### Response

``` json
{
  "success": true,
  "data": {
    "status": "online",
    "database": "healthy",
    "ml_service": "healthy",
    "llm_service": "healthy",
    "last_data_update": "2026-04-30T18:30:00Z"
  }
}
```

Frontend uses this for:

``` text
● All Systems Online
```

------------------------------------------------------------------------

# 38. DATA INFORMATION

## 38.1 Data Status

### Endpoint

``` http
GET /api/v1/system/data-info
```

### Response

``` json
{
  "success": true,
  "data": {
    "data_as_of": "2026-04-30",
    "total_projects": 1981,
    "source": "PAIMANA / Public Government Data",
    "last_processed": "2026-04-30T18:30:00Z",
    "records_processed": 1981
  }
}
```

------------------------------------------------------------------------

# 39. MODEL INFORMATION

## 39.1 Model Status

### Endpoint

``` http
GET /api/v1/system/models
```

### Response

``` json
{
  "success": true,
  "data": {
    "delay_model": {
      "name": "XGBoost Classifier",
      "version": "1.0",
      "last_trained": "2026-04-20",
      "validation_auc": 0.84
    },
    "cost_model": {
      "name": "XGBoost Regressor",
      "version": "1.0",
      "last_trained": "2026-04-20",
      "validation_mae": 7.8
    }
  }
}
```

------------------------------------------------------------------------

# 40. FRONTEND → BACKEND MAPPING

## 40.1 Command Center

``` text
COMMAND CENTER
│
├── KPI Cards
│      └── GET /dashboard/overview
│
├── India Map
│      └── GET /dashboard/risk-map
│
├── Risk Distribution
│      └── GET /dashboard/risk-distribution
│
├── Risk Trend
│      └── GET /dashboard/risk-trend
│
└── Priority Projects
       └── GET /dashboard/priority-projects
```

------------------------------------------------------------------------

## 40.2 Risk Radar

``` text
RISK RADAR
│
├── Scatter Plot
│      └── GET /risk/radar
│
├── Summary
│      └── GET /risk/summary
│
└── Filters
       └── Query Parameters
```

------------------------------------------------------------------------

## 40.3 Project Intelligence

``` text
PROJECT INTELLIGENCE
│
├── Project Information
│      └── GET /projects/{id}
│
├── Risk Score
│      └── GET /projects/{id}/risk
│
├── Delay Prediction
│      └── GET /projects/{id}/prediction/delay
│
├── Cost Prediction
│      └── GET /projects/{id}/prediction/cost
│
├── Progress Chart
│      └── GET /projects/{id}/progress
│
├── Cost History
│      └── GET /projects/{id}/cost-history
│
├── Timeline
│      └── GET /projects/{id}/timeline
│
└── Risk Drivers
       └── GET /projects/{id}/risk-drivers
```

------------------------------------------------------------------------

## 40.4 Early Warnings

``` text
EARLY WARNINGS
│
├── Alert Summary
│      └── GET /alerts/summary
│
├── Alert List
│      └── GET /alerts
│
└── Alert Details
       └── GET /alerts/{id}
```

------------------------------------------------------------------------

## 40.5 Analytics

``` text
ANALYTICS
│
├── Ministries
│      └── GET /analytics/ministries
│
├── Sectors
│      └── GET /analytics/sectors
│
├── States
│      └── GET /analytics/states
│
└── Cost
       └── GET /analytics/cost
```

------------------------------------------------------------------------

## 40.6 What-if Simulator

``` text
WHAT-IF SIMULATOR
│
├── Parameters
│      └── GET /simulator/{id}/parameters
│
└── Simulation
       └── POST /simulator/run
```

------------------------------------------------------------------------

## 40.7 AI Assistant

``` text
AI ASSISTANT
│
├── Chat
│      └── POST /assistant/chat
│
└── Suggestions
       └── GET /assistant/suggestions
```

------------------------------------------------------------------------

# 41. RECOMMENDED BACKEND PROJECT STRUCTURE

Do not put all endpoints in one `main.py`.

``` text
backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── dashboard.py
│   │   ├── projects.py
│   │   ├── risk.py
│   │   ├── predictions.py
│   │   ├── alerts.py
│   │   ├── analytics.py
│   │   ├── simulator.py
│   │   ├── assistant.py
│   │   ├── reports.py
│   │   └── system.py
│   │
│   ├── services/
│   │   ├── dashboard_service.py
│   │   ├── project_service.py
│   │   ├── risk_service.py
│   │   ├── prediction_service.py
│   │   ├── alert_service.py
│   │   ├── analytics_service.py
│   │   ├── simulator_service.py
│   │   ├── assistant_service.py
│   │   └── report_service.py
│   │
│   ├── ml/
│   │   ├── delay_model.py
│   │   ├── cost_model.py
│   │   ├── risk_engine.py
│   │   └── shap_service.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   └── utils/
│       ├── calculations.py
│       ├── validation.py
│       └── constants.py
│
├── tests/
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

# 42. DATABASE ENTITIES

Recommended core tables:

``` text
projects
project_monthly_updates
project_milestones
project_predictions
risk_scores
risk_drivers
alerts
ministries
sectors
states
model_versions
assistant_conversations
reports
```

## Projects

Suggested fields:

``` text
id
project_id
project_name
ministry
sector
state
district
latitude
longitude
original_cost_crore
current_cost_crore
expenditure_crore
physical_progress
start_date
original_completion_date
current_completion_date
status
created_at
updated_at
```

## Monthly Updates

``` text
id
project_id
reporting_month
planned_progress
actual_progress
expenditure_crore
current_cost_crore
milestone_status
created_at
```

------------------------------------------------------------------------

# 43. ML SERVICE FLOW

``` text
Project Data
     ↓
Data Validation
     ↓
Feature Engineering
     ↓
Delay Model
     ↓
Cost Model
     ↓
Risk Engine
     ↓
SHAP Explanation
     ↓
Prediction Database
     ↓
FastAPI
     ↓
Frontend
```

------------------------------------------------------------------------

# 44. IMPORTANT FEATURE ENGINEERING

The backend should calculate derived features rather than relying only
on raw fields.

## Cost Escalation

``` text
current_cost / original_cost
```

## Financial Completion

``` text
expenditure / current_cost
```

## Project Age

``` text
current_date - start_date
```

## Progress Gap

``` text
expected_progress - actual_progress
```

## Burn Rate

``` text
expenditure / project_age
```

## Schedule Slippage

``` text
current_completion_date - original_completion_date
```

------------------------------------------------------------------------

# 45. RISK SCORE

For the MVP, use a configurable formula:

``` text
Risk Score =
    0.50 × Delay Risk
  + 0.25 × Cost Risk
  + 0.15 × Progress Risk
  + 0.10 × Financial Risk
```

Risk levels:

``` text
0–30    Low
31–60   Medium
61–80   High
81–100  Critical
```

These weights are prototype decision-support weights and should not be
represented as official MoSPI weights.

------------------------------------------------------------------------

# 46. P0 IMPLEMENTATION SET

For the first working prototype, implement these endpoints first.

``` text
GET /dashboard/overview

GET /dashboard/risk-map

GET /dashboard/risk-distribution

GET /dashboard/risk-trend

GET /dashboard/priority-projects

GET /risk/radar

GET /risk/summary

GET /projects

GET /projects/{id}

GET /projects/{id}/risk

GET /projects/{id}/prediction/delay

GET /projects/{id}/prediction/cost

GET /projects/{id}/risk-drivers

GET /alerts

GET /alerts/summary
```

These endpoints are enough for the main dashboard, risk radar, project
intelligence and early-warning experience.

------------------------------------------------------------------------

# 47. P1 IMPLEMENTATION SET

Implement next:

``` text
GET /projects/{id}/progress

GET /projects/{id}/cost-history

GET /projects/{id}/timeline

GET /alerts/{id}

PATCH /alerts/{id}

GET /analytics/ministries

GET /analytics/sectors

GET /analytics/states

GET /analytics/cost

GET /projects/{id}/benchmark

GET /simulator/{id}/parameters

POST /simulator/run

POST /assistant/chat

GET /assistant/suggestions

GET /system/status

GET /system/data-info

GET /system/models
```

------------------------------------------------------------------------

# 48. P2 IMPLEMENTATION SET

Implement if time permits:

``` text
POST /reports/project/{id}

GET /reports/{report_id}/download

POST /reports/dashboard
```

------------------------------------------------------------------------

# 49. THREE-DAY BACKEND DEVELOPMENT PLAN

## DAY 1 --- Data + ML + Core APIs

### Step 1

Set up:

``` text
FastAPI
SQLite
Pandas
NumPy
Scikit-learn
XGBoost
SHAP
```

### Step 2

Create project database.

### Step 3

Load PAIMANA-compatible dataset.

### Step 4

Create derived features.

### Step 5

Train:

``` text
Delay Classifier
Delay Regressor
Cost Regressor
```

### Step 6

Build:

``` text
/dashboard/overview
/dashboard/risk-map
/dashboard/risk-distribution
/dashboard/risk-trend
/dashboard/priority-projects
```

### Step 7

Build:

``` text
/projects
/projects/{id}
/projects/{id}/risk
/projects/{id}/prediction/delay
/projects/{id}/prediction/cost
/projects/{id}/risk-drivers
```

### Day 1 deliverable

A working FastAPI backend with real prediction responses.

------------------------------------------------------------------------

# 50. DAY 2 --- Alerts + Analytics

Implement:

``` text
/risk/radar
/risk/summary

/alerts
/alerts/summary
/alerts/{id}

/projects/{id}/progress
/projects/{id}/cost-history
/projects/{id}/timeline

/analytics/ministries
/analytics/sectors
/analytics/states
/analytics/cost
```

### Day 2 deliverable

Complete backend for:

-   Dashboard
-   Risk Radar
-   Project Intelligence
-   Early Warning Center
-   Analytics

------------------------------------------------------------------------

# 51. DAY 3 --- USP FEATURES

Implement:

``` text
/simulator/{id}/parameters
/simulator/run

/assistant/chat
/assistant/suggestions

/system/status
/system/data-info
/system/models
```

Then add:

-   Ollama
-   Local LLM
-   RAG if time permits
-   Report generation if time permits

### Day 3 deliverable

Complete end-to-end prototype.

------------------------------------------------------------------------

# 52. FRONTEND ROUTES

Recommended routes:

``` text
/dashboard

/risk-radar

/projects

/projects/:id

/early-warnings

/simulator

/assistant
```

Risk explanation should be part of:

``` text
/projects/:id
```

rather than a separate page.

------------------------------------------------------------------------

# 53. FRONTEND DATA FLOW

``` text
React Page
    ↓
API Service
    ↓
Axios / Fetch
    ↓
FastAPI
    ↓
Service Layer
    ↓
Database / ML Engine
    ↓
JSON Response
    ↓
React State
    ↓
Chart / Table / Card
```

The frontend should not contain ML logic.

Do NOT hardcode:

``` javascript
const risk = 94;
```

Instead:

``` javascript
const response = await api.get(
  `/projects/${projectId}/risk`
);

const risk = response.data.data.risk_score;
```

------------------------------------------------------------------------

# 54. API DESIGN RULES

## Rule 1 --- Consistent JSON

All endpoints should use the common success/error structure.

## Rule 2 --- Pagination

Large datasets such as projects and alerts must be paginated.

## Rule 3 --- Filters

Use query parameters for filtering.

## Rule 4 --- IDs

Use stable `project_id` values.

## Rule 5 --- Dates

Use ISO 8601:

``` text
2026-04-30
```

or:

``` text
2026-04-30T18:30:00Z
```

## Rule 6 --- Percentages

Return percentages as numbers when useful:

``` text
48.5
```

Probabilities should be returned as decimals:

``` text
0.91
```

## Rule 7 --- Currency

Use crore values consistently:

``` text
1200
```

meaning:

``` text
₹1,200 crore
```

## Rule 8 --- Explainability

Every ML prediction should be accompanied by interpretable drivers where
possible.

------------------------------------------------------------------------

# 55. FINAL SYSTEM ARCHITECTURE

``` text
                    DATA SOURCES
                         │
              ┌──────────┴──────────┐
              │                     │
        PAIMANA Reports        OGD Data
              │                     │
              └──────────┬──────────┘
                         ↓
                  DATA INGESTION
                         ↓
                 DATA PROCESSING
                  Pandas / NumPy
                         ↓
                FEATURE ENGINEERING
                         ↓
              ┌──────────┴──────────┐
              │                     │
         ML PIPELINE            ANALYTICS
              │                     │
       ┌──────┴──────┐              │
       │             │              │
     Delay          Cost       Trends / Benchmarks
     Model          Model            │
       │             │              │
       └──────┬──────┘              │
              ↓                     │
           RISK ENGINE ←────────────┘
              │
       ┌──────┼─────────┐
       │      │         │
       ↓      ↓         ↓
     SHAP   ALERTS   BENCHMARK
       │      │         │
       └──────┼─────────┘
              ↓
        DECISION SUPPORT
              │
       ┌──────┴─────────┐
       │                │
       ↓                ↓
 WHAT-IF ENGINE      LLM/RAG
       │                │
       └──────┬─────────┘
              ↓
        FASTAPI BACKEND
              ↓
        REACT FRONTEND
```

------------------------------------------------------------------------

# 56. JUDGE DEMO API FLOW

The demo should follow this sequence:

``` text
GET /dashboard/overview
        ↓
GET /dashboard/risk-map
        ↓
GET /dashboard/priority-projects
        ↓
GET /projects/P1247
        ↓
GET /projects/P1247/risk
        ↓
GET /projects/P1247/prediction/delay
        ↓
GET /projects/P1247/prediction/cost
        ↓
GET /projects/P1247/risk-drivers
        ↓
GET /alerts
        ↓
POST /simulator/run
        ↓
POST /assistant/chat
```

This demonstrates:

``` text
MONITOR
   ↓
DETECT
   ↓
PREDICT
   ↓
EXPLAIN
   ↓
ALERT
   ↓
SIMULATE
   ↓
ASSIST
```

------------------------------------------------------------------------

# 57. Definition of Done

The backend is considered MVP-complete when:

-   [ ] FastAPI starts successfully
-   [ ] Swagger documentation works
-   [ ] Database loads project data
-   [ ] `/dashboard/overview` returns real data
-   [ ] Project list supports filters and pagination
-   [ ] Individual project details work
-   [ ] Delay prediction works
-   [ ] Cost prediction works
-   [ ] Risk score works
-   [ ] SHAP risk drivers work
-   [ ] Risk radar works
-   [ ] Alerts work
-   [ ] Ministry analytics work
-   [ ] What-if simulator works
-   [ ] AI assistant works locally or through a mocked provider
-   [ ] Frontend can consume every P0 endpoint
-   [ ] No important dashboard values are hardcoded
-   [ ] All prediction outputs are labelled as model estimates
-   [ ] API error handling works
-   [ ] README contains setup instructions

------------------------------------------------------------------------

# 58. Recommended Implementation Order

Do not implement endpoints randomly.

Use this order:

``` text
1. Database
      ↓
2. Data loading
      ↓
3. Feature engineering
      ↓
4. ML models
      ↓
5. Risk engine
      ↓
6. Dashboard APIs
      ↓
7. Project APIs
      ↓
8. Alert APIs
      ↓
9. Analytics APIs
      ↓
10. What-if simulator
      ↓
11. AI assistant
      ↓
12. Reports
```

The core product should work even if the LLM and report-generation
modules are temporarily disabled.

------------------------------------------------------------------------

# 59. Claude/Cursor Implementation Prompt

Use this document as the backend contract and give the following
instruction to the coding agent:

``` text
Read this entire API specification before writing code.

Build the PAIMANA Sentinel AI backend using:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite for MVP
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- SHAP

Requirements:

1. Follow the endpoint paths and response schemas in this document.
2. Use a clean layered architecture:
   API → Services → Database / ML.
3. Do not put business logic inside route handlers.
4. Create Pydantic schemas for request and response validation.
5. Create SQLAlchemy database models.
6. Create seed/demo data that follows the documented schema.
7. Create working ML prediction services.
8. Implement the P0 endpoints first.
9. Add unit tests for core services.
10. Enable Swagger documentation.
11. Add CORS for the React frontend.
12. Use environment variables for configuration.
13. Do not hardcode frontend-specific values into the API.
14. Return consistent success/error JSON.
15. Use model estimates and clearly expose confidence/ranges where appropriate.
16. Never fabricate official PAIMANA statistics. Demo/synthetic data must be clearly marked.
17. Keep the application runnable completely offline except for optional external data ingestion.
18. Do not require paid APIs.

Implement the project phase-by-phase.

Start with:
PHASE 1 — database + models + seed data + FastAPI setup.

After completing each phase, verify that the application runs before moving to the next phase.
```

------------------------------------------------------------------------

# 60. Priority Summary

For a 3-day SIH prototype:

### Must work

``` text
Dashboard
     ↓
Risk Radar
     ↓
Project Intelligence
     ↓
Early Warnings
     ↓
ML Predictions
     ↓
SHAP Explanations
```

### Strong differentiator

``` text
What-if Simulator
```

### Bonus

``` text
Local LLM Assistant
RAG
Reports
```

The central technical story should remain:

> **PAIMANA data → feature engineering → ML prediction → risk scoring →
> explainability → early warning → decision support.**
