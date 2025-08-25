"""
Tests for Video Generator Service
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from app.services.video_generator import VideoGeneratorService
from app.models.video import VideoRequest, VideoStyle, VideoQuality, VoicePreset, TransitionType


@pytest.fixture
def mock_services():
    """Mock all services"""
    with patch('app.services.video_generator.AIService') as mock_ai, \
         patch('app.services.video_generator.VoiceService') as mock_voice, \
         patch('app.services.video_generator.SubtitleService') as mock_subtitle, \
         patch('app.services.video_generator.MusicService') as mock_music, \
         patch('app.services.video_generator.EffectsService') as mock_effects, \
         patch('app.services.video_generator.StorageManager') as mock_storage, \
         patch('app.services.video_generator.DatabaseService') as mock_db, \
         patch('app.services.video_generator.MonitoringService') as mock_monitoring, \
         patch('app.services.video_generator.VideoUtils') as mock_utils:
        
        # Configure mock services
        mock_ai.return_value = Mock()
        mock_voice.return_value = Mock()
        mock_subtitle.return_value = Mock()
        mock_music.return_value = Mock()
        mock_effects.return_value = Mock()
        mock_storage.return_value = Mock()
        mock_db.return_value = Mock()
        mock_monitoring.return_value = Mock()
        mock_utils.return_value = Mock()
        
        yield {
            'ai': mock_ai.return_value,
            'voice': mock_voice.return_value,
            'subtitle': mock_subtitle.return_value,
            'music': mock_music.return_value,
            'effects': mock_effects.return_value,
            'storage': mock_storage.return_value,
            'db': mock_db.return_value,
            'monitoring': mock_monitoring.return_value,
            'utils': mock_utils.return_value
        }


@pytest.fixture
def sample_video_request():
    """Sample video request for testing"""
    return VideoRequest(
        title="Test Video",
        description="This is a test video description for testing purposes.",
        duration=30,
        style=VideoStyle.PROFESSIONAL,
        quality=VideoQuality.HIGH,
        voice_preset=VoicePreset.PROFESSIONAL,
        background_music=True,
        music_intensity="medium",
        aspect_ratio="16:9",
        transitions=TransitionType.FADE,
        ai_model="gpt-4",
        language="en",
        include_subtitles=True
    )


@pytest.fixture
def video_generator(mock_services):
    """Video generator service with mocked dependencies"""
    # Mock settings
    with patch('app.services.video_generator.settings') as mock_settings:
        mock_settings.performance.max_concurrent_generations = 5
        mock_settings.quality_presets = {
            VideoQuality.HIGH: {'fps': 30, 'codec': 'libx264', 'preset': 'medium', 'bitrate': '5000k'}
        }
        mock_settings.style_presets = {
            VideoStyle.PROFESSIONAL: {'filters': ['enhance'], 'animations': ['subtle']}
        }
        
        generator = VideoGeneratorService()
        
        # Mock the services
        generator.ai_service = mock_services['ai']
        generator.voice_service = mock_services['voice']
        generator.subtitle_service = mock_services['voice']
        generator.music_service = mock_services['music']
        generator.effects_service = mock_services['effects']
        generator.storage_manager = mock_services['storage']
        generator.database_service = mock_services['db']
        generator.monitoring_service = mock_services['monitoring']
        generator.video_utils = mock_services['utils']
        
        return generator


class TestVideoGeneratorService:
    """Test cases for VideoGeneratorService"""
    
    def test_initialization(self, mock_services):
        """Test service initialization"""
        with patch('app.services.video_generator.settings') as mock_settings:
            mock_settings.performance.max_concurrent_generations = 5
            mock_settings.quality_presets = {}
            mock_settings.style_presets = {}
            
            generator = VideoGeneratorService()
            
            assert generator.ai_service is not None
            assert generator.voice_service is not None
            assert generator.subtitle_service is not None
            assert generator.music_service is not None
            assert generator.effects_service is not None
            assert generator.storage_manager is not None
            assert generator.database_service is not None
            assert generator.monitoring_service is not None
            assert generator.video_utils is not None
    
    def test_setup_directories(self, video_generator):
        """Test directory setup"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            video_generator._setup_directories()
            
            # Should create all necessary directories
            assert mock_mkdir.call_count > 0
    
    def test_load_generation_config(self, video_generator):
        """Test generation config loading"""
        with patch('app.services.video_generator.settings') as mock_settings:
            mock_settings.performance.max_concurrent_generations = 10
            mock_settings.quality_presets = {'test': 'value'}
            mock_settings.style_presets = {'test': 'value'}
            
            video_generator._load_generation_config()
            
            assert video_generator.generation_config['max_concurrent_generations'] == 10
            assert 'quality_presets' in video_generator.generation_config
            assert 'style_presets' in video_generator.generation_config
    
    @pytest.mark.asyncio
    async def test_generate_video_success(self, video_generator, sample_video_request, mock_services):
        """Test successful video generation"""
        # Mock successful responses from all services
        mock_services['db'].save_video_request.return_value = {
            'success': True, 'request_id': 1
        }
        mock_services['db'].update_video_status.return_value = {'success': True}
        
        mock_services['ai'].generate_script.return_value = {
            'success': True, 'script': 'Generated script content'
        }
        
        mock_services['voice'].synthesize_speech.return_value = {
            'success': True, 'audio_path': '/tmp/test_audio.mp3', 'duration': 30.0
        }
        
        mock_services['subtitle'].generate_subtitles.return_value = {
            'success': True, 'output_path': '/tmp/test_subtitles.srt'
        }
        
        mock_services['music'].select_background_music.return_value = {
            'success': True, 'music_path': '/tmp/test_music.mp3'
        }
        
        # Mock video composition
        with patch.object(video_generator, '_create_video_composition') as mock_composition:
            mock_composition.return_value = {
                'success': True,
                'video_path': '/tmp/test_video.mp4',
                'video_clip': Mock(),
                'duration': 30.0,
                'size': 1024000
            }
            
            # Mock effects service
            mock_services['effects'].apply_video_effects.return_value = {
                'success': True, 'processed_video_clip': Mock()
            }
            
            # Mock video utils
            mock_services['utils'].optimize_video.return_value = {
                'success': True, 'output_path': '/tmp/optimized_video.mp4', 'output_size': 1024000
            }
            mock_services['utils'].generate_thumbnail.return_value = {
                'success': True, 'output_path': '/tmp/thumbnail.jpg'
            }
            
            # Mock storage
            mock_services['storage'].upload_file.return_value = {
                'success': True, 'url': 'https://storage.example.com/video.mp4'
            }
            
            # Execute video generation
            result = await video_generator.generate_video(sample_video_request)
            
            # Verify success
            assert result['success'] is True
            assert 'response' in result
            assert result['response'].status == 'completed'
            
            # Verify all services were called
            mock_services['db'].save_video_request.assert_called_once()
            mock_services['ai'].generate_script.assert_called_once()
            mock_services['voice'].synthesize_speech.assert_called_once()
            mock_services['subtitle'].generate_subtitles.assert_called_once()
            mock_services['music'].select_background_music.assert_called_once()
            mock_services['effects'].apply_video_effects.assert_called_once()
            mock_services['utils'].optimize_video.assert_called_once()
            mock_services['storage'].upload_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_video_ai_failure(self, video_generator, sample_video_request, mock_services):
        """Test video generation with AI service failure"""
        # Mock database save success
        mock_services['db'].save_video_request.return_value = {
            'success': True, 'request_id': 1
        }
        mock_services['db'].update_video_status.return_value = {'success': True}
        
        # Mock AI service failure
        mock_services['ai'].generate_script.return_value = {
            'success': False, 'error': 'AI service unavailable'
        }
        
        # Execute video generation
        result = await video_generator.generate_video(sample_video_request)
        
        # Verify failure
        assert result['success'] is False
        assert 'AI service unavailable' in result['error']
        
        # Verify database was updated with failure status
        mock_services['db'].update_video_status.assert_called_with(
            1, 'failed', metadata={'error': 'AI service unavailable', 'error_type': 'Exception'}
        )
    
    @pytest.mark.asyncio
    async def test_generate_video_voice_failure(self, video_generator, sample_video_request, mock_services):
        """Test video generation with voice service failure"""
        # Mock successful AI service
        mock_services['db'].save_video_request.return_value = {
            'success': True, 'request_id': 1
        }
        mock_services['db'].update_video_status.return_value = {'success': True}
        
        mock_services['ai'].generate_script.return_value = {
            'success': True, 'script': 'Generated script content'
        }
        
        # Mock voice service failure
        mock_services['voice'].synthesize_speech.return_value = {
            'success': False, 'error': 'Voice synthesis failed'
        }
        
        # Execute video generation
        result = await video_generator.generate_video(sample_video_request)
        
        # Verify failure
        assert result['success'] is False
        assert 'Voice synthesis failed' in result['error']
    
    @pytest.mark.asyncio
    async def test_batch_video_generation(self, video_generator, mock_services):
        """Test batch video generation"""
        from app.models.video import VideoBatchRequest
        
        # Create batch request
        batch_request = VideoBatchRequest(
            requests=[
                VideoRequest(
                    title="Video 1",
                    description="First video",
                    duration=30,
                    style=VideoStyle.PROFESSIONAL,
                    quality=VideoQuality.HIGH,
                    voice_preset=VoicePreset.PROFESSIONAL
                ),
                VideoRequest(
                    title="Video 2",
                    description="Second video",
                    duration=45,
                    style=VideoStyle.CREATIVE,
                    quality=VideoQuality.MEDIUM,
                    voice_preset=VoicePreset.FRIENDLY
                )
            ]
        )
        
        # Mock successful generation for both videos
        with patch.object(video_generator, 'generate_video') as mock_generate:
            mock_generate.side_effect = [
                {'success': True, 'response': Mock()},
                {'success': True, 'response': Mock()}
            ]
            
            result = await video_generator.generate_batch_videos(batch_request)
            
            # Verify success
            assert result['success'] is True
            assert result['total_requested'] == 2
            assert result['successful'] == 2
            assert result['failed'] == 0
            
            # Verify generate_video was called for each request
            assert mock_generate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_generation_status(self, video_generator, mock_services):
        """Test getting video generation status"""
        mock_services['db'].get_video_request.return_value = {
            'success': True,
            'data': {'id': 1, 'status': 'completed', 'title': 'Test Video'}
        }
        
        result = await video_generator.get_generation_status(1)
        
        assert result['success'] is True
        assert result['data']['status'] == 'completed'
        mock_services['db'].get_video_request.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_cancel_generation(self, video_generator, mock_services):
        """Test canceling video generation"""
        mock_services['db'].update_video_status.return_value = {'success': True}
        
        result = await video_generator.cancel_generation(1)
        
        assert result['success'] is True
        mock_services['db'].update_video_status.assert_called_once_with(1, 'cancelled')
    
    def test_get_service_status(self, video_generator, mock_services):
        """Test getting service status"""
        mock_services['storage'].get_storage_status.return_value = {'status': 'healthy'}
        mock_services['db'].get_database_status.return_value = {'status': 'healthy'}
        mock_services['monitoring'].get_metrics_summary.return_value = {'total_requests': 100}
        
        status = video_generator.get_service_status()
        
        assert 'ai_service' in status
        assert 'voice_service' in status
        assert 'subtitle_service' in status
        assert 'music_service' in status
        assert 'effects_service' in status
        assert 'storage_manager' in status
        assert 'database_service' in status
        assert 'monitoring_service' in status
    
    @pytest.mark.asyncio
    async def test_cleanup_temp_files(self, video_generator):
        """Test temporary file cleanup"""
        with patch('pathlib.Path.glob') as mock_glob, \
             patch('pathlib.Path.unlink') as mock_unlink:
            
            # Mock file paths
            mock_file = Mock()
            mock_file.name = 'test_gen_123_temp.mp4'
            mock_glob.return_value = [mock_file]
            
            await video_generator._cleanup_temp_files('gen_123')
            
            # Verify cleanup was attempted
            mock_unlink.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_service(self, video_generator, mock_services):
        """Test service cleanup"""
        await video_generator.close()
        
        # Verify all services were closed
        mock_services['db'].close.assert_called_once()
        mock_services['monitoring'].close.assert_called_once()


class TestVideoComposition:
    """Test video composition methods"""
    
    @pytest.mark.asyncio
    async def test_create_video_composition(self, video_generator, sample_video_request):
        """Test video composition creation"""
        with patch('app.services.video_generator.AudioFileClip') as mock_audio, \
             patch('app.services.video_generator.CompositeVideoClip') as mock_composite, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            
            # Mock audio clip
            mock_audio_clip = Mock()
            mock_audio_clip.duration = 30.0
            mock_audio.return_value = mock_audio_clip
            
            # Mock composite video
            mock_composite_video = Mock()
            mock_composite.return_value = mock_composite_video
            
            # Mock file operations
            with patch('builtins.open', create=True), \
                 patch('os.path.getsize', return_value=1024000):
                
                result = await video_generator._create_video_composition(
                    'Test script',
                    '/tmp/audio.mp3',
                    '/tmp/subtitles.srt',
                    '/tmp/music.mp3',
                    sample_video_request,
                    'test_gen_123'
                )
                
                assert result['success'] is True
                assert 'video_path' in result
                assert result['duration'] == 30.0
                assert result['size'] == 1024000
    
    def test_create_background(self, video_generator):
        """Test background creation"""
        with patch('app.services.video_generator.cv2.imwrite') as mock_imwrite, \
             patch('app.services.video_generator.ImageClip') as mock_image_clip:
            
            mock_image = Mock()
            mock_image_clip.return_value = mock_image
            
            result = video_generator._create_background((1920, 1080), VideoStyle.PROFESSIONAL)
            
            assert result is not None
            mock_imwrite.assert_called_once()
            mock_image_clip.assert_called_once()
    
    def test_create_text_clips(self, video_generator):
        """Test text clip creation"""
        with patch('app.services.video_generator.TextClip') as mock_text_clip:
            mock_clip = Mock()
            mock_text_clip.return_value = mock_clip
            
            result = video_generator._create_text_clips(
                'This is a test sentence. This is another sentence.',
                30.0,
                (1920, 1080),
                VideoStyle.PROFESSIONAL
            )
            
            assert len(result) > 0
            mock_text_clip.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
