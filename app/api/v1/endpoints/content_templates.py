"""Content Templates API endpoints.

Provides CRUD operations for content templates.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.schemas.content_template import (
    ContentTemplateCreate,
    ContentTemplateResponse,
    ContentTemplateUpdate,
)
from app.services.content_template_service import ContentTemplateService

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response schemas

class TemplateTestRequest(BaseModel):
    """Request to test a template."""
    variables: dict = Field(..., description="Variable values for template")


class TemplateTestResponse(BaseModel):
    """Template test response."""
    rendered: str


# Endpoints

@router.post(
    "/templates",
    response_model=ContentTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create template",
    description="Create a new content template",
)
async def create_template(
    template: ContentTemplateCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a content template."""
    try:
        result = await ContentTemplateService.create_template(
            db=db,
            template_data=template,
            created_by=UUID(str(user.user_id)),
        )
        return result
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}",
        )


@router.get(
    "/templates/{template_id}",
    response_model=ContentTemplateResponse,
    summary="Get template",
    description="Retrieve a specific content template",
)
async def get_template(
    template_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get template by ID."""
    template = await ContentTemplateService.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )
    return template


@router.get(
    "/templates",
    response_model=List[ContentTemplateResponse],
    summary="List templates",
    description="List content templates with optional filters",
)
async def list_templates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List content templates."""
    templates = await ContentTemplateService.list_templates(
        db=db,
        skip=skip,
        limit=limit,
        template_type=template_type,
        language=language,
        platform=platform,
        is_active=is_active,
    )
    return templates


@router.put(
    "/templates/{template_id}",
    response_model=ContentTemplateResponse,
    summary="Update template",
    description="Update an existing content template",
)
async def update_template(
    template_id: UUID,
    template: ContentTemplateUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a template."""
    try:
        result = await ContentTemplateService.update_template(
            db=db,
            template_id=template_id,
            template_data=template,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}",
        )


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete template",
    description="Delete a content template",
)
async def delete_template(
    template_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a template."""
    deleted = await ContentTemplateService.delete_template(db, template_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )


@router.post(
    "/templates/{template_id}/test",
    response_model=TemplateTestResponse,
    summary="Test template",
    description="Test a template with provided variables",
)
async def test_template(
    template_id: UUID,
    request: TemplateTestRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Test a template with variables."""
    try:
        rendered = await ContentTemplateService.test_template(
            db=db,
            template_id=template_id,
            variables=request.variables,
        )
        return {"rendered": rendered}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error testing template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test template: {str(e)}",
        )


@router.get(
    "/templates/suggestions",
    response_model=List[ContentTemplateResponse],
    summary="Get template suggestions",
    description="Get suggested templates for a content type",
)
async def get_template_suggestions(
    content_type: str = Query(..., description="Content type"),
    language: str = Query("en", description="Language code"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get template suggestions."""
    suggestions = await ContentTemplateService.get_template_suggestions(
        db=db,
        content_type=content_type,
        language=language,
    )
    return suggestions
