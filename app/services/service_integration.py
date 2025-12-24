"""Service Integration.

Provides HTTP client for calling other microservices.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
from httpx import AsyncClient, Response

from app.core.config import settings

logger = logging.getLogger(__name__)


class ServiceIntegrationClient:
    """HTTP client for microservice integration."""
    
    def __init__(self):
        """Initialize service integration client."""
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.auth_service_url = settings.AUTH_SERVICE_URL
        self.content_service_url = settings.CONTENT_SERVICE_URL
        self.social_media_service_url = settings.SOCIAL_MEDIA_SERVICE_URL
        self.notification_service_url = settings.NOTIFICATION_SERVICE_URL
        self.partners_crm_service_url = settings.PARTNERS_CRM_SERVICE_URL
        self.projects_service_url = settings.PROJECTS_SERVICE_URL
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        json: Optional[Dict] = None,
        auth_token: Optional[str] = None,
    ) -> Response:
        """Make HTTP request to a service."""
        if headers is None:
            headers = {}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
            )
            response.raise_for_status()
            return response
    
    # Content Service Integration
    
    async def publish_to_content_service(
        self,
        content_data: Dict,
        auth_token: str,
    ) -> Dict:
        """Publish generated content to Content Service.
        
        Args:
            content_data: Content data to publish
            auth_token: User auth token
            
        Returns:
            Published content info
        """
        try:
            url = f"{self.content_service_url}/api/v1/content"
            response = await self._make_request(
                method="POST",
                url=url,
                json=content_data,
                auth_token=auth_token,
            )
            logger.info("Published content to Content Service")
            return response.json()
        except Exception as e:
            logger.error(f"Error publishing to Content Service: {e}")
            raise
    
    # Social Media Service Integration
    
    async def publish_to_social_media(
        self,
        platform: str,
        content: str,
        media_urls: Optional[list],
        schedule_time: Optional[str],
        auth_token: str,
    ) -> Dict:
        """Publish content to Social Media Service.
        
        Args:
            platform: Social media platform
            content: Post content
            media_urls: Media URLs
            schedule_time: Scheduled publish time
            auth_token: User auth token
            
        Returns:
            Published post info
        """
        try:
            url = f"{self.social_media_service_url}/api/v1/posts"
            response = await self._make_request(
                method="POST",
                url=url,
                json={
                    "platform": platform,
                    "content": content,
                    "media_urls": media_urls or [],
                    "schedule_time": schedule_time,
                },
                auth_token=auth_token,
            )
            logger.info(f"Published to {platform} via Social Media Service")
            return response.json()
        except Exception as e:
            logger.error(f"Error publishing to Social Media Service: {e}")
            raise
    
    # Notification Service Integration
    
    async def send_via_notification_service(
        self,
        notification_type: str,
        recipients: list,
        subject: str,
        content: str,
        auth_token: str,
    ) -> Dict:
        """Send content via Notification Service.
        
        Args:
            notification_type: Type (email, sms, push)
            recipients: List of recipient IDs or emails
            subject: Notification subject
            content: Notification content
            auth_token: User auth token
            
        Returns:
            Notification send info
        """
        try:
            url = f"{self.notification_service_url}/api/v1/notifications"
            response = await self._make_request(
                method="POST",
                url=url,
                json={
                    "type": notification_type,
                    "recipients": recipients,
                    "subject": subject,
                    "content": content,
                },
                auth_token=auth_token,
            )
            logger.info("Sent notification via Notification Service")
            return response.json()
        except Exception as e:
            logger.error(f"Error sending via Notification Service: {e}")
            raise
    
    # Partners CRM Service Integration
    
    async def get_partner_data(
        self,
        partner_id: UUID,
        auth_token: str,
    ) -> Dict:
        """Get partner data from Partners CRM Service.
        
        Args:
            partner_id: Partner UUID
            auth_token: User auth token
            
        Returns:
            Partner data
        """
        try:
            url = f"{self.partners_crm_service_url}/api/v1/partners/{partner_id}"
            response = await self._make_request(
                method="GET",
                url=url,
                auth_token=auth_token,
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching partner data: {e}")
            raise
    
    # Projects Service Integration
    
    async def get_project_data(
        self,
        project_id: UUID,
        auth_token: str,
    ) -> Dict:
        """Get project data from Projects Service.
        
        Args:
            project_id: Project UUID
            auth_token: User auth token
            
        Returns:
            Project data
        """
        try:
            url = f"{self.projects_service_url}/api/v1/projects/{project_id}"
            response = await self._make_request(
                method="GET",
                url=url,
                auth_token=auth_token,
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching project data: {e}")
            raise


# Global client instance
service_integration = ServiceIntegrationClient()
