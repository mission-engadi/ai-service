"""Translation Service.

Provides AI-powered translation capabilities.
"""

import logging
import time
from typing import Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.abacus_client import abacus_client
from app.models.ai_task import AITask, TaskStatus, TaskType
from app.models.translation_job import TranslationJob, TranslationStatus
from app.services.ai_task_service import AITaskService
from app.schemas.ai_task import AITaskCreate

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for AI translation."""
    
    SUPPORTED_LANGUAGES = ["en", "es", "fr", "pt"]
    
    @staticmethod
    async def translate(
        db: AsyncSession,
        text: str,
        source_lang: str,
        target_lang: str,
        created_by: UUID,
    ) -> Dict:
        """Translate text.
        
        Args:
            db: Database session
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            created_by: User ID
            
        Returns:
            Translation result
        """
        # Validate languages
        if source_lang not in TranslationService.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language: {source_lang}")
        if target_lang not in TranslationService.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_lang}")
        
        # Create AI task
        task = await AITaskService.create_task(
            db=db,
            task_data=AITaskCreate(
                task_type=TaskType.TRANSLATION,
                input_data={
                    "text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                },
                prompt="",
                requires_approval=False,
            ),
            created_by=created_by,
        )
        
        # Create translation job
        translation_job = TranslationJob(
            task_id=task.id,
            source_language=source_lang,
            target_language=target_lang,
            source_text=text,
            status=TranslationStatus.PROCESSING,
        )
        db.add(translation_job)
        
        task.status = TaskStatus.PROCESSING
        await db.commit()
        
        try:
            # Perform translation
            start_time = time.time()
            result = await abacus_client.translate_text(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            processing_time = time.time() - start_time
            
            # Update records
            task.status = TaskStatus.COMPLETED
            task.tokens_used = result.get("tokens_used")
            task.processing_time = processing_time
            task.output_data = result
            
            translation_job.status = TranslationStatus.COMPLETED
            translation_job.translated_text = result["translated_text"]
            translation_job.quality_score = result.get("quality_score")
            
            await db.commit()
            await db.refresh(translation_job)
            
            logger.info(f"Completed translation job {translation_job.id}")
            return {
                "task_id": str(task.id),
                "translation_id": str(translation_job.id),
                "translated_text": result["translated_text"],
                "quality_score": result.get("quality_score"),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            translation_job.status = TranslationStatus.FAILED
            translation_job.error_message = str(e)
            await db.commit()
            raise
    
    @staticmethod
    async def batch_translate(
        db: AsyncSession,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        created_by: UUID,
    ) -> List[Dict]:
        """Batch translate multiple texts.
        
        Args:
            db: Database session
            texts: List of texts to translate
            source_lang: Source language
            target_lang: Target language
            created_by: User ID
            
        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            try:
                result = await TranslationService.translate(
                    db=db,
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    created_by=created_by,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error in batch translation: {e}")
                results.append({"error": str(e), "text": text})
        
        return results
    
    @staticmethod
    async def auto_translate_content(
        db: AsyncSession,
        content_id: UUID,
        target_languages: List[str],
        created_by: UUID,
    ) -> Dict:
        """Auto-translate content to multiple languages.
        
        Args:
            db: Database session
            content_id: Content ID to translate
            target_languages: List of target language codes
            created_by: User ID
            
        Returns:
            Translation results for all languages
        """
        # Fetch content
        from app.models.generated_content import GeneratedContent
        from sqlalchemy import select
        
        result = await db.execute(
            select(GeneratedContent).where(GeneratedContent.id == content_id)
        )
        content = result.scalar_one_or_none()
        
        if not content:
            raise ValueError(f"Content {content_id} not found")
        
        # Translate to each target language
        translations = {}
        for target_lang in target_languages:
            if target_lang == content.language:
                continue  # Skip source language
            
            try:
                translation = await TranslationService.translate(
                    db=db,
                    text=content.body,
                    source_lang=content.language,
                    target_lang=target_lang,
                    created_by=created_by,
                )
                translations[target_lang] = translation
            except Exception as e:
                logger.error(f"Error translating to {target_lang}: {e}")
                translations[target_lang] = {"error": str(e)}
        
        return {
            "content_id": str(content_id),
            "source_language": content.language,
            "translations": translations,
        }
