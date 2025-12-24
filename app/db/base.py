"""Database base classes and common models."""

from sqlalchemy.orm import DeclarativeBase

# Import all models here for Alembic to detect them
from app.db.base_class import Base  # noqa: F401
from app.models.ai_task import AITask  # noqa: F401
from app.models.content_template import ContentTemplate  # noqa: F401
from app.models.generated_content import GeneratedContent  # noqa: F401
from app.models.translation_job import TranslationJob  # noqa: F401
