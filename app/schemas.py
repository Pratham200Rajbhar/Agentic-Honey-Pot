"""
Pydantic schemas for request/response validation
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import uuid


class RequestMetadata(BaseModel):
    """Optional metadata for the request."""

    source: Optional[str] = None
    timestamp: Optional[str] = None


class ScamRequest(BaseModel):
    """Request schema for honeypot analysis."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The message to analyze (1-5000 characters)",
    )
    metadata: Optional[RequestMetadata] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate and clean message input."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v


class ExtractedEntities(BaseModel):
    """Extracted entities from the message."""

    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)


class ScamResponse(BaseModel):
    """Response schema for honeypot analysis."""

    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scam_type: str
    threat_level: str = Field(..., pattern="^(Low|Medium|High)$")
    threat_score: int = Field(..., ge=0, le=100)
    intent: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    language: str
    extracted_entities: ExtractedEntities


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status_code: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "2.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""

    name: str = Field(
        ..., min_length=1, max_length=50, description="Friendly name for the API key"
    )


class ApiKeyResponse(BaseModel):
    """Schema for API key response."""

    id: str
    name: str
    prefix: str
    key: Optional[str] = None  # Only returned once on creation
    created_at: datetime
    last_used: Optional[datetime] = None


class UserCreate(BaseModel):
    """Schema for user creation."""

    username: str
    email: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    username: str
    email: str
    created_at: datetime
