"""Content Enhancement Service.

Provides AI-powered content improvement capabilities.
"""

import logging
import time
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.abacus_client import abacus_client
from app.models.ai_task import TaskStatus, TaskType
from app.services.ai_task_service import AITaskService
from app.schemas.ai_task import AITaskCreate

logger = logging.getLogger(__name__)


class ContentEnhancementService:
    """Service for AI content enhancement."""
    
    ENHANCEMENT_TYPES = ["grammar", "tone", "seo", "summarize", "improve"]
    
    @staticmethod
    async def enhance_content(
        db: AsyncSession,
        text: str,
        enhancement_type: str,
        context: Optional[str],
        created_by: UUID,
    ) -> Dict:
        """Enhance content using AI.
        
        Args:
            db: Database session
            text: Text to enhance
            enhancement_type: Type of enhancement
            context: Additional context
            created_by: User ID
            
        Returns:
            Enhanced content
        """
        if enhancement_type not in ContentEnhancementService.ENHANCEMENT_TYPES:
            raise ValueError(f"Unsupported enhancement type: {enhancement_type}")
        
        # Create AI task
        task = await AITaskService.create_task(
            db=db,
            task_data=AITaskCreate(
                task_type=TaskType.CONTENT_ENHANCEMENT,
                input_data={
                    "text": text,
                    "enhancement_type": enhancement_type,
                    "context": context,
                },
                prompt="",
                requires_approval=False,
            ),
            created_by=created_by,
        )
        
        task.status = TaskStatus.PROCESSING
        await db.commit()
        
        try:
            # Enhance content
            start_time = time.time()
            result = await abacus_client.enhance_text(
                text=text,
                enhancement_type=enhancement_type,
                additional_context=context,
            )
            processing_time = time.time() - start_time
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.output_data = result
            task.tokens_used = result.get("tokens_used")
            task.processing_time = processing_time
            
            await db.commit()
            
            logger.info(f"Enhanced content for task {task.id}")
            return {
                "task_id": str(task.id),
                "original_text": text,
                "enhanced_text": result["enhanced_text"],
                "enhancement_type": enhancement_type,
                "changes_made": result.get("changes_made", []),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Content enhancement error: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            await db.commit()
            raise
    
    @staticmethod
    async def fix_grammar(
        db: AsyncSession,
        text: str,
        created_by: UUID,
    ) -> Dict:
        """Fix grammar and spelling."""
        return await ContentEnhancementService.enhance_content(
            db=db,
            text=text,
            enhancement_type="grammar",
            context=None,
            created_by=created_by,
        )
    
    @staticmethod
    async def adjust_tone(
        db: AsyncSession,
        text: str,
        target_tone: str,
        created_by: UUID,
    ) -> Dict:
        """Adjust content tone."""
        return await ContentEnhancementService.enhance_content(
            db=db,
            text=text,
            enhancement_type="tone",
            context=target_tone,
            created_by=created_by,
        )
    
    @staticmethod
    async def optimize_seo(
        db: AsyncSession,
        text: str,
        keywords: Optional[str],
        created_by: UUID,
    ) -> Dict:
        """Optimize content for SEO."""
        return await ContentEnhancementService.enhance_content(
            db=db,
            text=text,
            enhancement_type="seo",
            context=keywords,
            created_by=created_by,
        )
    
    @staticmethod
    async def summarize(
        db: AsyncSession,
        text: str,
        max_length: Optional[int],
        created_by: UUID,
    ) -> Dict:
        """Summarize content."""
        context = f"Maximum {max_length} words" if max_length else None
        return await ContentEnhancementService.enhance_content(
            db=db,
            text=text,
            enhancement_type="summarize",
            context=context,
            created_by=created_by,
        )
