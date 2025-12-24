"""AITask database model.

Tracks AI processing tasks for content generation, translation, and other AI operations.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.generated_content import GeneratedContent
    from app.models.translation_job import TranslationJob


class TaskType(str, enum.Enum):
    """AI task types."""
    
    CONTENT_GENERATION = "content_generation"
    TRANSLATION = "translation"
    IMAGE_GENERATION = "image_generation"
    CONTENT_ENHANCEMENT = "content_enhancement"
    AUTOMATION = "automation"


class TaskStatus(str, enum.Enum):
    """AI task status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AITask(Base):
    """AI Task model.
    
    Tracks AI processing tasks including content generation, translation,
    image generation, and content enhancement operations.
    
    Attributes:
        id: Unique task identifier (UUID)
        task_type: Type of AI task (content_generation, translation, etc.)
        status: Current status (pending, processing, completed, failed, cancelled)
        input_data: Input parameters as JSON
        output_data: Generated output as JSON
        prompt: AI prompt used for generation
        model_used: Name of AI model used
        tokens_used: Number of tokens consumed
        processing_time: Processing time in seconds
        error_message: Error message if task failed
        requires_approval: Whether task output requires approval
        approved: Whether task output has been approved
        approved_by: User ID who approved the task
        approved_at: Timestamp of approval
        created_by: User ID who created the task
        created_at: Task creation timestamp (inherited)
        updated_at: Last update timestamp (inherited)
    """
    
    __tablename__ = "ai_tasks"
    
    # Override id to use UUID
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    
    # Task information
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType),
        nullable=False,
        index=True,
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
    )
    
    # Task data
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # AI model information
    prompt: Mapped[str] = mapped_column(Text, nullable=True)
    model_used: Mapped[str] = mapped_column(String(255), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    processing_time: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Error handling
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Approval workflow
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Audit fields
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    # Relationships
    generated_content: Mapped[list["GeneratedContent"]] = relationship(
        "GeneratedContent",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    
    translation_jobs: Mapped[list["TranslationJob"]] = relationship(
        "TranslationJob",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return (
            f"<AITask(id={self.id}, type='{self.task_type.value}', "
            f"status='{self.status.value}')>"
        )
