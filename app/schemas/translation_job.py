"""Pydantic schemas for TranslationJob model.

Schemas define the structure of API requests and responses for translation jobs.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.translation_job import TranslationStatus


class TranslationJobBase(BaseModel):
    """Base schema with common translation job fields."""
    
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")
    source_text: str = Field(..., min_length=1, description="Text to translate")


class TranslationJobCreate(TranslationJobBase):
    """Schema for creating a translation job.
    
    Used for POST requests.
    """
    
    task_id: UUID = Field(..., description="Reference to AI task")


class TranslationJobUpdate(BaseModel):
    """Schema for updating a translation job.
    
    Used for PUT/PATCH requests. All fields are optional for partial updates.
    """
    
    translated_text: Optional[str] = Field(None, min_length=1)
    status: Optional[TranslationStatus] = None
    quality_score: Optional[float] = Field(None, ge=0, le=1)
    error_message: Optional[str] = None


class TranslationJobResponse(TranslationJobBase):
    """Schema for translation job responses.
    
    Used for GET requests. Includes all database fields.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    translated_text: Optional[str] = None
    status: TranslationStatus
    quality_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TranslationJobListResponse(BaseModel):
    """Schema for paginated translation job list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    source_language: str
    target_language: str
    status: TranslationStatus
    created_at: datetime


class TranslationRequest(BaseModel):
    """Schema for requesting content translation."""
    
    source_text: str = Field(..., min_length=1, description="Text to translate")
    source_language: str = Field(..., description="Source language code")
    target_languages: list[str] = Field(..., min_items=1, description="Target language codes")
    created_by: UUID = Field(..., description="User requesting translation")
