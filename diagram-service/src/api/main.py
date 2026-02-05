from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
from pathlib import Path

from src.core.config import settings
from src.core.logger import app_logger
from src.core.exceptions import DiagramServiceException
from src.api.routes import analyze, generate, mock_data
from src.api.models.responses import HealthResponse, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    app_logger.info(f"Device: {settings.device}")
    app_logger.info(f"Debug mode: {settings.debug}")
    yield
    app_logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ML-сервис для двухстороннего преобразования диаграмм",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    app_logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    app_logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.3f}s"
    )
    
    return response


@app.exception_handler(DiagramServiceException)
async def diagram_service_exception_handler(request: Request, exc: DiagramServiceException):
    app_logger.error(f"DiagramServiceException: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    app_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(exc)} if settings.debug else {}
        ).model_dump()
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        device=settings.device,
        models_loaded=True
    )


@app.get("/", tags=["Root"])
async def root():
    from fastapi.responses import FileResponse
    static_dir = Path(__file__).parent.parent.parent / "static"
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


app.include_router(analyze.router, prefix=settings.api_prefix, tags=["Analyze"])
app.include_router(generate.router, prefix=settings.api_prefix, tags=["Generate"])
app.include_router(mock_data.router, prefix=settings.api_prefix, tags=["Mock Demo"])
