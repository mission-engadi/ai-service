"""Content Template Service.

Provides CRUD operations for content templates.
"""

import logging
import re
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_template import ContentTemplate
from app.schemas.content_template import ContentTemplateCreate, ContentTemplateUpdate

logger = logging.getLogger(__name__)


class ContentTemplateService:
    """Service for content template operations."""
    
    @staticmethod
    def extract_variables(template_text: str) -> List[str]:
        """Extract variable names from template text.
        
        Variables are in the format {variable_name}.
        """
        pattern = r"\{([^}]+)\}"
        matches = re.findall(pattern, template_text)
        return list(set(matches))  # Remove duplicates
    
    @staticmethod
    async def create_template(
        db: AsyncSession,
        template_data: ContentTemplateCreate,
        created_by: UUID,
    ) -> ContentTemplate:
        """Create a new content template.
        
        Args:
            db: Database session
            template_data: Template creation data
            created_by: User ID
            
        Returns:
            Created template
        """
        # Extract variables from prompt template
        variables = ContentTemplateService.extract_variables(
            template_data.prompt_template
        )
        
        template = ContentTemplate(
            name=template_data.name,
            template_type=template_data.template_type,
            description=template_data.description,
            prompt_template=template_data.prompt_template,
            variables=variables,
            language=template_data.language,
            platform=template_data.platform,
            is_active=True,
            usage_count=0,
            created_by=created_by,
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        logger.info(f"Created template {template.id}: {template.name}")
        return template
    
    @staticmethod
    async def get_template(
        db: AsyncSession,
        template_id: UUID,
    ) -> Optional[ContentTemplate]:
        """Get template by ID."""
        result = await db.execute(
            select(ContentTemplate).where(ContentTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_templates(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        template_type: Optional[str] = None,
        language: Optional[str] = None,
        platform: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> List[ContentTemplate]:
        """List templates with filters."""
        query = select(ContentTemplate)
        
        if template_type:
            query = query.where(ContentTemplate.template_type == template_type)
        if language:
            query = query.where(ContentTemplate.language == language)
        if platform:
            query = query.where(ContentTemplate.platform == platform)
        if is_active is not None:
            query = query.where(ContentTemplate.is_active == is_active)
        
        query = query.offset(skip).limit(limit).order_by(
            ContentTemplate.usage_count.desc(),
            ContentTemplate.created_at.desc()
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_template(
        db: AsyncSession,
        template_id: UUID,
        template_data: ContentTemplateUpdate,
    ) -> Optional[ContentTemplate]:
        """Update a template."""
        template = await ContentTemplateService.get_template(db, template_id)
        if not template:
            return None
        
        update_data = template_data.model_dump(exclude_unset=True)
        
        # If prompt template is updated, re-extract variables
        if "prompt_template" in update_data:
            variables = ContentTemplateService.extract_variables(
                update_data["prompt_template"]
            )
            update_data["variables"] = variables
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        await db.commit()
        await db.refresh(template)
        
        logger.info(f"Updated template {template_id}")
        return template
    
    @staticmethod
    async def delete_template(
        db: AsyncSession,
        template_id: UUID,
    ) -> bool:
        """Delete a template."""
        template = await ContentTemplateService.get_template(db, template_id)
        if not template:
            return False
        
        await db.delete(template)
        await db.commit()
        
        logger.info(f"Deleted template {template_id}")
        return True
    
    @staticmethod
    async def increment_usage(
        db: AsyncSession,
        template_id: UUID,
    ) -> None:
        """Increment template usage count."""
        template = await ContentTemplateService.get_template(db, template_id)
        if template:
            template.increment_usage()
            await db.commit()
    
    @staticmethod
    async def test_template(
        db: AsyncSession,
        template_id: UUID,
        variables: dict,
    ) -> str:
        """Test a template with provided variables.
        
        Args:
            db: Database session
            template_id: Template ID
            variables: Variable values
            
        Returns:
            Rendered template
        """
        template = await ContentTemplateService.get_template(db, template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        try:
            rendered = template.prompt_template.format(**variables)
            return rendered
        except KeyError as e:
            raise ValueError(f"Missing variable: {e}")
    
    @staticmethod
    async def get_template_suggestions(
        db: AsyncSession,
        content_type: str,
        language: str = "en",
    ) -> List[ContentTemplate]:
        """Get template suggestions for a content type."""
        result = await db.execute(
            select(ContentTemplate)
            .where(
                ContentTemplate.template_type == content_type,
                ContentTemplate.language == language,
                ContentTemplate.is_active == True,
            )
            .order_by(ContentTemplate.usage_count.desc())
            .limit(5)
        )
        return list(result.scalars().all())
