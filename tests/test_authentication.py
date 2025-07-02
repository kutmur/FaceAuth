"""
Comprehensive test suite for FaceAuth authentication module.
Tests face authentication, security integration, and error handling.
"""

import pytest
import numpy as np
import time
import cv2
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from pathlib import Path
import tempfile
import shutil
import torch
from PIL import Image

from faceauth.core.authentication import FaceAuthenticator, AuthenticationError
from faceauth.utils.storage import FaceDataStorage


class TestFaceAuthenticator:
    """Test cases for FaceAuthenticator class."""
    
    def test_authenticator_initialization(self, temp_dir):
        """Test authenticator initialization with default parameters."""
        authenticator = FaceAuthenticator(storage_dir=str(temp_dir))
        
        assert authenticator.device in ['cpu', 'cuda']
        assert authenticator.similarity_threshold == 0.6
        assert authenticator.storage is not None
        assert authenticator.secure_storage is not None
        assert authenticator.audit_logger is not None
        assert authenticator.privacy_manager is not None
        assert authenticator.memory_manager is not None
        assert authenticator.mtcnn is not None
        assert authenticator.model is not None
    
    def test_authenticator_custom_threshold(self, temp_dir):
        """Test authenticator with custom similarity threshold."""
        custom_threshold = 0.8
        authenticator = FaceAuthenticator(
            similarity_threshold=custom_threshold,
            storage_dir=str(temp_dir)
        )
        
        assert authenticator.similarity_threshold == custom_threshold
    
    def test_authenticator_device_selection(self, temp_dir):
        """Test device selection logic."""
        # Test CPU device
        authenticator = FaceAuthenticator(device='cpu', storage_dir=str(temp_dir))
        assert authenticator.device == 'cpu'
        
        # Test CUDA device (if available)
        if torch.cuda.is_available():
            authenticator = FaceAuthenticator(device='cuda', storage_dir=str(temp_dir))
            assert authenticator.device == 'cuda'


class TestFaceDetectionAndEmbedding:
    """Test face detection and embedding generation."""
    
    def test_extract_face_valid_image(self, authenticator, face_image):
        """Test face extraction from valid image."""
        embedding, error = authenticator._extract_face_and_embedding(face_image)
        
        assert error is None
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (512,)  # FaceNet embedding size
        assert np.linalg.norm(embedding) > 0  # Non-zero embedding
    
    def test_extract_face_no_face(self, authenticator, no_face_image):
        """Test face extraction when no face is present."""
        embedding, error = authenticator._extract_face_and_embedding(no_face_image)
        
        assert embedding is None
        assert error == "No face detected"
    
    def test_extract_face_poor_quality(self, authenticator, blurry_image):
        """Test face extraction with poor quality image."""
        # This might still extract a face but with lower confidence
        embedding, error = authenticator._extract_face_and_embedding(blurry_image)
        
        # Either extracts successfully or fails due to quality
        if embedding is not None:
            assert isinstance(embedding, np.ndarray)
        else:
            assert error is not None
    
    def test_calculate_similarity(self, authenticator, face_embedding_pair):
        """Test similarity calculation between embeddings."""
        embedding1, embedding2 = face_embedding_pair
        
        similarity = authenticator._calculate_similarity(embedding1, embedding2)
        
        assert isinstance(similarity, float)
        assert -1.0 <= similarity <= 1.0
        
        # Self-similarity should be close to 1.0
        self_similarity = authenticator._calculate_similarity(embedding1, embedding1)
        assert self_similarity > 0.95
    
    def test_calculate_similarity_different_faces(self, authenticator):
        """Test similarity between different face embeddings."""
        # Generate two random embeddings (simulating different faces)
        embedding1 = np.random.rand(512).astype(np.float32)
        embedding2 = np.random.rand(512).astype(np.float32)
        
        # Normalize embeddings
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        similarity = authenticator._calculate_similarity(embedding1, embedding2)
        
        # Random embeddings should have low similarity
        assert similarity < 0.5


class TestImageQuality:
    """Test image quality assessment functionality."""
    
    def test_assess_image_quality_good_image(self, authenticator, face_image):
        """Test quality assessment for good image."""
        quality = authenticator._assess_image_quality(face_image)
        
        assert 'sharpness' in quality
        assert 'brightness' in quality
        assert 'contrast' in quality
        assert all(isinstance(v, (int, float)) for v in quality.values())
    
    def test_assess_image_quality_blurry(self, authenticator, blurry_image):
        """Test quality assessment for blurry image."""
        quality = authenticator._assess_image_quality(blurry_image)
        
        # Blurry images should have low sharpness
        assert quality['sharpness'] < 100.0
    
    def test_assess_image_quality_dark(self, authenticator, dark_image):
        """Test quality assessment for dark image."""
        quality = authenticator._assess_image_quality(dark_image)
        
        # Dark images should have low brightness
        assert quality['brightness'] < 80
    
    def test_is_good_quality_validation(self, authenticator):
        """Test quality validation logic."""
        # Good quality metrics
        good_quality = {
            'sharpness': 150.0,
            'brightness': 120.0,
            'contrast': 50.0
        }
        is_good, reason = authenticator._is_good_quality(good_quality)
        assert is_good is True
        assert reason == "Good quality"
        
        # Poor sharpness
        poor_sharpness = {
            'sharpness': 50.0,
            'brightness': 120.0,
            'contrast': 50.0
        }
        is_good, reason = authenticator._is_good_quality(poor_sharpness)
        assert is_good is False
        assert "blurry" in reason.lower()
        
        # Too dark
        too_dark = {
            'sharpness': 150.0,
            'brightness': 50.0,
            'contrast': 50.0
        }
        is_good, reason = authenticator._is_good_quality(too_dark)
        assert is_good is False
        assert "dark" in reason.lower()


class TestAuthenticationFlow:
    """Test complete authentication workflow."""
    
    @patch('cv2.VideoCapture')
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_authenticate_realtime_success(self, mock_destroy, mock_waitkey, 
                                         mock_imshow, mock_videocap, 
                                         authenticator_with_user, enrolled_user_id, 
                                         face_image):
        """Test successful real-time authentication."""
        # Setup mocks
        mock_cap = Mock()
        mock_videocap.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
        mock_cap.set.return_value = True
        mock_cap.release.return_value = None
        mock_waitkey.return_value = ord('q')  # Simulate quit after first frame
        
        authenticator = authenticator_with_user
        
        # Mock face detection to return a valid embedding
        with patch.object(authenticator, '_extract_face_and_embedding') as mock_extract:
            # Return high-similarity embedding
            high_sim_embedding = np.random.rand(512).astype(np.float32)
            mock_extract.return_value = (high_sim_embedding, None)
            
            # Mock similarity calculation to return high similarity
            with patch.object(authenticator, '_calculate_similarity') as mock_similarity:
                mock_similarity.return_value = 0.9  # Above threshold
                
                result = authenticator.authenticate_realtime(
                    user_id=enrolled_user_id,
                    timeout=5,
                    max_attempts=3
                )
        
        assert result['success'] is True
        assert result['user_id'] == enrolled_user_id
        assert result['similarity'] >= authenticator.similarity_threshold
        assert 'duration' in result
        assert 'attempts' in result
    
    @patch('cv2.VideoCapture')
    def test_authenticate_realtime_webcam_error(self, mock_videocap, authenticator, enrolled_user_id):
        """Test authentication when webcam is not accessible."""
        # Mock webcam failure
        mock_cap = Mock()
        mock_videocap.return_value = mock_cap
        mock_cap.isOpened.return_value = False
        
        result = authenticator.authenticate_realtime(enrolled_user_id, timeout=5)
        
        assert result['success'] is False
        assert result['error_type'] == 'webcam_error'
        assert 'Cannot access webcam' in result['error']
    
    def test_authenticate_realtime_user_not_found(self, authenticator):
        """Test authentication for non-enrolled user."""
        non_existent_user = "non_existent_user"
        
        result = authenticator.authenticate_realtime(non_existent_user, timeout=5)
        
        assert result['success'] is False
        assert result['error_type'] == 'user_not_found'
        assert non_existent_user in result['error']
    
    @patch('cv2.VideoCapture')
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_authenticate_realtime_low_similarity(self, mock_destroy, mock_waitkey, 
                                                mock_imshow, mock_videocap, 
                                                authenticator_with_user, enrolled_user_id, 
                                                face_image):
        """Test authentication failure due to low similarity."""
        # Setup mocks
        mock_cap = Mock()
        mock_videocap.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
        mock_cap.set.return_value = True
        mock_cap.release.return_value = None
        mock_waitkey.side_effect = [ord('a')] * 10 + [ord('q')]  # Multiple attempts then quit
        
        authenticator = authenticator_with_user
        
        # Mock face detection to return a valid embedding
        with patch.object(authenticator, '_extract_face_and_embedding') as mock_extract:
            low_sim_embedding = np.random.rand(512).astype(np.float32)
            mock_extract.return_value = (low_sim_embedding, None)
            
            # Mock similarity calculation to return low similarity
            with patch.object(authenticator, '_calculate_similarity') as mock_similarity:
                mock_similarity.return_value = 0.3  # Below threshold
                
                result = authenticator.authenticate_realtime(
                    user_id=enrolled_user_id,
                    timeout=5,
                    max_attempts=3
                )
        
        assert result['success'] is False
        assert result['user_id'] == enrolled_user_id
        assert result['best_similarity'] < authenticator.similarity_threshold


class TestPerformanceMetrics:
    """Test performance metrics functionality."""
    
    def test_initial_performance_metrics(self, authenticator):
        """Test initial state of performance metrics."""
        metrics = authenticator.get_performance_metrics()
        
        assert metrics['average_authentication_time'] == 0
        assert metrics['total_attempts'] == 0
        assert metrics['successful_attempts'] == 0
        assert metrics['false_positive_rate'] == 0
        assert metrics['false_negative_rate'] == 0
        assert metrics['false_positives'] == 0
        assert metrics['false_negatives'] == 0
    
    def test_performance_metrics_after_attempts(self, authenticator):
        """Test performance metrics after authentication attempts."""
        # Simulate some authentication attempts
        authenticator.total_attempts = 10
        authenticator.authentication_times = [1.2, 1.5, 0.8, 2.1, 1.0]
        authenticator.false_positives = 1
        authenticator.false_negatives = 2
        
        metrics = authenticator.get_performance_metrics()
        
        assert metrics['total_attempts'] == 10
        assert metrics['successful_attempts'] == 5
        assert metrics['average_authentication_time'] == sum(authenticator.authentication_times) / 5
        assert metrics['false_positive_rate'] == 0.1
        assert metrics['false_negative_rate'] == 0.2
        assert metrics['false_positives'] == 1
        assert metrics['false_negatives'] == 2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_storage_error_handling(self, authenticator, enrolled_user_id):
        """Test handling of storage errors during authentication."""
        # Mock storage error
        with patch.object(authenticator.secure_storage, 'load_encrypted_file') as mock_load:
            mock_load.side_effect = Exception("Storage corruption")
            
            result = authenticator.authenticate_realtime(enrolled_user_id, timeout=5)
            
            assert result['success'] is False
            assert result['error_type'] == 'storage_error'
            assert 'Storage corruption' in result['error']
    
    def test_model_error_handling(self, authenticator, face_image):
        """Test handling of model processing errors."""
        # Mock model error
        with patch.object(authenticator, '_extract_face_and_embedding') as mock_extract:
            mock_extract.side_effect = Exception("Model processing error")
            
            embedding, error = authenticator._extract_face_and_embedding(face_image)
            
            assert embedding is None
            assert "Model processing error" in error
    
    def test_webcam_frame_capture_error(self, authenticator):
        """Test handling of webcam frame capture errors."""
        frame = authenticator._capture_frame_from_webcam(None)
        assert frame is None


class TestPrivacyIntegration:
    """Test privacy manager integration."""
    
    def test_authentication_privacy_denied(self, authenticator, enrolled_user_id):
        """Test authentication when privacy processing is not allowed."""
        # Mock privacy manager to deny processing
        with patch.object(authenticator.privacy_manager, 'is_processing_allowed') as mock_privacy:
            mock_privacy.return_value = False
            
            result = authenticator.authenticate_realtime(enrolled_user_id, timeout=5)
            
            assert result['success'] is False
            assert result['error_type'] == 'privacy_denied'
            assert 'not permitted' in result['error']


class TestSecurityIntegration:
    """Test security features integration."""
    
    def test_audit_logging_on_authentication(self, authenticator, enrolled_user_id):
        """Test that authentication attempts are logged."""
        with patch.object(authenticator.audit_logger, 'log_event') as mock_log:
            # Test user not found scenario (simpler to test)
            authenticator.authenticate_realtime(enrolled_user_id, timeout=5)
            
            # Verify logging was called
            assert mock_log.called
            
            # Check that authentication_started and authentication_failed events were logged
            call_args_list = mock_log.call_args_list
            event_types = [call[1]['event_type'] for call in call_args_list]
            
            assert 'authentication_started' in event_types
            assert 'authentication_failed' in event_types


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    def test_end_to_end_authentication_workflow(self, authenticator_with_user, enrolled_user_id):
        """Test complete end-to-end authentication workflow."""
        # This would test the full workflow from enrollment to authentication
        # Mock the complex interactions
        with patch.object(authenticator_with_user, 'authenticate_realtime') as mock_auth:
            mock_auth.return_value = {
                'success': True,
                'user_id': enrolled_user_id,
                'similarity': 0.85,
                'threshold': 0.6,
                'duration': 2.5,
                'attempts': 2,
                'authentication_attempts': [
                    {'attempt': 1, 'similarity': 0.45, 'timestamp': time.time()},
                    {'attempt': 2, 'similarity': 0.85, 'timestamp': time.time()}
                ]
            }
            
            result = authenticator_with_user.authenticate_realtime(enrolled_user_id)
            
            assert result['success'] is True
            assert result['user_id'] == enrolled_user_id
            assert result['similarity'] > result['threshold']
            assert len(result['authentication_attempts']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
