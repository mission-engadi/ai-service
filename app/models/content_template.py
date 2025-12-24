"""ContentTemplate database model.

Stores reusable templates for AI content generation with variable placeholders.
"""

from typing import List
from uuid import UUID, uuid4

from sqlalchemy import (
    ARRAY,
    Boolean,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.generated_content import ContentType


class ContentTemplate(Base):
    """Content Template model.
    
    Stores reusable templates for AI content generation. Templates can include
    variables that are replaced at generation time (e.g., {organization_name},
    {campaign_title}, {impact_story}, etc.).
    
    Attributes:
        id: Unique template identifier (UUID)
        name: Template name (indexed)
        template_type: Type of content this template generates
        description: Template description
        prompt_template: Template text with variables in {variable} format
        variables: List of variable names used in the template
        language: Template language (en, es, fr, pt)
        platform: Target platform for social posts
        is_active: Whether template is active and available for use
        usage_count: Number of times template has been used
        created_by: User ID who created the template
        created_at: Creation timestamp (inherited)
        updated_at: Last update timestamp (inherited)
    """
    
    __tablename__ = "content_templates"
    
    # Override id to use UUID
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    
    # Template identification
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    template_type: Mapped[ContentType] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Template content
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )
    
    # Language and platform
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        index=True,
    )
    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    
    # Template status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    
    # Audit
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    def __repr__(self) -> str:
        return (
            f"<ContentTemplate(id={self.id}, name='{self.name}', "
            f"type='{self.template_type}', active={self.is_active})>"
        )
    
    def increment_usage(self) -> None:
        """Increment the usage count for this template."""
        self.usage_count += 1
