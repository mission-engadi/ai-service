"""Pydantic schemas for GeneratedContent model.

Schemas define the structure of API requests and responses for AI-generated content.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.generated_content import ContentType


class GeneratedContentBase(BaseModel):
    """Base schema with common generated content fields."""
    
    content_type: ContentType = Field(..., description="Type of content")
    title: Optional[str] = Field(None, max_length=500, description="Content title")
    body: str = Field(..., min_length=1, description="Main content body")
    language: str = Field("en", description="Content language (en, es, fr, pt)")
    platform: Optional[str] = Field(None, max_length=50, description="Target platform")
    content_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class GeneratedContentCreate(GeneratedContentBase):
    """Schema for creating generated content.
    
    Used for POST requests.
    """
    
    task_id: UUID = Field(..., description="Reference to AI task")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Quality score")


class GeneratedContentUpdate(BaseModel):
    """Schema for updating generated content.
    
    Used for PUT/PATCH requests. All fields are optional for partial updates.
    """
    
    title: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    content_metadata: Optional[Dict[str, Any]] = None
    published: Optional[bool] = None
    external_id: Optional[UUID] = None


class GeneratedContentResponse(GeneratedContentBase):
    """Schema for generated content responses.
    
    Used for GET requests. Includes all database fields.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    quality_score: Optional[float] = None
    published: bool
    published_at: Optional[datetime] = None
    external_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class GeneratedContentListResponse(BaseModel):
    """Schema for paginated generated content list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    content_type: ContentType
    title: Optional[str] = None
    language: str
    platform: Optional[str] = None
    published: bool
    created_at: datetime


class GeneratedContentPublish(BaseModel):
    """Schema for publishing generated content."""
    
    published: bool = Field(..., description="Publication status")
    external_id: Optional[UUID] = Field(None, description="External system ID")
