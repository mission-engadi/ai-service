"""TranslationJob database model.

Tracks AI translation tasks for multi-language content support.
"""

import enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.ai_task import AITask


class TranslationStatus(str, enum.Enum):
    """Translation job status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranslationJob(Base):
    """Translation Job model.
    
    Tracks AI translation tasks for converting content between languages.
    Supports English, Spanish, French, and Portuguese.
    
    Attributes:
        id: Unique job identifier (UUID)
        task_id: Reference to the parent AI task
        source_language: Source language code (en, es, fr, pt)
        target_language: Target language code (en, es, fr, pt)
        source_text: Original text to translate
        translated_text: Translated text (null until completed)
        status: Current translation status
        quality_score: AI confidence/quality score
        error_message: Error message if translation failed
        created_at: Creation timestamp (inherited)
        updated_at: Last update timestamp (inherited)
    """
    
    __tablename__ = "translation_jobs"
    
    # Override id to use UUID
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    
    # Foreign key to AI task
    task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Language information
    source_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    target_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    
    # Translation content
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Status and quality
    status: Mapped[TranslationStatus] = mapped_column(
        Enum(TranslationStatus),
        nullable=False,
        default=TranslationStatus.PENDING,
        index=True,
    )
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Error handling
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    task: Mapped["AITask"] = relationship(
        "AITask",
        back_populates="translation_jobs",
    )
    
    def __repr__(self) -> str:
        return (
            f"<TranslationJob(id={self.id}, {self.source_language}->{self.target_language}, "
            f"status='{self.status.value}')>"
        )
