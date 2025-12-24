"""Pydantic schemas for AITask model.

Schemas define the structure of API requests and responses for AI tasks.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.ai_task import TaskStatus, TaskType


class AITaskBase(BaseModel):
    """Base schema with common AI task fields."""
    
    task_type: TaskType = Field(..., description="Type of AI task")
    input_data: Dict[str, Any] = Field(..., description="Input parameters as JSON")
    prompt: Optional[str] = Field(None, description="AI prompt used")
    requires_approval: bool = Field(True, description="Whether task requires approval")


class AITaskCreate(AITaskBase):
    """Schema for creating an AI task.
    
    Used for POST requests to initiate AI operations.
    """
    
    created_by: UUID = Field(..., description="User ID who created the task")


class AITaskUpdate(BaseModel):
    """Schema for updating an AI task.
    
    Used for PUT/PATCH requests. All fields are optional for partial updates.
    """
    
    status: Optional[TaskStatus] = Field(None, description="Task status")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Generated output")
    model_used: Optional[str] = Field(None, description="AI model name")
    tokens_used: Optional[int] = Field(None, ge=0, description="Tokens consumed")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    approved: Optional[bool] = Field(None, description="Approval status")
    approved_by: Optional[UUID] = Field(None, description="User who approved")


class AITaskResponse(AITaskBase):
    """Schema for AI task responses.
    
    Used for GET requests. Includes all database fields.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: TaskStatus
    output_data: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    approved: bool
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class AITaskListResponse(BaseModel):
    """Schema for paginated AI task list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_type: TaskType
    status: TaskStatus
    requires_approval: bool
    approved: bool
    created_by: UUID
    created_at: datetime


class AITaskApproval(BaseModel):
    """Schema for approving/rejecting an AI task."""
    
    approved: bool = Field(..., description="Approval decision")
    approved_by: UUID = Field(..., description="User ID performing approval")
