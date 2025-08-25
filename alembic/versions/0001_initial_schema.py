"""Initial database schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create video_requests table
    op.create_table('video_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=False),
        sa.Column('quality', sa.String(length=50), nullable=False),
        sa.Column('voice_preset', sa.String(length=50), nullable=False),
        sa.Column('background_music', sa.Boolean(), nullable=True),
        sa.Column('music_intensity', sa.String(length=20), nullable=True),
        sa.Column('aspect_ratio', sa.String(length=10), nullable=True),
        sa.Column('transitions', sa.String(length=50), nullable=True),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('language', sa.String(length=5), nullable=True),
        sa.Column('custom_prompts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('exclude_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('include_subtitles', sa.Boolean(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('video_path', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create video_templates table
    op.create_table('video_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('style', sa.String(length=50), nullable=False),
        sa.Column('quality', sa.String(length=50), nullable=False),
        sa.Column('voice_preset', sa.String(length=50), nullable=False),
        sa.Column('background_music', sa.Boolean(), nullable=True),
        sa.Column('music_intensity', sa.String(length=20), nullable=True),
        sa.Column('aspect_ratio', sa.String(length=10), nullable=True),
        sa.Column('transitions', sa.String(length=50), nullable=True),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('language', sa.String(length=5), nullable=True),
        sa.Column('custom_prompts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('exclude_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('include_subtitles', sa.Boolean(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create video_analytics table
    op.create_table('video_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('shares', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Integer(), nullable=True),
        sa.Column('watch_time', sa.Integer(), nullable=True),
        sa.Column('completion_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('engagement_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('demographics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('geographic_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('device_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tracked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['video_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('default_style', sa.String(length=50), nullable=True),
        sa.Column('default_quality', sa.String(length=50), nullable=True),
        sa.Column('default_voice_preset', sa.String(length=50), nullable=True),
        sa.Column('default_language', sa.String(length=5), nullable=True),
        sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('storage_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create api_usage table
    op.create_table('api_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('endpoint', sa.String(length=200), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_time', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('request_size', sa.Integer(), nullable=True),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create error_logs table
    op.create_table('error_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('error_type', sa.String(length=100), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('request_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create storage_files table
    op.create_table('storage_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('storage_provider', sa.String(length=50), nullable=False),
        sa.Column('storage_url', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create batch_processes table
    op.create_table('batch_processes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('batch_id', sa.String(length=255), nullable=False),
        sa.Column('total_videos', sa.Integer(), nullable=False),
        sa.Column('completed_videos', sa.Integer(), nullable=True),
        sa.Column('failed_videos', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_id')
    )
    
    # Create batch_video_items table
    op.create_table('batch_video_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.String(length=255), nullable=True),
        sa.Column('video_request_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batch_processes.batch_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_request_id'], ['video_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_video_requests_user_id', 'video_requests', ['user_id'])
    op.create_index('idx_video_requests_status', 'video_requests', ['status'])
    op.create_index('idx_video_requests_created_at', 'video_requests', ['created_at'])
    op.create_index('idx_video_requests_style', 'video_requests', ['style'])
    op.create_index('idx_video_requests_quality', 'video_requests', ['quality'])
    
    op.create_index('idx_video_templates_user_id', 'video_templates', ['user_id'])
    op.create_index('idx_video_templates_style', 'video_templates', ['style'])
    op.create_index('idx_video_templates_category', 'video_templates', ['category'])
    
    op.create_index('idx_video_analytics_video_id', 'video_analytics', ['video_id'])
    op.create_index('idx_video_analytics_user_id', 'video_analytics', ['user_id'])
    op.create_index('idx_video_analytics_tracked_at', 'video_analytics', ['tracked_at'])
    
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])
    
    op.create_index('idx_api_usage_user_id', 'api_usage', ['user_id'])
    op.create_index('idx_api_usage_endpoint', 'api_usage', ['endpoint'])
    op.create_index('idx_api_usage_created_at', 'api_usage', ['created_at'])
    op.create_index('idx_api_usage_status_code', 'api_usage', ['status_code'])
    
    op.create_index('idx_error_logs_user_id', 'error_logs', ['user_id'])
    op.create_index('idx_error_logs_error_type', 'error_logs', ['error_type'])
    op.create_index('idx_error_logs_created_at', 'error_logs', ['created_at'])
    
    op.create_index('idx_storage_files_file_path', 'storage_files', ['file_path'])
    op.create_index('idx_storage_files_user_id', 'storage_files', ['user_id'])
    op.create_index('idx_storage_files_storage_provider', 'storage_files', ['storage_provider'])
    op.create_index('idx_storage_files_created_at', 'storage_files', ['created_at'])
    
    op.create_index('idx_batch_processes_user_id', 'batch_processes', ['user_id'])
    op.create_index('idx_batch_processes_batch_id', 'batch_processes', ['batch_id'])
    op.create_index('idx_batch_processes_status', 'batch_processes', ['status'])
    
    op.create_index('idx_batch_video_items_batch_id', 'batch_video_items', ['batch_id'])
    op.create_index('idx_batch_video_items_video_request_id', 'batch_video_items', ['video_request_id'])
    op.create_index('idx_batch_video_items_status', 'batch_video_items', ['status'])
    
    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create triggers
    op.execute("""
        CREATE TRIGGER update_video_requests_updated_at 
            BEFORE UPDATE ON video_requests 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_video_templates_updated_at 
            BEFORE UPDATE ON video_templates 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_user_preferences_updated_at 
            BEFORE UPDATE ON user_preferences 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_batch_processes_updated_at 
            BEFORE UPDATE ON batch_processes 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_batch_video_items_updated_at 
            BEFORE UPDATE ON batch_video_items 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Insert default templates
    op.execute("""
        INSERT INTO video_templates (name, description, style, quality, voice_preset, language) VALUES
        ('Professional Business', 'Professional business video template with clean design', 'professional', 'high', 'professional', 'en'),
        ('Creative Marketing', 'Creative marketing video template with vibrant colors', 'creative', 'high', 'friendly', 'en'),
        ('Minimalist Presentation', 'Minimalist presentation template with simple design', 'minimalist', 'medium', 'professional', 'en'),
        ('Educational Content', 'Educational content template with clear typography', 'educational', 'high', 'clear', 'en')
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_batch_video_items_updated_at ON batch_video_items")
    op.execute("DROP TRIGGER IF EXISTS update_batch_processes_updated_at ON batch_processes")
    op.execute("DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences")
    op.execute("DROP TRIGGER IF EXISTS update_video_templates_updated_at ON video_templates")
    op.execute("DROP TRIGGER IF EXISTS update_video_requests_updated_at ON video_requests")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop tables
    op.drop_table('batch_video_items')
    op.drop_table('batch_processes')
    op.drop_table('storage_files')
    op.drop_table('error_logs')
    op.drop_table('api_usage')
    op.drop_table('user_preferences')
    op.drop_table('video_analytics')
    op.drop_table('video_templates')
    op.drop_table('video_requests')
