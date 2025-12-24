"""AI Task Service.

Provides CRUD operations and business logic for AI tasks.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_task import AITask, TaskStatus, TaskType
from app.schemas.ai_task import AITaskCreate, AITaskUpdate

logger = logging.getLogger(__name__)


class AITaskService:
    """Service for AI task operations."""
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_data: AITaskCreate,
        created_by: UUID,
    ) -> AITask:
        """Create a new AI task.
        
        Args:
            db: Database session
            task_data: Task creation data
            created_by: User ID creating the task
            
        Returns:
            Created AI task
        """
        task = AITask(
            task_type=task_data.task_type,
            status=TaskStatus.PENDING,
            input_data=task_data.input_data,
            prompt=task_data.prompt,
            requires_approval=task_data.requires_approval,
            created_by=created_by,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        logger.info(f"Created AI task {task.id} of type {task.task_type}")
        return task
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: UUID) -> Optional[AITask]:
        """Get AI task by ID.
        
        Args:
            db: Database session
            task_id: Task UUID
            
        Returns:
            AI task or None if not found
        """
        result = await db.execute(select(AITask).where(AITask.id == task_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        created_by: Optional[UUID] = None,
    ) -> List[AITask]:
        """List AI tasks with filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            task_type: Filter by task type
            status: Filter by status
            created_by: Filter by creator
            
        Returns:
            List of AI tasks
        """
        query = select(AITask)
        
        if task_type:
            query = query.where(AITask.task_type == task_type)
        if status:
            query = query.where(AITask.status == status)
        if created_by:
            query = query.where(AITask.created_by == created_by)
        
        query = query.offset(skip).limit(limit).order_by(AITask.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: UUID,
        task_data: AITaskUpdate,
    ) -> Optional[AITask]:
        """Update an AI task.
        
        Args:
            db: Database session
            task_id: Task UUID
            task_data: Task update data
            
        Returns:
            Updated task or None if not found
        """
        task = await AITaskService.get_task(db, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def approve_task(
        db: AsyncSession,
        task_id: UUID,
        approved_by: UUID,
    ) -> Optional[AITask]:
        """Approve an AI task.
        
        Args:
            db: Database session
            task_id: Task UUID
            approved_by: User ID approving the task
            
        Returns:
            Approved task or None if not found
        """
        task = await AITaskService.get_task(db, task_id)
        if not task:
            return None
        
        task.approved = True
        task.approved_by = approved_by
        task.approved_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task {task_id} approved by {approved_by}")
        return task
    
    @staticmethod
    async def reject_task(
        db: AsyncSession,
        task_id: UUID,
        rejected_by: UUID,
        reason: Optional[str] = None,
    ) -> Optional[AITask]:
        """Reject an AI task.
        
        Args:
            db: Database session
            task_id: Task UUID
            rejected_by: User ID rejecting the task
            reason: Rejection reason
            
        Returns:
            Rejected task or None if not found
        """
        task = await AITaskService.get_task(db, task_id)
        if not task:
            return None
        
        task.status = TaskStatus.CANCELLED
        task.error_message = f"Rejected by user: {reason or 'No reason provided'}"
        
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task {task_id} rejected by {rejected_by}")
        return task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: UUID) -> bool:
        """Delete an AI task.
        
        Args:
            db: Database session
            task_id: Task UUID
            
        Returns:
            True if deleted, False if not found
        """
        task = await AITaskService.get_task(db, task_id)
        if not task:
            return False
        
        await db.delete(task)
        await db.commit()
        logger.info(f"Deleted task {task_id}")
        return True
    
    @staticmethod
    async def get_task_statistics(
        db: AsyncSession,
        created_by: Optional[UUID] = None,
    ) -> dict:
        """Get task statistics.
        
        Args:
            db: Database session
            created_by: Filter by creator
            
        Returns:
            Statistics dictionary
        """
        query = select(AITask)
        if created_by:
            query = query.where(AITask.created_by == created_by)
        
        # Total tasks
        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        # Tasks by status
        status_query = select(
            AITask.status,
            func.count(AITask.id)
        ).group_by(AITask.status)
        
        if created_by:
            status_query = status_query.where(AITask.created_by == created_by)
        
        status_result = await db.execute(status_query)
        by_status = {str(status): count for status, count in status_result.all()}
        
        # Tasks by type
        type_query = select(
            AITask.task_type,
            func.count(AITask.id)
        ).group_by(AITask.task_type)
        
        if created_by:
            type_query = type_query.where(AITask.created_by == created_by)
        
        type_result = await db.execute(type_query)
        by_type = {str(task_type): count for task_type, count in type_result.all()}
        
        return {
            "total_tasks": total,
            "by_status": by_status,
            "by_type": by_type,
        }
