"""
Agentic Honey-Pot: Scam Intelligence Extraction API
Main FastAPI Application
"""

import logging
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .schemas import (
    ScamRequest,
    ScamResponse,
    ErrorResponse,
    HealthResponse,
    ApiKeyCreate,
    ApiKeyResponse,
)
from .auth import verify_api_key, hash_api_key
from .config import get_settings
from .orchestrator import get_orchestrator
from .db import db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting Agentic Honey-Pot API...")
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log level: {settings.log_level}")

    # Pre-initialize orchestrator
    _ = get_orchestrator()
    logger.info("Orchestrator initialized")

    # Connect to database
    await db.connect()

    yield

    # Shutdown
    logger.info("Shutting down Agentic Honey-Pot API...")
    await db.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="Scam Intelligence Extraction API with Multi-Agent Analysis Pipeline",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurable for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Root endpoint - Serve the Web Interface
@app.get("/", tags=["UI"])
async def root():
    """Serve the web interface."""
    return FileResponse("app/static/index.html")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail, analysis_id=str(uuid.uuid4()), status_code=exc.status_code
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error. Please try again later.",
            analysis_id=str(uuid.uuid4()),
            status_code=500,
        ).model_dump(),
    )


# Health check endpoint (no authentication required)
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and healthy",
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy", version="2.0.0", timestamp=datetime.utcnow().isoformat()
    )


# API Information endpoint
@app.get(
    "/api/info",
    tags=["Info"],
    summary="API Information",
    description="Get basic API information",
)
async def api_info():
    """Endpoint with API information."""
    return {
        "name": "Agentic Honey-Pot API",
        "version": "2.0.0",
        "description": "Scam Intelligence Extraction API",
        "documentation": "/docs",
    }


# Main analysis endpoint
@app.post(
    "/api/honeypot",
    response_model=ScamResponse,
    tags=["Analysis"],
    summary="Analyze Message",
    description="Analyze a message for scam/spam indicators and extract threat intelligence",
    responses={
        200: {"description": "Successful analysis", "model": ScamResponse},
        400: {"description": "Invalid request", "model": ErrorResponse},
        401: {"description": "Authentication failed", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def analyze_message(request: ScamRequest, api_key: str = Depends(verify_api_key)):
    """
    Analyze a message for scam/spam indicators.

    This endpoint accepts a message and runs it through a multi-agent
    analysis pipeline to extract threat intelligence including:

    - **Scam Type**: Classification into 10 scam categories
    - **Threat Level**: Low, Medium, or High
    - **Threat Score**: 0-100 quantified threat level
    - **Intent**: Inferred attacker motivation
    - **Confidence Score**: Model certainty (0.0-1.0)
    - **Language**: Detected message language
    - **Extracted Entities**: URLs, emails, phones, monetary amounts
    """
    logger.info(f"Received analysis request, message length: {len(request.message)}")

    try:
        # Get orchestrator and run analysis
        orchestrator = get_orchestrator()
        response = orchestrator.analyze(request.message)

        logger.info(
            f"Analysis complete: {response.scam_type}, "
            f"threat_score={response.threat_score}, "
            f"confidence={response.confidence_score}"
        )

        return response

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Analysis failed. Please try again later."
        )


# Alternative endpoint path for compatibility
@app.post(
    "/analyze",
    response_model=ScamResponse,
    tags=["Analysis"],
    summary="Analyze Message (Alternative)",
    description="Alternative endpoint for message analysis",
    include_in_schema=True,
)
async def analyze_message_alt(
    request: ScamRequest, api_key: str = Depends(verify_api_key)
):
    """Alternative analysis endpoint."""
    return await analyze_message(request, api_key)


# --- API Key Management Endpoints ---


@app.post(
    "/api/keys",
    response_model=ApiKeyResponse,
    tags=["API Keys"],
    summary="Create API Key",
)
async def create_api_key(
    request: ApiKeyCreate,
    api_key: str = Depends(
        verify_api_key
    ),  # Requires valid key to create new ones (or we could use a different auth)
):
    """Generate a new API key."""
    # For now, we assume a default user for the GUI hackathon context if not implemented fully
    # In a real app, we'd get the user from the current session/token
    user = await db.client.user.find_first()
    if not user:
        user = await db.client.user.create(
            data={"username": "default_user", "email": "user@example.com"}
        )

    raw_key = f"hp_{uuid.uuid4().hex}"
    hashed_key = hash_api_key(raw_key)
    prefix = raw_key[:11]  # hp_ + 8 chars

    new_key = await db.client.apikey.create(
        data={
            "name": request.name,
            "hashed_key": hashed_key,
            "prefix": prefix,
            "userId": user.id,
        }
    )

    return ApiKeyResponse(
        id=new_key.id,
        name=new_key.name,
        prefix=new_key.prefix,
        key=raw_key,  # Returned ONLY once
        created_at=new_key.created_at,
        last_used=new_key.last_used,
    )


@app.get(
    "/api/keys",
    response_model=List[ApiKeyResponse],
    tags=["API Keys"],
    summary="List API Keys",
)
async def list_api_keys(api_key: str = Depends(verify_api_key)):
    """List all API keys for the current user."""
    keys = await db.client.apikey.find_many(order={"created_at": "desc"})
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            prefix=k.prefix,
            created_at=k.created_at,
            last_used=k.last_used,
        )
        for k in keys
    ]


@app.delete(
    "/api/keys/{key_id}",
    tags=["API Keys"],
    summary="Delete API Key",
)
async def delete_api_key(key_id: str, api_key: str = Depends(verify_api_key)):
    """Delete an API key."""
    try:
        await db.client.apikey.delete(where={"id": key_id})
        return {"status": "success", "message": "API key deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="API key not found")


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=settings.port, reload=settings.debug
    )
