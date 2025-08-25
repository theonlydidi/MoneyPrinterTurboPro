-- Database Schema for MoneyPrinterTurboPro
-- PostgreSQL database schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS video_requests (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    duration INTEGER NOT NULL CHECK (duration >= 5 AND duration <= 600),
    style VARCHAR(50) NOT NULL,
    quality VARCHAR(50) NOT NULL,
    voice_preset VARCHAR(50) NOT NULL,
    background_music BOOLEAN DEFAULT TRUE,
    music_intensity VARCHAR(20) DEFAULT 'medium',
    aspect_ratio VARCHAR(10) DEFAULT '16:9',
    transitions VARCHAR(50) DEFAULT 'fade',
    ai_model VARCHAR(100) DEFAULT 'gpt-4',
    language VARCHAR(5) DEFAULT 'en',
    custom_prompts JSONB,
    exclude_keywords JSONB,
    include_subtitles BOOLEAN DEFAULT TRUE,
    tags JSONB,
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    video_path TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_video_requests_user_id ON video_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_video_requests_status ON video_requests(status);
CREATE INDEX IF NOT EXISTS idx_video_requests_created_at ON video_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_video_requests_style ON video_requests(style);
CREATE INDEX IF NOT EXISTS idx_video_requests_quality ON video_requests(quality);

-- Video templates table
CREATE TABLE IF NOT EXISTS video_templates (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    style VARCHAR(50) NOT NULL,
    quality VARCHAR(50) NOT NULL,
    voice_preset VARCHAR(50) NOT NULL,
    background_music BOOLEAN DEFAULT TRUE,
    music_intensity VARCHAR(20) DEFAULT 'medium',
    aspect_ratio VARCHAR(10) DEFAULT '16:9',
    transitions VARCHAR(50) DEFAULT 'fade',
    ai_model VARCHAR(100) DEFAULT 'gpt-4',
    language VARCHAR(5) DEFAULT 'en',
    custom_prompts JSONB,
    exclude_keywords JSONB,
    include_subtitles BOOLEAN DEFAULT TRUE,
    tags JSONB,
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for templates
CREATE INDEX IF NOT EXISTS idx_video_templates_user_id ON video_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_video_templates_style ON video_templates(style);
CREATE INDEX IF NOT EXISTS idx_video_templates_category ON video_templates(category);

-- Video analytics table
CREATE TABLE IF NOT EXISTS video_analytics (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES video_requests(id) ON DELETE CASCADE,
    user_id VARCHAR(255),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    watch_time INTEGER DEFAULT 0, -- in seconds
    completion_rate DECIMAL(5,2) DEFAULT 0.0, -- percentage
    engagement_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100 scale
    demographics JSONB, -- age, gender, etc.
    geographic_data JSONB, -- country, region, city
    device_data JSONB, -- device type, browser, OS
    tracked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for analytics
CREATE INDEX IF NOT EXISTS idx_video_analytics_video_id ON video_analytics(video_id);
CREATE INDEX IF NOT EXISTS idx_video_analytics_user_id ON video_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_video_analytics_tracked_at ON video_analytics(tracked_at);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    default_style VARCHAR(50) DEFAULT 'professional',
    default_quality VARCHAR(50) DEFAULT 'high',
    default_voice_preset VARCHAR(50) DEFAULT 'professional',
    default_language VARCHAR(5) DEFAULT 'en',
    notification_settings JSONB,
    storage_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for user preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time DECIMAL(10,3), -- in seconds
    request_size INTEGER, -- in bytes
    response_size INTEGER, -- in bytes
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for API usage
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_status_code ON api_usage(status_code);

-- Error logging table
CREATE TABLE IF NOT EXISTS error_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_data JSONB,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for error logs
CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);

-- Storage files table
CREATE TABLE IF NOT EXISTS storage_files (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100),
    mime_type VARCHAR(100),
    storage_provider VARCHAR(50) NOT NULL,
    storage_url TEXT,
    metadata JSONB,
    user_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for storage files
CREATE INDEX IF NOT EXISTS idx_storage_files_file_path ON storage_files(file_path);
CREATE INDEX IF NOT EXISTS idx_storage_files_user_id ON storage_files(user_id);
CREATE INDEX IF NOT EXISTS idx_storage_files_storage_provider ON storage_files(storage_provider);
CREATE INDEX IF NOT EXISTS idx_storage_files_created_at ON storage_files(created_at);

-- Batch processing table
CREATE TABLE IF NOT EXISTS batch_processes (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    batch_id VARCHAR(255) UNIQUE NOT NULL,
    total_videos INTEGER NOT NULL,
    completed_videos INTEGER DEFAULT 0,
    failed_videos INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'processing',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for batch processes
CREATE INDEX IF NOT EXISTS idx_batch_processes_user_id ON batch_processes(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_processes_batch_id ON batch_processes(batch_id);
CREATE INDEX IF NOT EXISTS idx_batch_processes_status ON batch_processes(status);

-- Batch video items table
CREATE TABLE IF NOT EXISTS batch_video_items (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(255) REFERENCES batch_processes(batch_id) ON DELETE CASCADE,
    video_request_id INTEGER REFERENCES video_requests(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    result_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for batch video items
CREATE INDEX IF NOT EXISTS idx_batch_video_items_batch_id ON batch_video_items(batch_id);
CREATE INDEX IF NOT EXISTS idx_batch_video_items_video_request_id ON batch_video_items(video_request_id);
CREATE INDEX IF NOT EXISTS idx_batch_video_items_status ON batch_video_items(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_video_requests_updated_at 
    BEFORE UPDATE ON video_requests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_templates_updated_at 
    BEFORE UPDATE ON video_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_processes_updated_at 
    BEFORE UPDATE ON batch_processes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_video_items_updated_at 
    BEFORE UPDATE ON batch_video_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW video_generation_stats AS
SELECT 
    DATE(created_at) as generation_date,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_videos,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_videos,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_videos,
    AVG(CASE WHEN status = 'completed' THEN 
        (metadata->>'generation_time')::DECIMAL 
    END) as avg_generation_time,
    AVG(CASE WHEN status = 'completed' THEN 
        (metadata->>'final_duration')::DECIMAL 
    END) as avg_video_duration
FROM video_requests 
GROUP BY DATE(created_at)
ORDER BY generation_date DESC;

-- Create view for user statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    user_id,
    COUNT(*) as total_videos,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_videos,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_videos,
    AVG(CASE WHEN status = 'completed' THEN 
        (metadata->>'generation_time')::DECIMAL 
    END) as avg_generation_time,
    SUM(CASE WHEN status = 'completed' THEN 
        (metadata->>'final_size')::BIGINT 
    END) as total_storage_used,
    MAX(created_at) as last_activity
FROM video_requests 
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY total_videos DESC;

-- Create view for quality and style distribution
CREATE OR REPLACE VIEW quality_style_distribution AS
SELECT 
    quality,
    style,
    COUNT(*) as count,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
    AVG(CASE WHEN status = 'completed' THEN 
        (metadata->>'generation_time')::DECIMAL 
    END) as avg_generation_time
FROM video_requests 
GROUP BY quality, style
ORDER BY count DESC;

-- Insert some default data
INSERT INTO video_templates (name, description, style, quality, voice_preset, language) VALUES
('Professional Business', 'Professional business video template with clean design', 'professional', 'high', 'professional', 'en'),
('Creative Marketing', 'Creative marketing video template with vibrant colors', 'creative', 'high', 'friendly', 'en'),
('Minimalist Presentation', 'Minimalist presentation template with simple design', 'minimalist', 'medium', 'professional', 'en'),
('Educational Content', 'Educational content template with clear typography', 'educational', 'high', 'clear', 'en')
ON CONFLICT DO NOTHING;

-- Create function to get video statistics
CREATE OR REPLACE FUNCTION get_video_statistics(
    p_user_id VARCHAR DEFAULT NULL,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
)
RETURNS TABLE(
    total_videos BIGINT,
    completed_videos BIGINT,
    failed_videos BIGINT,
    processing_videos BIGINT,
    avg_generation_time DECIMAL,
    total_storage_used BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_videos,
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::BIGINT as completed_videos,
        COUNT(CASE WHEN status = 'failed' THEN 1 END)::BIGINT as failed_videos,
        COUNT(CASE WHEN status = 'processing' THEN 1 END)::BIGINT as processing_videos,
        AVG(CASE WHEN status = 'completed' THEN 
            (metadata->>'generation_time')::DECIMAL 
        END) as avg_generation_time,
        SUM(CASE WHEN status = 'completed' THEN 
            (metadata->>'final_size')::BIGINT 
        END) as total_storage_used
    FROM video_requests 
    WHERE (p_user_id IS NULL OR user_id = p_user_id)
        AND (p_start_date IS NULL OR created_at >= p_start_date)
        AND (p_end_date IS NULL OR created_at <= p_end_date);
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_user;
