"""Pydantic schemas for ContentTemplate model.

Schemas define the structure of API requests and responses for content templates.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContentTemplateBase(BaseModel):
    """Base schema with common content template fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    template_type: str = Field(..., description="Type of content this generates")
    description: Optional[str] = Field(None, description="Template description")
    prompt_template: str = Field(..., min_length=1, description="Template with variables")
    variables: List[str] = Field(default_factory=list, description="List of variables")
    language: str = Field("en", description="Template language (en, es, fr, pt)")
    platform: Optional[str] = Field(None, max_length=50, description="Target platform")
    is_active: bool = Field(True, description="Whether template is active")


class ContentTemplateCreate(ContentTemplateBase):
    """Schema for creating a content template.
    
    Used for POST requests.
    """
    
    created_by: UUID = Field(..., description="User ID who created the template")


class ContentTemplateUpdate(BaseModel):
    """Schema for updating a content template.
    
    Used for PUT/PATCH requests. All fields are optional for partial updates.
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    prompt_template: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None
    language: Optional[str] = None
    platform: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ContentTemplateResponse(ContentTemplateBase):
    """Schema for content template responses.
    
    Used for GET requests. Includes all database fields.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    usage_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ContentTemplateListResponse(BaseModel):
    """Schema for paginated content template list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    template_type: str
    language: str
    is_active: bool
    usage_count: int
    created_at: datetime


class ContentTemplateGenerate(BaseModel):
    """Schema for generating content from a template."""
    
    template_id: UUID = Field(..., description="Template to use")
    variable_values: dict = Field(..., description="Values for template variables")
    created_by: UUID = Field(..., description="User generating the content")
