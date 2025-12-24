"""Image Generation Service.

Provides AI-powered image generation capabilities.
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


class ImageGenerationService:
    """Service for AI image generation."""
    
    SUPPORTED_SIZES = ["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]
    
    @staticmethod
    async def generate_image(
        db: AsyncSession,
        prompt: str,
        size: str,
        style: Optional[str],
        created_by: UUID,
    ) -> Dict:
        """Generate an image from text prompt.
        
        Args:
            db: Database session
            prompt: Image description
            size: Image size
            style: Image style (realistic, artistic, cartoon, etc.)
            created_by: User ID
            
        Returns:
            Generated image info
        """
        if size not in ImageGenerationService.SUPPORTED_SIZES:
            raise ValueError(f"Unsupported size: {size}")
        
        # Create AI task
        task = await AITaskService.create_task(
            db=db,
            task_data=AITaskCreate(
                task_type=TaskType.IMAGE_GENERATION,
                input_data={
                    "prompt": prompt,
                    "size": size,
                    "style": style,
                },
                prompt=prompt,
                requires_approval=True,
            ),
            created_by=created_by,
        )
        
        task.status = TaskStatus.PROCESSING
        await db.commit()
        
        try:
            # Generate image
            start_time = time.time()
            result = await abacus_client.generate_image(
                prompt=prompt,
                size=size,
            )
            processing_time = time.time() - start_time
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.output_data = result
            task.processing_time = processing_time
            
            await db.commit()
            
            logger.info(f"Generated image for task {task.id}")
            return {
                "task_id": str(task.id),
                "image_url": result["image_url"],
                "size": size,
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            await db.commit()
            raise
    
    @staticmethod
    async def generate_variations(
        db: AsyncSession,
        image_url: str,
        num_variations: int,
        created_by: UUID,
    ) -> Dict:
        """Generate variations of an existing image.
        
        Args:
            db: Database session
            image_url: Source image URL
            num_variations: Number of variations to generate
            created_by: User ID
            
        Returns:
            Generated variations
        """
        # Placeholder implementation
        logger.warning("Image variations not yet fully implemented")
        return {
            "variations": [],
            "message": "Feature coming soon",
        }
