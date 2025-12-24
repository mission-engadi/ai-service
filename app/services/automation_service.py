"""Automation Service.

Provides automated content generation workflows.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_task import AITask, TaskType
from app.services.content_generation_service import ContentGenerationService
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


class AutomationWorkflow:
    """Represents an automation workflow."""
    
    def __init__(
        self,
        id: UUID,
        name: str,
        workflow_type: str,
        config: Dict,
        schedule: Optional[str],
        is_active: bool,
        created_by: UUID,
    ):
        self.id = id
        self.name = name
        self.workflow_type = workflow_type
        self.config = config
        self.schedule = schedule
        self.is_active = is_active
        self.created_by = created_by
        self.created_at = datetime.utcnow()


class AutomationService:
    """Service for content automation workflows."""
    
    # In-memory storage for workflows (should be in database in production)
    _workflows: Dict[UUID, AutomationWorkflow] = {}
    _workflow_history: List[Dict] = []
    
    @staticmethod
    async def create_workflow(
        db: AsyncSession,
        name: str,
        workflow_type: str,
        config: Dict,
        schedule: Optional[str],
        created_by: UUID,
    ) -> Dict:
        """Create an automation workflow.
        
        Args:
            db: Database session
            name: Workflow name
            workflow_type: Type (auto_translate, scheduled_post, etc.)
            config: Workflow configuration
            schedule: Cron schedule (optional)
            created_by: User ID
            
        Returns:
            Created workflow info
        """
        from uuid import uuid4
        
        workflow_id = uuid4()
        workflow = AutomationWorkflow(
            id=workflow_id,
            name=name,
            workflow_type=workflow_type,
            config=config,
            schedule=schedule,
            is_active=True,
            created_by=created_by,
        )
        
        AutomationService._workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow_id}: {name}")
        return {
            "workflow_id": str(workflow_id),
            "name": name,
            "workflow_type": workflow_type,
            "is_active": True,
            "created_at": workflow.created_at.isoformat(),
        }
    
    @staticmethod
    async def get_workflow(workflow_id: UUID) -> Optional[Dict]:
        """Get workflow by ID."""
        workflow = AutomationService._workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": str(workflow.id),
            "name": workflow.name,
            "workflow_type": workflow.workflow_type,
            "config": workflow.config,
            "schedule": workflow.schedule,
            "is_active": workflow.is_active,
            "created_by": str(workflow.created_by),
            "created_at": workflow.created_at.isoformat(),
        }
    
    @staticmethod
    async def list_workflows(
        created_by: Optional[UUID] = None,
    ) -> List[Dict]:
        """List workflows."""
        workflows = []
        for workflow in AutomationService._workflows.values():
            if created_by and workflow.created_by != created_by:
                continue
            
            workflows.append({
                "workflow_id": str(workflow.id),
                "name": workflow.name,
                "workflow_type": workflow.workflow_type,
                "is_active": workflow.is_active,
                "created_at": workflow.created_at.isoformat(),
            })
        
        return workflows
    
    @staticmethod
    async def update_workflow(
        workflow_id: UUID,
        name: Optional[str],
        config: Optional[Dict],
        schedule: Optional[str],
        is_active: Optional[bool],
    ) -> Optional[Dict]:
        """Update a workflow."""
        workflow = AutomationService._workflows.get(workflow_id)
        if not workflow:
            return None
        
        if name:
            workflow.name = name
        if config:
            workflow.config = config
        if schedule is not None:
            workflow.schedule = schedule
        if is_active is not None:
            workflow.is_active = is_active
        
        return await AutomationService.get_workflow(workflow_id)
    
    @staticmethod
    async def delete_workflow(workflow_id: UUID) -> bool:
        """Delete a workflow."""
        if workflow_id in AutomationService._workflows:
            del AutomationService._workflows[workflow_id]
            logger.info(f"Deleted workflow {workflow_id}")
            return True
        return False
    
    @staticmethod
    async def trigger_workflow(
        db: AsyncSession,
        workflow_id: UUID,
        trigger_data: Optional[Dict],
        created_by: UUID,
    ) -> Dict:
        """Trigger a workflow execution.
        
        Args:
            db: Database session
            workflow_id: Workflow ID
            trigger_data: Additional trigger data
            created_by: User ID
            
        Returns:
            Execution result
        """
        workflow = AutomationService._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if not workflow.is_active:
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Execute workflow based on type
        execution_id = str(UUID())
        start_time = datetime.utcnow()
        
        try:
            if workflow.workflow_type == "auto_translate":
                result = await AutomationService._execute_auto_translate(
                    db, workflow, trigger_data, created_by
                )
            elif workflow.workflow_type == "scheduled_post":
                result = await AutomationService._execute_scheduled_post(
                    db, workflow, trigger_data, created_by
                )
            else:
                result = {"message": "Workflow type not implemented"}
            
            # Record execution
            execution_record = {
                "execution_id": execution_id,
                "workflow_id": str(workflow_id),
                "started_at": start_time.isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "result": result,
            }
            AutomationService._workflow_history.append(execution_record)
            
            return execution_record
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            execution_record = {
                "execution_id": execution_id,
                "workflow_id": str(workflow_id),
                "started_at": start_time.isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "status": "failed",
                "error": str(e),
            }
            AutomationService._workflow_history.append(execution_record)
            raise
    
    @staticmethod
    async def _execute_auto_translate(
        db: AsyncSession,
        workflow: AutomationWorkflow,
        trigger_data: Optional[Dict],
        created_by: UUID,
    ) -> Dict:
        """Execute auto-translate workflow."""
        content_id = trigger_data.get("content_id") if trigger_data else None
        target_languages = workflow.config.get("target_languages", ["es", "fr", "pt"])
        
        if not content_id:
            raise ValueError("content_id required for auto_translate workflow")
        
        from uuid import UUID as parse_uuid
        result = await TranslationService.auto_translate_content(
            db=db,
            content_id=parse_uuid(content_id),
            target_languages=target_languages,
            created_by=created_by,
        )
        
        return result
    
    @staticmethod
    async def _execute_scheduled_post(
        db: AsyncSession,
        workflow: AutomationWorkflow,
        trigger_data: Optional[Dict],
        created_by: UUID,
    ) -> Dict:
        """Execute scheduled post workflow."""
        config = workflow.config
        result = await ContentGenerationService.generate_social_post(
            db=db,
            platform=config.get("platform", "facebook"),
            topic=config.get("topic", ""),
            tone=config.get("tone", "professional"),
            max_length=config.get("max_length", 500),
            include_hashtags=config.get("include_hashtags", True),
            created_by=created_by,
        )
        
        return result
    
    @staticmethod
    async def get_workflow_history(
        workflow_id: UUID,
        limit: int = 10,
    ) -> List[Dict]:
        """Get workflow execution history."""
        history = [
            record for record in AutomationService._workflow_history
            if record["workflow_id"] == str(workflow_id)
        ]
        return history[-limit:]
