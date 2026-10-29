from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException

from app.api import alerts, dashboard, projects, risk

app = FastAPI(title="PAIMANA Sentinel AI API", version="0.1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # ApiError (app/utils/response.py) already builds the documented
    # {success:false, error:{code,message}} body as `detail`; pass it through
    # instead of letting FastAPI wrap it in {"detail": ...}.
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": "HTTP_ERROR", "message": str(exc.detail)}},
    )


app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend is connected!"}
