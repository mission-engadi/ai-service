"""Tests for AI task service."""
import pytest
from app.services.ai_task_service import AITaskService
from app.schemas.ai_task import (
    AITaskCreate,
    AITaskUpdate,
    TaskStatus,
)


@pytest.fixture
def task_service(test_db):
    """Create AI task service instance."""
    return AITaskService(test_db)


@pytest.mark.asyncio
async def test_create_task(task_service):
    """Test task creation."""
    task_data = AITaskCreate(
        task_type="content_generation",
        description="Generate social media post",
        priority="high",
        metadata={"platform": "twitter", "topic": "Mission Update"},
    )

    task = await task_service.create_task(task_data, user_id="test-user")

    assert task is not None
    assert task.task_type == "content_generation"
    assert task.status == TaskStatus.PENDING
    assert task.created_by == "test-user"


@pytest.mark.asyncio
async def test_get_task(task_service):
    """Test retrieving a task."""
    # Create task first
    task_data = AITaskCreate(
        task_type="translation",
        description="Translate content",
        priority="medium",
    )
    created_task = await task_service.create_task(task_data, user_id="test-user")

    # Retrieve task
    task = await task_service.get_task(created_task.id)

    assert task is not None
    assert task.id == created_task.id
    assert task.task_type == "translation"


@pytest.mark.asyncio
async def test_update_task_status(task_service):
    """Test updating task status."""
    # Create task
    task_data = AITaskCreate(
        task_type="content_generation",
        description="Generate article",
        priority="low",
    )
    task = await task_service.create_task(task_data, user_id="test-user")

    # Update status
    update_data = AITaskUpdate(status=TaskStatus.IN_PROGRESS)
    updated_task = await task_service.update_task(task.id, update_data)

    assert updated_task.status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_approve_task(task_service):
    """Test task approval."""
    # Create task
    task_data = AITaskCreate(
        task_type="content_generation",
        description="Generate content",
        priority="high",
    )
    task = await task_service.create_task(task_data, user_id="test-user")

    # Approve task
    approved_task = await task_service.approve_task(
        task_id=task.id,
        approved_by="admin-user",
        comments="Looks good",
    )

    assert approved_task.status == TaskStatus.APPROVED
    assert approved_task.approved_by == "admin-user"


@pytest.mark.asyncio
async def test_reject_task(task_service):
    """Test task rejection."""
    # Create task
    task_data = AITaskCreate(
        task_type="content_generation",
        description="Generate content",
        priority="high",
    )
    task = await task_service.create_task(task_data, user_id="test-user")

    # Reject task
    rejected_task = await task_service.reject_task(
        task_id=task.id,
        rejected_by="admin-user",
        reason="Needs revision",
    )

    assert rejected_task.status == TaskStatus.REJECTED


@pytest.mark.asyncio
async def test_get_task_statistics(task_service):
    """Test task statistics."""
    # Create multiple tasks
    for i in range(5):
        task_data = AITaskCreate(
            task_type="content_generation",
            description=f"Task {i}",
            priority="medium",
        )
        await task_service.create_task(task_data, user_id="test-user")

    # Get statistics
    stats = await task_service.get_task_statistics(user_id="test-user")

    assert stats is not None
    assert "total" in stats
    assert stats["total"] == 5
    assert "by_status" in stats
    assert "by_type" in stats
