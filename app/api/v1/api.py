"""API router configuration.

This module aggregates all API routers for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_tasks,
    automation,
    content_enhancement,
    content_generation,
    content_templates,
    examples,
    generated_content,
    health,
    image_generation,
    translation,
)

api_router = APIRouter()

# Include all endpoint routers

# Health check endpoints
api_router.include_router(
    health.router,
    tags=["health"],
)

# Content Generation endpoints
api_router.include_router(
    content_generation.router,
    tags=["content-generation"],
)

# Translation endpoints
api_router.include_router(
    translation.router,
    tags=["translation"],
)

# Image Generation endpoints
api_router.include_router(
    image_generation.router,
    tags=["image-generation"],
)

# Content Enhancement endpoints
api_router.include_router(
    content_enhancement.router,
    tags=["content-enhancement"],
)

# Automation endpoints
api_router.include_router(
    automation.router,
    tags=["automation"],
)

# AI Tasks endpoints
api_router.include_router(
    ai_tasks.router,
    tags=["ai-tasks"],
)

# Content Templates endpoints
api_router.include_router(
    content_templates.router,
    tags=["content-templates"],
)

# Generated Content endpoints
api_router.include_router(
    generated_content.router,
    tags=["generated-content"],
)

# Examples (for reference)
api_router.include_router(
    examples.router,
    prefix="/examples",
    tags=["examples"],
)
