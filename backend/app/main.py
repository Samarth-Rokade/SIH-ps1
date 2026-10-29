from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.api import alerts, analytics, assistant, dashboard, projects, reports, risk, simulator, system

app = FastAPI(title="PAIMANA Sentinel AI API", version="0.1.0")

# Any localhost / 127.0.0.1 port: Vite falls back to 5174, 5175... when 5173 is busy.
LOCAL_ORIGIN_REGEX = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"

# Radar/risk-map responses are thousands of repetitive JSON rows; gzip shrinks them ~10x.
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=LOCAL_ORIGIN_REGEX,
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = f"{field}: {first.get('msg', 'Invalid request')}" if field else first.get("msg", "Invalid request")
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": {"code": "VALIDATION_ERROR", "message": message}},
    )


app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(simulator.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend is connected!"}
