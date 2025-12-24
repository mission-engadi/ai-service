"""Tests for content generation service."""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.content_generation_service import ContentGenerationService
from app.schemas.content_generation import (
    SocialPostGenerationRequest,
    ArticleGenerationRequest,
    DonorCommunicationRequest,
)


@pytest.fixture
def content_service(test_db):
    """Create content generation service instance."""
    return ContentGenerationService(test_db)


@pytest.mark.asyncio
async def test_generate_social_post(content_service, mock_abacus_client):
    """Test social media post generation."""
    request = SocialPostGenerationRequest(
        topic="Mission Update",
        platform="twitter",
        tone="professional",
        language="en",
        include_hashtags=True,
    )

    result = await content_service.generate_social_post(request, user_id="test-user")

    assert result is not None
    assert "content" in result
    assert "metadata" in result
    assert result["platform"] == "twitter"
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_generate_article(content_service, mock_abacus_client):
    """Test article generation."""
    request = ArticleGenerationRequest(
        topic="Digital Ministry in Modern Missions",
        tone="informative",
        length="medium",
        language="en",
        keywords=["digital", "ministry", "missions"],
    )

    result = await content_service.generate_article(request, user_id="test-user")

    assert result is not None
    assert "title" in result
    assert "content" in result
    assert "metadata" in result
    assert len(result["content"]) > 100


@pytest.mark.asyncio
async def test_generate_donor_communication(content_service, mock_abacus_client):
    """Test donor communication generation."""
    request = DonorCommunicationRequest(
        communication_type="thank_you",
        donor_name="John Smith",
        donation_amount=100.0,
        tone="warm",
        language="en",
    )

    result = await content_service.generate_donor_communication(request, user_id="test-user")

    assert result is not None
    assert "content" in result
    assert "John Smith" in result["content"]
    assert result["communication_type"] == "thank_you"


@pytest.mark.asyncio
async def test_batch_generation(content_service, mock_abacus_client):
    """Test batch content generation."""
    requests = [
        SocialPostGenerationRequest(
            topic=f"Update {i}",
            platform="twitter",
            tone="professional",
            language="en",
        )
        for i in range(3)
    ]

    results = await content_service.generate_batch(requests, user_id="test-user")

    assert len(results) == 3
    for result in results:
        assert "content" in result
        assert "platform" in result
