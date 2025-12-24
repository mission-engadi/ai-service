"""AI Tasks API endpoints.

Provides operations for managing AI tasks.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.models.ai_task import TaskStatus, TaskType
from app.schemas.ai_task import AITaskResponse, AITaskListResponse
from app.services.ai_task_service import AITaskService

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response schemas

class TaskApprovalRequest(BaseModel):
    """Request to approve/reject a task."""
    approved: bool
    reason: Optional[str] = None


class TaskStatisticsResponse(BaseModel):
    """Task statistics response."""
    total_tasks: int
    by_status: dict
    by_type: dict


# Endpoints

@router.get(
    "/tasks/{task_id}",
    response_model=AITaskResponse,
    summary="Get task",
    description="Retrieve details of a specific AI task",
)
async def get_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI task by ID."""
    task = await AITaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.get(
    "/tasks",
    response_model=List[AITaskListResponse],
    summary="List tasks",
    description="List AI tasks with optional filters",
)
async def list_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    task_type: Optional[TaskType] = Query(None, description="Filter by task type"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List AI tasks."""
    tasks = await AITaskService.list_tasks(
        db=db,
        skip=skip,
        limit=limit,
        task_type=task_type,
        status=status,
        created_by=UUID(str(user.user_id)),
    )
    return tasks


@router.post(
    "/tasks/{task_id}/approve",
    response_model=AITaskResponse,
    summary="Approve task",
    description="Approve an AI task output",
)
async def approve_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve an AI task."""
    task = await AITaskService.approve_task(
        db=db,
        task_id=task_id,
        approved_by=UUID(str(user.user_id)),
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.post(
    "/tasks/{task_id}/reject",
    response_model=AITaskResponse,
    summary="Reject task",
    description="Reject an AI task output",
)
async def reject_task(
    task_id: UUID,
    request: TaskApprovalRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject an AI task."""
    task = await AITaskService.reject_task(
        db=db,
        task_id=task_id,
        rejected_by=UUID(str(user.user_id)),
        reason=request.reason,
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete an AI task",
)
async def delete_task(
    task_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an AI task."""
    deleted = await AITaskService.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )


@router.get(
    "/tasks/statistics",
    response_model=TaskStatisticsResponse,
    summary="Get task statistics",
    description="Retrieve AI task statistics",
)
async def get_task_statistics(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get task statistics."""
    stats = await AITaskService.get_task_statistics(
        db=db,
        created_by=UUID(str(user.user_id)),
    )
    return stats
