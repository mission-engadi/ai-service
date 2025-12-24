"""Tests for translation service."""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.translation_service import TranslationService
from app.schemas.translation import (
    TranslationRequest,
    BatchTranslationRequest,
)


@pytest.fixture
def translation_service(test_db):
    """Create translation service instance."""
    return TranslationService(test_db)


@pytest.mark.asyncio
async def test_translate_text(translation_service, mock_abacus_client):
    """Test single text translation."""
    request = TranslationRequest(
        text="Hello, welcome to our mission",
        source_language="en",
        target_language="es",
    )

    result = await translation_service.translate_text(request, user_id="test-user")

    assert result is not None
    assert "translated_text" in result
    assert "target_language" in result
    assert result["target_language"] == "es"
    assert "[ES]" in result["translated_text"]


@pytest.mark.asyncio
async def test_batch_translation(translation_service, mock_abacus_client):
    """Test batch translation."""
    request = BatchTranslationRequest(
        texts=["Hello", "Welcome", "Thank you"],
        source_language="en",
        target_languages=["es", "fr"],
    )

    result = await translation_service.translate_batch(request, user_id="test-user")

    assert result is not None
    assert "translations" in result
    assert len(result["translations"]) == 3


@pytest.mark.asyncio
async def test_detect_language(translation_service, mock_abacus_client):
    """Test language detection."""
    text = "Bonjour, bienvenue à notre mission"

    result = await translation_service.detect_language(text)

    assert result is not None
    assert "language" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_auto_translate_workflow(translation_service, mock_abacus_client):
    """Test auto-translation workflow."""
    content_id = "test-content-123"
    target_languages = ["es", "fr", "pt"]

    result = await translation_service.auto_translate_workflow(
        content_id=content_id,
        target_languages=target_languages,
        user_id="test-user",
    )

    assert result is not None
    assert "workflow_id" in result
    assert "status" in result
    assert len(result["translations"]) == 3


@pytest.mark.asyncio
async def test_translation_quality_check(translation_service, mock_abacus_client):
    """Test translation quality scoring."""
    original = "Hello, welcome to our mission"
    translated = "Hola, bienvenido a nuestra misión"

    quality_score = await translation_service.check_translation_quality(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="es",
    )

    assert quality_score is not None
    assert 0 <= quality_score <= 1
