"""Generated Content API endpoints.

Provides operations for managing AI-generated content.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.models.generated_content import ContentType, GeneratedContent
from app.schemas.generated_content import (
    GeneratedContentListResponse,
    GeneratedContentResponse,
    GeneratedContentUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response schemas

class PublishContentRequest(BaseModel):
    """Request to publish content."""
    external_id: Optional[UUID] = None


class ContentStatisticsResponse(BaseModel):
    """Content statistics response."""
    total_content: int
    by_type: dict
    by_language: dict
    published_count: int


# Endpoints

@router.get(
    "/content/{content_id}",
    response_model=GeneratedContentResponse,
    summary="Get generated content",
    description="Retrieve details of generated content",
)
async def get_content(
    content_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get generated content by ID."""
    result = await db.execute(
        select(GeneratedContent).where(GeneratedContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content {content_id} not found",
        )
    return content


@router.get(
    "/content",
    response_model=List[GeneratedContentListResponse],
    summary="List generated content",
    description="List generated content with optional filters",
)
async def list_content(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    published: Optional[bool] = Query(None, description="Filter by published status"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List generated content."""
    query = select(GeneratedContent)
    
    if content_type:
        query = query.where(GeneratedContent.content_type == content_type)
    if language:
        query = query.where(GeneratedContent.language == language)
    if platform:
        query = query.where(GeneratedContent.platform == platform)
    if published is not None:
        query = query.where(GeneratedContent.published == published)
    
    query = query.offset(skip).limit(limit).order_by(GeneratedContent.created_at.desc())
    
    result = await db.execute(query)
    contents = result.scalars().all()
    return contents


@router.put(
    "/content/{content_id}",
    response_model=GeneratedContentResponse,
    summary="Update generated content",
    description="Update generated content details",
)
async def update_content(
    content_id: UUID,
    content_update: GeneratedContentUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update generated content."""
    result = await db.execute(
        select(GeneratedContent).where(GeneratedContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content {content_id} not found",
        )
    
    update_data = content_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    await db.commit()
    await db.refresh(content)
    return content


@router.delete(
    "/content/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete generated content",
    description="Delete generated content",
)
async def delete_content(
    content_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete generated content."""
    result = await db.execute(
        select(GeneratedContent).where(GeneratedContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content {content_id} not found",
        )
    
    await db.delete(content)
    await db.commit()


@router.post(
    "/content/{content_id}/publish",
    response_model=GeneratedContentResponse,
    summary="Publish generated content",
    description="Mark content as published and optionally set external ID",
)
async def publish_content(
    content_id: UUID,
    request: PublishContentRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish generated content."""
    result = await db.execute(
        select(GeneratedContent).where(GeneratedContent.id == content_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content {content_id} not found",
        )
    
    from datetime import datetime
    content.published = True
    content.published_at = datetime.utcnow()
    if request.external_id:
        content.external_id = request.external_id
    
    await db.commit()
    await db.refresh(content)
    
    logger.info(f"Published content {content_id}")
    return content


@router.get(
    "/content/statistics",
    response_model=ContentStatisticsResponse,
    summary="Get content statistics",
    description="Retrieve generated content statistics",
)
async def get_content_statistics(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content statistics."""
    from sqlalchemy import func
    
    # Total content
    total_result = await db.execute(
        select(func.count(GeneratedContent.id))
    )
    total = total_result.scalar()
    
    # By type
    type_result = await db.execute(
        select(GeneratedContent.content_type, func.count(GeneratedContent.id))
        .group_by(GeneratedContent.content_type)
    )
    by_type = {str(ct): count for ct, count in type_result.all()}
    
    # By language
    lang_result = await db.execute(
        select(GeneratedContent.language, func.count(GeneratedContent.id))
        .group_by(GeneratedContent.language)
    )
    by_language = {lang: count for lang, count in lang_result.all()}
    
    # Published count
    published_result = await db.execute(
        select(func.count(GeneratedContent.id))
        .where(GeneratedContent.published == True)
    )
    published_count = published_result.scalar()
    
    return {
        "total_content": total,
        "by_type": by_type,
        "by_language": by_language,
        "published_count": published_count,
    }
