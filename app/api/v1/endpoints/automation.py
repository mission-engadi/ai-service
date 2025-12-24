"""Automation API endpoints.

Provides automated content generation workflows.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.services.automation_service import AutomationService

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response schemas

class WorkflowCreateRequest(BaseModel):
    """Request to create an automation workflow."""
    name: str = Field(..., min_length=1, description="Workflow name")
    workflow_type: str = Field(..., description="Workflow type (auto_translate, scheduled_post, etc.)")
    config: dict = Field(..., description="Workflow configuration")
    schedule: Optional[str] = Field(None, description="Cron schedule")


class WorkflowUpdateRequest(BaseModel):
    """Request to update a workflow."""
    name: Optional[str] = Field(None, description="Workflow name")
    config: Optional[dict] = Field(None, description="Workflow configuration")
    schedule: Optional[str] = Field(None, description="Cron schedule")
    is_active: Optional[bool] = Field(None, description="Active status")


class WorkflowTriggerRequest(BaseModel):
    """Request to trigger a workflow."""
    trigger_data: Optional[dict] = Field(None, description="Additional trigger data")


class WorkflowResponse(BaseModel):
    """Workflow response."""
    workflow_id: str
    name: str
    workflow_type: str
    config: dict
    schedule: Optional[str]
    is_active: bool
    created_by: str
    created_at: str


class WorkflowListResponse(BaseModel):
    """Workflow list item."""
    workflow_id: str
    name: str
    workflow_type: str
    is_active: bool
    created_at: str


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response."""
    execution_id: str
    workflow_id: str
    started_at: str
    completed_at: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


# Endpoints

@router.post(
    "/automation/workflows",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workflow",
    description="Create an automation workflow",
)
async def create_workflow(
    request: WorkflowCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an automation workflow."""
    try:
        result = await AutomationService.create_workflow(
            db=db,
            name=request.name,
            workflow_type=request.workflow_type,
            config=request.config,
            schedule=request.schedule,
            created_by=UUID(str(user.user_id)),
        )
        return result
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}",
        )


@router.get(
    "/automation/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow",
    description="Retrieve workflow details",
)
async def get_workflow(
    workflow_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workflow by ID."""
    result = await AutomationService.get_workflow(workflow_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    return result


@router.get(
    "/automation/workflows",
    response_model=List[WorkflowListResponse],
    summary="List workflows",
    description="List all automation workflows",
)
async def list_workflows(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workflows."""
    results = await AutomationService.list_workflows(
        created_by=UUID(str(user.user_id)),
    )
    return results


@router.put(
    "/automation/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Update workflow",
    description="Update an existing workflow",
)
async def update_workflow(
    workflow_id: UUID,
    request: WorkflowUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a workflow."""
    try:
        result = await AutomationService.update_workflow(
            workflow_id=workflow_id,
            name=request.name,
            config=request.config,
            schedule=request.schedule,
            is_active=request.is_active,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}",
        )


@router.delete(
    "/automation/workflows/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow",
    description="Delete an automation workflow",
)
async def delete_workflow(
    workflow_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a workflow."""
    deleted = await AutomationService.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )


@router.post(
    "/automation/workflows/{workflow_id}/trigger",
    response_model=WorkflowExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger workflow",
    description="Manually trigger a workflow execution",
)
async def trigger_workflow(
    workflow_id: UUID,
    request: WorkflowTriggerRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a workflow execution."""
    try:
        result = await AutomationService.trigger_workflow(
            db=db,
            workflow_id=workflow_id,
            trigger_data=request.trigger_data,
            created_by=UUID(str(user.user_id)),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error triggering workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger workflow: {str(e)}",
        )


@router.get(
    "/automation/workflows/{workflow_id}/history",
    response_model=List[WorkflowExecutionResponse],
    summary="Get workflow history",
    description="Retrieve execution history for a workflow",
)
async def get_workflow_history(
    workflow_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workflow execution history."""
    history = await AutomationService.get_workflow_history(
        workflow_id=workflow_id,
        limit=limit,
    )
    return history
