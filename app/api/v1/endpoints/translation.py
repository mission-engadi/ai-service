"""Translation API endpoints.

Provides AI-powered translation capabilities for multi-language content support.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.models.translation_job import TranslationJob
from app.services.translation_service import TranslationService
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response schemas

class TranslateRequest(BaseModel):
    """Request to translate text."""
    text: str = Field(..., min_length=1, description="Text to translate")
    source_lang: str = Field(..., description="Source language (en, es, fr, pt)")
    target_lang: str = Field(..., description="Target language (en, es, fr, pt)")


class BatchTranslateRequest(BaseModel):
    """Request to batch translate multiple texts."""
    texts: List[str] = Field(..., min_items=1, max_items=50, description="Texts to translate")
    source_lang: str = Field(..., description="Source language")
    target_lang: str = Field(..., description="Target language")


class AutoTranslateRequest(BaseModel):
    """Request to auto-translate content."""
    content_id: UUID = Field(..., description="Content ID to translate")
    target_languages: List[str] = Field(..., min_items=1, description="Target languages")


class TranslationResponse(BaseModel):
    """Translation response."""
    task_id: str
    translation_id: str
    translated_text: str
    quality_score: float
    status: str


class BatchTranslationResponse(BaseModel):
    """Batch translation response."""
    results: List[TranslationResponse]


class AutoTranslationResponse(BaseModel):
    """Auto-translation response."""
    content_id: str
    source_language: str
    translations: dict


class TranslationJobResponse(BaseModel):
    """Translation job details."""
    id: str
    task_id: str
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    status: str
    quality_score: float


# Endpoints

@router.post(
    "/translate",
    response_model=TranslationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Translate text",
    description="Translate text between supported languages (en, es, fr, pt)",
)
async def translate_text(
    request: TranslateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Translate text from source language to target language."""
    try:
        result = await TranslationService.translate(
            db=db,
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            created_by=UUID(str(user.user_id)),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to translate text: {str(e)}",
        )


@router.post(
    "/translate/batch",
    response_model=List[TranslationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Batch translate texts",
    description="Translate multiple texts in a single request",
)
async def batch_translate(
    request: BatchTranslateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Batch translate multiple texts."""
    try:
        results = await TranslationService.batch_translate(
            db=db,
            texts=request.texts,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            created_by=UUID(str(user.user_id)),
        )
        return results
    except Exception as e:
        logger.error(f"Error in batch translation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch translate: {str(e)}",
        )


@router.post(
    "/translate/auto",
    response_model=AutoTranslationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Auto-translate content",
    description="Automatically translate existing content to multiple languages",
)
async def auto_translate_content(
    request: AutoTranslateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Auto-translate content to multiple target languages."""
    try:
        result = await TranslationService.auto_translate_content(
            db=db,
            content_id=request.content_id,
            target_languages=request.target_languages,
            created_by=UUID(str(user.user_id)),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in auto-translation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-translate: {str(e)}",
        )


@router.get(
    "/translate/{translation_id}",
    response_model=TranslationJobResponse,
    summary="Get translation job",
    description="Retrieve details of a specific translation job",
)
async def get_translation_job(
    translation_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get translation job by ID."""
    result = await db.execute(
        select(TranslationJob).where(TranslationJob.id == translation_id)
    )
    translation_job = result.scalar_one_or_none()
    
    if not translation_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Translation job {translation_id} not found",
        )
    
    return {
        "id": str(translation_job.id),
        "task_id": str(translation_job.task_id),
        "source_language": translation_job.source_language,
        "target_language": translation_job.target_language,
        "source_text": translation_job.source_text,
        "translated_text": translation_job.translated_text or "",
        "status": translation_job.status.value,
        "quality_score": translation_job.quality_score or 0.0,
    }


@router.get(
    "/translate",
    response_model=List[TranslationJobResponse],
    summary="List translation jobs",
    description="List translation jobs with optional filters",
)
async def list_translation_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    source_lang: str = Query(None, description="Filter by source language"),
    target_lang: str = Query(None, description="Filter by target language"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List translation jobs."""
    query = select(TranslationJob)
    
    if source_lang:
        query = query.where(TranslationJob.source_language == source_lang)
    if target_lang:
        query = query.where(TranslationJob.target_language == target_lang)
    
    query = query.offset(skip).limit(limit).order_by(TranslationJob.created_at.desc())
    
    result = await db.execute(query)
    translation_jobs = result.scalars().all()
    
    return [
        {
            "id": str(job.id),
            "task_id": str(job.task_id),
            "source_language": job.source_language,
            "target_language": job.target_language,
            "source_text": job.source_text[:100] + "..." if len(job.source_text) > 100 else job.source_text,
            "translated_text": (job.translated_text[:100] + "...") if job.translated_text and len(job.translated_text) > 100 else (job.translated_text or ""),
            "status": job.status.value,
            "quality_score": job.quality_score or 0.0,
        }
        for job in translation_jobs
    ]
