"""
Tests for FastAPI endpoints
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.models.video import VideoRequest, VideoStyle, VideoQuality, VoicePreset, TransitionType


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def sample_video_request():
    """Sample video request for testing"""
    return {
        "title": "Test Video",
        "description": "This is a test video description for testing purposes.",
        "duration": 30,
        "style": "professional",
        "quality": "high",
        "voice_preset": "professional",
        "background_music": True,
        "music_intensity": "medium",
        "aspect_ratio": "16:9",
        "transitions": "fade",
        "ai_model": "gpt-4",
        "language": "en",
        "include_subtitles": True
    }


@pytest.fixture
def sample_batch_request():
    """Sample batch request for testing"""
    return {
        "requests": [
            {
                "title": "Video 1",
                "description": "First video",
                "duration": 30,
                "style": "professional",
                "quality": "high",
                "voice_preset": "professional"
            },
            {
                "title": "Video 2",
                "description": "Second video",
                "duration": 45,
                "style": "creative",
                "quality": "medium",
                "voice_preset": "friendly"
            }
        ]
    }


@pytest.fixture
def mock_services():
    """Mock all services"""
    with patch('app.main.VideoGeneratorService') as mock_vg, \
         patch('app.main.DatabaseService') as mock_db, \
         patch('app.main.MonitoringService') as mock_mon, \
         patch('app.main.StorageManager') as mock_storage:
        
        # Configure mock services
        mock_vg.return_value = Mock()
        mock_db.return_value = Mock()
        mock_mon.return_value = Mock()
        mock_storage.return_value = Mock()
        
        yield {
            'video_generator': mock_vg.return_value,
            'database_service': mock_db.return_value,
            'monitoring_service': mock_mon.return_value,
            'storage_manager': mock_storage.return_value
        }


class TestHealthEndpoints:
    """Test health and monitoring endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Welcome to MoneyPrinterTurboPro API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "running"
    
    def test_health_check(self, client, mock_services):
        """Test health check endpoint"""
        mock_services['monitoring_service'].check_health.return_value = {
            'status': 'healthy',
            'last_check': '2024-01-01T00:00:00',
            'response_time': 0.1
        }
        
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_metrics_endpoint(self, client, mock_services):
        """Test metrics endpoint"""
        mock_services['monitoring_service'].export_metrics.return_value = {
            'success': True,
            'format': 'prometheus',
            'data': b'# HELP test_metric Test metric\n# TYPE test_metric counter\ntest_metric 1.0\n',
            'content_type': 'text/plain; version=0.0.4; charset=utf-8'
        }
        
        response = client.get("/metrics")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == 'text/plain; version=0.0.4; charset=utf-8'


class TestVideoGenerationEndpoints:
    """Test video generation endpoints"""
    
    def test_generate_video_success(self, client, sample_video_request, mock_services):
        """Test successful video generation"""
        # Mock successful video generation
        mock_response = Mock()
        mock_response.status = "completed"
        mock_response.video_path = "/tmp/test_video.mp4"
        mock_response.duration = 30
        mock_response.size = 1024000
        
        mock_services['video_generator'].generate_video.return_value = {
            'success': True,
            'response': mock_response,
            'generation_id': 'test_gen_123',
            'generation_time': 15.5
        }
        
        response = client.post("/videos/generate", json=sample_video_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert data["video_path"] == "/tmp/test_video.mp4"
        
        # Verify service was called
        mock_services['video_generator'].generate_video.assert_called_once()
    
    def test_generate_video_failure(self, client, sample_video_request, mock_services):
        """Test video generation failure"""
        # Mock failed video generation
        mock_services['video_generator'].generate_video.return_value = {
            'success': False,
            'error': 'AI service unavailable',
            'error_type': 'ServiceUnavailableError',
            'generation_id': 'test_gen_123',
            'generation_time': 2.1
        }
        
        response = client.post("/videos/generate", json=sample_video_request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "AI service unavailable" in data["detail"]
    
    def test_generate_batch_videos_success(self, client, sample_batch_request, mock_services):
        """Test successful batch video generation"""
        # Mock successful batch generation
        mock_services['video_generator'].generate_batch_videos.return_value = {
            'success': True,
            'total_requested': 2,
            'successful': 2,
            'failed': 0,
            'results': {
                'successful': [{'id': 1}, {'id': 2}],
                'failed': []
            }
        }
        
        response = client.post("/videos/generate/batch", json=sample_batch_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 2
        assert data["successful"] == 2
        assert data["failed"] == 0
    
    def test_generate_batch_videos_failure(self, client, sample_batch_request, mock_services):
        """Test batch video generation failure"""
        # Mock failed batch generation
        mock_services['video_generator'].generate_batch_videos.return_value = {
            'success': False,
            'error': 'Batch processing failed',
            'error_type': 'BatchError'
        }
        
        response = client.post("/videos/generate/batch", json=sample_batch_request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Batch processing failed" in data["detail"]
    
    def test_get_video_status_success(self, client, mock_services):
        """Test getting video status successfully"""
        # Mock successful status retrieval
        mock_services['video_generator'].get_generation_status.return_value = {
            'success': True,
            'data': {
                'id': 1,
                'status': 'processing',
                'title': 'Test Video',
                'created_at': '2024-01-01T00:00:00'
            }
        }
        
        response = client.get("/videos/1/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "processing"
    
    def test_get_video_status_not_found(self, client, mock_services):
        """Test getting video status for non-existent video"""
        # Mock video not found
        mock_services['video_generator'].get_generation_status.return_value = {
            'success': False,
            'error': 'Video request not found'
        }
        
        response = client.get("/videos/999/status")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Video request not found" in data["detail"]
    
    def test_cancel_video_generation_success(self, client, mock_services):
        """Test successful video generation cancellation"""
        # Mock successful cancellation
        mock_services['video_generator'].cancel_generation.return_value = {
            'success': True,
            'message': 'Video generation cancelled successfully'
        }
        
        response = client.post("/videos/1/cancel")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "cancelled successfully" in data["message"]
    
    def test_cancel_video_generation_failure(self, client, mock_services):
        """Test video generation cancellation failure"""
        # Mock failed cancellation
        mock_services['video_generator'].cancel_generation.return_value = {
            'success': False,
            'error': 'Failed to cancel generation'
        }
        
        response = client.post("/videos/1/cancel")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Failed to cancel generation" in data["detail"]


class TestVideoManagementEndpoints:
    """Test video management endpoints"""
    
    def test_list_videos_success(self, client, mock_services):
        """Test successful video listing"""
        # Mock successful video listing
        mock_services['database_service'].list_video_requests.return_value = {
            'success': True,
            'data': [
                {
                    'id': 1,
                    'title': 'Video 1',
                    'status': 'completed',
                    'created_at': '2024-01-01T00:00:00'
                },
                {
                    'id': 2,
                    'title': 'Video 2',
                    'status': 'processing',
                    'created_at': '2024-01-01T01:00:00'
                }
            ],
            'count': 2,
            'source': 'database'
        }
        
        response = client.get("/videos")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["count"] == 2
    
    def test_list_videos_with_filters(self, client, mock_services):
        """Test video listing with filters"""
        # Mock successful filtered video listing
        mock_services['database_service'].list_video_requests.return_value = {
            'success': True,
            'data': [
                {
                    'id': 1,
                    'title': 'Video 1',
                    'status': 'completed',
                    'user_id': 'user123'
                }
            ],
            'count': 1,
            'source': 'database'
        }
        
        response = client.get("/videos?user_id=user123&status=completed&limit=10&offset=0")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["user_id"] == "user123"
    
    def test_get_video_success(self, client, mock_services):
        """Test successful video retrieval"""
        # Mock successful video retrieval
        mock_services['database_service'].get_video_request.return_value = {
            'success': True,
            'data': {
                'id': 1,
                'title': 'Test Video',
                'status': 'completed',
                'video_path': '/tmp/test_video.mp4',
                'created_at': '2024-01-01T00:00:00'
            }
        }
        
        response = client.get("/videos/1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Video"
        assert data["status"] == "completed"
    
    def test_get_video_not_found(self, client, mock_services):
        """Test video retrieval for non-existent video"""
        # Mock video not found
        mock_services['database_service'].get_video_request.return_value = {
            'success': False,
            'error': 'Video request not found'
        }
        
        response = client.get("/videos/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Video request not found" in data["detail"]


class TestTemplateEndpoints:
    """Test template management endpoints"""
    
    def test_create_template_success(self, client, mock_services):
        """Test successful template creation"""
        template_data = {
            "name": "Test Template",
            "description": "A test template",
            "style": "professional",
            "quality": "high",
            "voice_preset": "professional",
            "language": "en"
        }
        
        # Mock successful template creation
        mock_services['database_service'].save_video_template.return_value = {
            'success': True,
            'template_id': 1,
            'message': 'Video template saved successfully'
        }
        
        response = client.post("/templates", json=template_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["template_id"] == 1
        assert "saved successfully" in data["message"]
    
    def test_create_template_failure(self, client, mock_services):
        """Test template creation failure"""
        template_data = {
            "name": "Test Template",
            "style": "professional",
            "quality": "high",
            "voice_preset": "professional"
        }
        
        # Mock failed template creation
        mock_services['database_service'].save_video_template.return_value = {
            'success': False,
            'error': 'Failed to save template'
        }
        
        response = client.post("/templates", json=template_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Failed to save template" in data["detail"]


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_save_analytics_success(self, client, mock_services):
        """Test successful analytics saving"""
        analytics_data = {
            "video_id": 1,
            "user_id": "user123",
            "views": 100,
            "likes": 25,
            "shares": 10,
            "comments": 5,
            "watch_time": 1800,
            "completion_rate": 85.5,
            "engagement_score": 78.2
        }
        
        # Mock successful analytics saving
        mock_services['database_service'].save_video_analytics.return_value = {
            'success': True,
            'analytics_id': 1,
            'message': 'Video analytics saved successfully'
        }
        
        response = client.post("/analytics", json=analytics_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["analytics_id"] == 1
        assert "saved successfully" in data["message"]
    
    def test_save_analytics_failure(self, client, mock_services):
        """Test analytics saving failure"""
        analytics_data = {
            "video_id": 1,
            "user_id": "user123",
            "views": 100
        }
        
        # Mock failed analytics saving
        mock_services['database_service'].save_video_analytics.return_value = {
            'success': False,
            'error': 'Failed to save analytics'
        }
        
        response = client.post("/analytics", json=analytics_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Failed to save analytics" in data["detail"]


class TestSystemEndpoints:
    """Test system status endpoints"""
    
    def test_get_system_status(self, client, mock_services):
        """Test getting system status"""
        # Mock system status
        mock_services['video_generator'].get_service_status.return_value = {
            'ai_service': 'available',
            'voice_service': 'available',
            'subtitle_service': 'available',
            'music_service': 'available',
            'effects_service': 'available',
            'storage_manager': {'status': 'healthy'},
            'database_service': {'status': 'healthy'},
            'monitoring_service': {'total_requests': 100}
        }
        
        response = client.get("/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ai_service"] == "available"
        assert data["voice_service"] == "available"
        assert data["storage_manager"]["status"] == "healthy"
    
    def test_get_storage_status(self, client, mock_services):
        """Test getting storage status"""
        # Mock storage status
        mock_services['storage_manager'].get_storage_status.return_value = {
            'local_storage': {
                'enabled': True,
                'size_gb': 5.2,
                'max_size_gb': 10.0
            },
            'providers': {
                'local': True,
                's3': True,
                'azure': False
            }
        }
        
        response = client.get("/storage/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["local_storage"]["enabled"] is True
        assert data["providers"]["local"] is True
        assert data["providers"]["s3"] is True


class TestErrorHandling:
    """Test error handling"""
    
    def test_global_exception_handler(self, client, mock_services):
        """Test global exception handler"""
        # Mock service to raise exception
        mock_services['video_generator'].generate_video.side_effect = Exception("Unexpected error")
        
        response = client.post("/videos/generate", json={"invalid": "data"})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"] == "Internal server error"
        assert data["error_type"] == "Exception"
    
    def test_http_exception_handler(self, client, mock_services):
        """Test HTTP exception handler"""
        # Mock service to return failure
        mock_services['video_generator'].generate_video.return_value = {
            'success': False,
            'error': 'Service unavailable'
        }
        
        response = client.post("/videos/generate", json={"invalid": "data"})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Service unavailable" in data["detail"]


class TestMiddleware:
    """Test middleware functionality"""
    
    def test_request_logging_middleware(self, client, mock_services):
        """Test request logging middleware"""
        # Mock successful response
        mock_services['video_generator'].generate_video.return_value = {
            'success': True,
            'response': Mock(status="completed")
        }
        
        response = client.post("/videos/generate", json={"test": "data"})
        
        # Verify processing time header is present
        assert "X-Process-Time" in response.headers
        assert float(response.headers["X-Process-Time"]) >= 0
    
    def test_cors_middleware(self, client):
        """Test CORS middleware"""
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # CORS preflight should succeed
        assert response.status_code in [200, 204]


if __name__ == "__main__":
    pytest.main([__file__])
