"""Initial migration: AI Task, Generated Content, Content Template, Translation Job

Revision ID: 143773deba39
Revises: 
Create Date: 2025-12-24 19:53:16.066317+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '143773deba39'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    
    # Create enums
    task_type_enum = sa.Enum(
        'content_generation',
        'translation',
        'image_generation',
        'content_enhancement',
        'automation',
        name='tasktype'
    )
    task_status_enum = sa.Enum(
        'pending',
        'processing',
        'completed',
        'failed',
        'cancelled',
        name='taskstatus'
    )
    content_type_enum = sa.Enum(
        'social_post',
        'article',
        'story',
        'donor_letter',
        'newsletter',
        'prayer_request',
        'campaign_copy',
        name='contenttype'
    )
    translation_status_enum = sa.Enum(
        'pending',
        'processing',
        'completed',
        'failed',
        name='translationstatus'
    )
    
    task_type_enum.create(op.get_bind())
    task_status_enum.create(op.get_bind())
    content_type_enum.create(op.get_bind())
    translation_status_enum.create(op.get_bind())
    
    # Create ai_tasks table
    op.create_table(
        'ai_tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('task_type', task_type_enum, nullable=False),
        sa.Column('status', task_status_enum, nullable=False, server_default='pending'),
        sa.Column('input_data', JSONB, nullable=False),
        sa.Column('output_data', JSONB, nullable=True),
        sa.Column('prompt', sa.Text, nullable=True),
        sa.Column('model_used', sa.String(255), nullable=True),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('processing_time', sa.Float, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('requires_approval', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('approved', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('approved_by', UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for ai_tasks
    op.create_index('ix_ai_tasks_id', 'ai_tasks', ['id'])
    op.create_index('ix_ai_tasks_task_type', 'ai_tasks', ['task_type'])
    op.create_index('ix_ai_tasks_status', 'ai_tasks', ['status'])
    op.create_index('ix_ai_tasks_created_by', 'ai_tasks', ['created_by'])
    
    # Create generated_content table
    op.create_table(
        'generated_content',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('ai_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_type', content_type_enum, nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('platform', sa.String(50), nullable=True),
        sa.Column('content_metadata', JSONB, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('published', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('external_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for generated_content
    op.create_index('ix_generated_content_id', 'generated_content', ['id'])
    op.create_index('ix_generated_content_task_id', 'generated_content', ['task_id'])
    op.create_index('ix_generated_content_content_type', 'generated_content', ['content_type'])
    op.create_index('ix_generated_content_language', 'generated_content', ['language'])
    op.create_index('ix_generated_content_platform', 'generated_content', ['platform'])
    op.create_index('ix_generated_content_external_id', 'generated_content', ['external_id'])
    
    # Create content_templates table
    op.create_table(
        'content_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('template_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('prompt_template', sa.Text, nullable=False),
        sa.Column('variables', sa.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('platform', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for content_templates
    op.create_index('ix_content_templates_id', 'content_templates', ['id'])
    op.create_index('ix_content_templates_name', 'content_templates', ['name'])
    op.create_index('ix_content_templates_template_type', 'content_templates', ['template_type'])
    op.create_index('ix_content_templates_language', 'content_templates', ['language'])
    op.create_index('ix_content_templates_platform', 'content_templates', ['platform'])
    op.create_index('ix_content_templates_is_active', 'content_templates', ['is_active'])
    op.create_index('ix_content_templates_created_by', 'content_templates', ['created_by'])
    
    # Create translation_jobs table
    op.create_table(
        'translation_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('ai_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_language', sa.String(10), nullable=False),
        sa.Column('target_language', sa.String(10), nullable=False),
        sa.Column('source_text', sa.Text, nullable=False),
        sa.Column('translated_text', sa.Text, nullable=True),
        sa.Column('status', translation_status_enum, nullable=False, server_default='pending'),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for translation_jobs
    op.create_index('ix_translation_jobs_id', 'translation_jobs', ['id'])
    op.create_index('ix_translation_jobs_task_id', 'translation_jobs', ['task_id'])
    op.create_index('ix_translation_jobs_source_language', 'translation_jobs', ['source_language'])
    op.create_index('ix_translation_jobs_target_language', 'translation_jobs', ['target_language'])
    op.create_index('ix_translation_jobs_status', 'translation_jobs', ['status'])


def downgrade() -> None:
    """Downgrade database schema."""
    
    # Drop tables
    op.drop_table('translation_jobs')
    op.drop_table('content_templates')
    op.drop_table('generated_content')
    op.drop_table('ai_tasks')
    
    # Drop enums
    sa.Enum(name='translationstatus').drop(op.get_bind())
    sa.Enum(name='contenttype').drop(op.get_bind())
    sa.Enum(name='taskstatus').drop(op.get_bind())
    sa.Enum(name='tasktype').drop(op.get_bind())
