"""Pydantic schemas for AI Service."""

from app.schemas.ai_task import (
    AITaskApproval,
    AITaskBase,
    AITaskCreate,
    AITaskListResponse,
    AITaskResponse,
    AITaskUpdate,
)
from app.schemas.content_template import (
    ContentTemplateBase,
    ContentTemplateCreate,
    ContentTemplateGenerate,
    ContentTemplateListResponse,
    ContentTemplateResponse,
    ContentTemplateUpdate,
)
from app.schemas.generated_content import (
    GeneratedContentBase,
    GeneratedContentCreate,
    GeneratedContentListResponse,
    GeneratedContentPublish,
    GeneratedContentResponse,
    GeneratedContentUpdate,
)
from app.schemas.translation_job import (
    TranslationJobBase,
    TranslationJobCreate,
    TranslationJobListResponse,
    TranslationJobResponse,
    TranslationJobUpdate,
    TranslationRequest,
)

__all__ = [
    # AI Task schemas
    "AITaskBase",
    "AITaskCreate",
    "AITaskUpdate",
    "AITaskResponse",
    "AITaskListResponse",
    "AITaskApproval",
    # Content Template schemas
    "ContentTemplateBase",
    "ContentTemplateCreate",
    "ContentTemplateUpdate",
    "ContentTemplateResponse",
    "ContentTemplateListResponse",
    "ContentTemplateGenerate",
    # Generated Content schemas
    "GeneratedContentBase",
    "GeneratedContentCreate",
    "GeneratedContentUpdate",
    "GeneratedContentResponse",
    "GeneratedContentListResponse",
    "GeneratedContentPublish",
    # Translation Job schemas
    "TranslationJobBase",
    "TranslationJobCreate",
    "TranslationJobUpdate",
    "TranslationJobResponse",
    "TranslationJobListResponse",
    "TranslationRequest",
]
