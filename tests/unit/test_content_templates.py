"""Tests for content template service."""
import pytest
from app.services.content_template_service import ContentTemplateService
from app.schemas.content_template import (
    ContentTemplateCreate,
    ContentTemplateUpdate,
)


@pytest.fixture
def template_service(test_db):
    """Create content template service instance."""
    return ContentTemplateService(test_db)


@pytest.mark.asyncio
async def test_create_template(template_service):
    """Test template creation."""
    template_data = ContentTemplateCreate(
        name="Social Media Post Template",
        content_type="social_post",
        template_text="Check out our latest update: {{topic}}. {{description}} #{{hashtag}}",
        variables=["topic", "description", "hashtag"],
        category="social_media",
    )

    template = await template_service.create_template(template_data, user_id="test-user")

    assert template is not None
    assert template.name == "Social Media Post Template"
    assert len(template.variables) == 3
    assert template.created_by == "test-user"


@pytest.mark.asyncio
async def test_get_template(template_service):
    """Test retrieving a template."""
    # Create template
    template_data = ContentTemplateCreate(
        name="Test Template",
        content_type="article",
        template_text="Title: {{title}}\n\nContent: {{content}}",
        variables=["title", "content"],
    )
    created_template = await template_service.create_template(template_data, user_id="test-user")

    # Retrieve template
    template = await template_service.get_template(created_template.id)

    assert template is not None
    assert template.id == created_template.id
    assert template.name == "Test Template"


@pytest.mark.asyncio
async def test_apply_template(template_service):
    """Test applying template with variables."""
    # Create template
    template_data = ContentTemplateCreate(
        name="Welcome Template",
        content_type="email",
        template_text="Hello {{name}}, welcome to {{organization}}!",
        variables=["name", "organization"],
    )
    template = await template_service.create_template(template_data, user_id="test-user")

    # Apply template
    variables = {
        "name": "John",
        "organization": "Mission Engadi",
    }
    result = await template_service.apply_template(template.id, variables)

    assert result is not None
    assert "Hello John" in result
    assert "Mission Engadi" in result


@pytest.mark.asyncio
async def test_list_templates(template_service):
    """Test listing templates."""
    # Create multiple templates
    for i in range(3):
        template_data = ContentTemplateCreate(
            name=f"Template {i}",
            content_type="social_post",
            template_text=f"Content {i}: {{{{topic}}}}",
            variables=["topic"],
        )
        await template_service.create_template(template_data, user_id="test-user")

    # List templates
    templates = await template_service.list_templates(
        content_type="social_post",
        skip=0,
        limit=10,
    )

    assert len(templates) == 3


@pytest.mark.asyncio
async def test_update_template(template_service):
    """Test updating a template."""
    # Create template
    template_data = ContentTemplateCreate(
        name="Original Template",
        content_type="article",
        template_text="Original content",
        variables=[],
    )
    template = await template_service.create_template(template_data, user_id="test-user")

    # Update template
    update_data = ContentTemplateUpdate(
        name="Updated Template",
        template_text="Updated content: {{new_variable}}",
        variables=["new_variable"],
    )
    updated_template = await template_service.update_template(template.id, update_data)

    assert updated_template.name == "Updated Template"
    assert "new_variable" in updated_template.variables


@pytest.mark.asyncio
async def test_delete_template(template_service):
    """Test deleting a template."""
    # Create template
    template_data = ContentTemplateCreate(
        name="To Delete",
        content_type="social_post",
        template_text="Content",
        variables=[],
    )
    template = await template_service.create_template(template_data, user_id="test-user")

    # Delete template
    result = await template_service.delete_template(template.id)

    assert result is True

    # Verify deletion
    deleted_template = await template_service.get_template(template.id)
    assert deleted_template is None


@pytest.mark.asyncio
async def test_suggest_templates(template_service, mock_abacus_client):
    """Test template suggestions."""
    suggestions = await template_service.suggest_templates(
        content_type="social_post",
        context="Mission updates for social media",
    )

    assert suggestions is not None
    assert "suggestions" in suggestions
    assert len(suggestions["suggestions"]) > 0
