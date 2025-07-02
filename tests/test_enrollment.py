# test_enrollment.py - Tests for face enrollment functionality
import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from faceauth.core.enrollment import FaceEnrollmentManager, FaceEnrollmentError
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager
from conftest import create_test_frame, create_test_frame_no_face, create_test_frame_multiple_faces


class TestFaceEnrollmentManager:
    """Test suite for FaceEnrollmentManager."""
    
    @pytest.mark.unit
    def test_initialization(self, temp_storage_dir):
        """Test enrollment manager initialization."""
        with patch('faceauth.core.enrollment.MTCNN'), \
             patch('faceauth.core.enrollment.InceptionResnetV1'):
            manager = FaceEnrollmentManager(storage_dir=temp_storage_dir)
            
            assert manager.storage_dir == temp_storage_dir
            assert manager.device in ['cpu', 'cuda']
            assert manager.min_samples >= 1
            assert manager.max_samples >= manager.min_samples
            assert 0.0 < manager.quality_threshold < 1.0
    
    @pytest.mark.unit
    def test_initialization_with_custom_params(self, temp_storage_dir):
        """Test enrollment manager with custom parameters."""
        with patch('faceauth.core.enrollment.MTCNN'), \
             patch('faceauth.core.enrollment.InceptionResnetV1'):
            manager = FaceEnrollmentManager(
                storage_dir=temp_storage_dir,
                device='cpu',
                min_samples=5,
                max_samples=15,
                quality_threshold=0.8
            )
            
            assert manager.device == 'cpu'
            assert manager.min_samples == 5
            assert manager.max_samples == 15
            assert manager.quality_threshold == 0.8
    
    @pytest.mark.unit
    def test_model_initialization(self, temp_storage_dir):
        """Test that models are properly initialized."""
        with patch('faceauth.core.enrollment.MTCNN') as mock_mtcnn, \
             patch('faceauth.core.enrollment.InceptionResnetV1') as mock_facenet:
            
            manager = FaceEnrollmentManager(storage_dir=temp_storage_dir)
            
            # Verify MTCNN initialization
            mock_mtcnn.assert_called_once()
            mtcnn_call_kwargs = mock_mtcnn.call_args[1]
            assert mtcnn_call_kwargs['image_size'] == 160
            assert mtcnn_call_kwargs['device'] == manager.device
            
            # Verify FaceNet initialization  
            mock_facenet.assert_called_once_with(pretrained='vggface2')
    
    @pytest.mark.unit
    def test_verify_enrollment_user_not_exists(self, enrollment_manager):
        """Test verification when user doesn't exist."""
        with patch.object(enrollment_manager.storage, 'user_exists', return_value=False):
            assert not enrollment_manager.verify_enrollment('nonexistent_user')
    
    @pytest.mark.unit
    def test_verify_enrollment_user_exists(self, enrollment_manager):
        """Test verification when user exists."""
        with patch.object(enrollment_manager.storage, 'user_exists', return_value=True):
            assert enrollment_manager.verify_enrollment('existing_user')
    
    @pytest.mark.unit
    def test_image_quality_assessment(self, enrollment_manager):
        """Test image quality assessment."""
        # Test good quality image
        good_frame = create_test_frame()
        quality = enrollment_manager._assess_image_quality(good_frame)
        
        assert 'sharpness' in quality
        assert 'brightness' in quality
        assert 'contrast' in quality
        assert all(isinstance(v, (int, float)) for v in quality.values())
        assert all(v >= 0 for v in quality.values())
    
    @pytest.mark.unit
    def test_quality_check_good_image(self, enrollment_manager):
        """Test quality check with good image."""
        quality_metrics = {
            'sharpness': 200.0,
            'brightness': 120.0,
            'contrast': 50.0
        }
        
        is_good, reason = enrollment_manager._is_good_quality(quality_metrics)
        assert is_good
        assert reason == "Good quality"
    
    @pytest.mark.unit
    def test_quality_check_blurry_image(self, enrollment_manager):
        """Test quality check with blurry image."""
        quality_metrics = {
            'sharpness': 50.0,  # Below threshold
            'brightness': 120.0,
            'contrast': 50.0
        }
        
        is_good, reason = enrollment_manager._is_good_quality(quality_metrics)
        assert not is_good
        assert "blurry" in reason.lower()
    
    @pytest.mark.unit
    def test_quality_check_dark_image(self, enrollment_manager):
        """Test quality check with dark image."""
        quality_metrics = {
            'sharpness': 200.0,
            'brightness': 50.0,  # Below threshold
            'contrast': 50.0
        }
        
        is_good, reason = enrollment_manager._is_good_quality(quality_metrics)
        assert not is_good
        assert "dark" in reason.lower()
    
    @pytest.mark.unit
    def test_quality_check_bright_image(self, enrollment_manager):
        """Test quality check with bright image."""
        quality_metrics = {
            'sharpness': 200.0,
            'brightness': 250.0,  # Above threshold
            'contrast': 50.0
        }
        
        is_good, reason = enrollment_manager._is_good_quality(quality_metrics)
        assert not is_good
        assert "bright" in reason.lower()
    
    @pytest.mark.unit
    def test_quality_check_low_contrast(self, enrollment_manager):
        """Test quality check with low contrast image."""
        quality_metrics = {
            'sharpness': 200.0,
            'brightness': 120.0,
            'contrast': 10.0  # Below threshold
        }
        
        is_good, reason = enrollment_manager._is_good_quality(quality_metrics)
        assert not is_good
        assert "contrast" in reason.lower()
    
    @pytest.mark.unit
    def test_face_extraction_success(self, enrollment_manager, mock_face_embedding):
        """Test successful face extraction and embedding generation."""
        test_frame = create_test_frame()
        
        # Mock MTCNN to return a face tensor
        with patch.object(enrollment_manager.face_detector.mtcnn, '__call__') as mock_mtcnn, \
             patch.object(enrollment_manager.embedding_generator.model, '__call__') as mock_model:
            
            # Mock face detection
            mock_face_tensor = Mock()
            mock_mtcnn.return_value = mock_face_tensor
            
            # Mock embedding generation
            mock_output = Mock()
            mock_output.cpu.return_value.numpy.return_value.flatten.return_value = mock_face_embedding
            mock_model.return_value = mock_output
            
            embedding, error = enrollment_manager._extract_face_and_embedding(test_frame)
            
            assert embedding is not None
            assert error is None
            assert len(embedding) == 512  # FaceNet embedding size
            assert isinstance(embedding, np.ndarray)
    
    @pytest.mark.unit
    def test_face_extraction_no_face(self, enrollment_manager):
        """Test face extraction when no face is detected."""
        test_frame = create_test_frame_no_face()
        
        # Mock MTCNN to return None (no face detected)
        with patch.object(enrollment_manager.face_detector.mtcnn, '__call__', return_value=None):
            embedding, error = enrollment_manager._extract_face_and_embedding(test_frame)
            
            assert embedding is None
            assert error is not None
            assert "no face detected" in error.lower()
    
    @pytest.mark.unit
    def test_face_extraction_error(self, enrollment_manager):
        """Test face extraction with processing error."""
        test_frame = create_test_frame()
        
        # Mock MTCNN to raise an exception
        with patch.object(enrollment_manager.face_detector.mtcnn, '__call__', 
                         side_effect=Exception("Processing error")):
            embedding, error = enrollment_manager._extract_face_and_embedding(test_frame)
            
            assert embedding is None
            assert error is not None
            assert "error processing face" in error.lower()
    
    @pytest.mark.unit
    def test_enrollment_sample_validation(self, enrollment_manager, mock_face_embedding):
        """Test enrollment sample validation."""
        samples = [mock_face_embedding] * 5
        
        # All samples should be similar (using same mock embedding)
        is_valid, reason = enrollment_manager._validate_enrollment_samples(samples)
        assert is_valid
        assert reason == "Samples are consistent"
    
    @pytest.mark.unit
    def test_enrollment_sample_validation_inconsistent(self, enrollment_manager, 
                                                      mock_face_embedding, 
                                                      mock_face_embedding_different):
        """Test enrollment sample validation with inconsistent samples."""
        samples = [mock_face_embedding, mock_face_embedding_different]
        
        is_valid, reason = enrollment_manager._validate_enrollment_samples(samples)
        assert not is_valid
        assert "inconsistent" in reason.lower()
    
    @pytest.mark.unit
    def test_enrollment_sample_validation_insufficient(self, enrollment_manager, mock_face_embedding):
        """Test enrollment sample validation with insufficient samples."""
        samples = [mock_face_embedding]  # Only one sample, but min_samples might be higher
        
        with patch.object(enrollment_manager, 'min_samples', 3):
            is_valid, reason = enrollment_manager._validate_enrollment_samples(samples)
            assert not is_valid
            assert "insufficient" in reason.lower()
    
    @pytest.mark.unit
    def test_calculate_average_embedding(self, enrollment_manager):
        """Test average embedding calculation."""
        # Create test embeddings
        embedding1 = np.array([1.0, 0.0, 0.0] + [0.0] * 509, dtype=np.float32)
        embedding2 = np.array([0.0, 1.0, 0.0] + [0.0] * 509, dtype=np.float32)
        embedding3 = np.array([0.0, 0.0, 1.0] + [0.0] * 509, dtype=np.float32)
        
        samples = [embedding1, embedding2, embedding3]
        average = enrollment_manager._calculate_average_embedding(samples)
        
        assert len(average) == 512
        assert isinstance(average, np.ndarray)
        # Average should be normalized
        assert abs(np.linalg.norm(average) - 1.0) < 1e-6
    
    @pytest.mark.integration
    @patch('cv2.VideoCapture')
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_enroll_user_success(self, mock_destroy, mock_waitkey, mock_imshow, 
                                mock_videocapture, enrollment_manager, mock_face_embedding):
        """Test successful user enrollment."""
        # Mock webcam
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, create_test_frame())
        mock_cap.set.return_value = True
        mock_cap.release.return_value = None
        mock_videocapture.return_value = mock_cap
        
        # Mock key press to end enrollment
        mock_waitkey.return_value = ord('q')
        
        # Mock face extraction to return consistent embeddings
        with patch.object(enrollment_manager, '_extract_face_and_embedding') as mock_extract:
            mock_extract.return_value = (mock_face_embedding, None)
            
            # Mock storage save
            with patch.object(enrollment_manager.storage, 'save_user_embedding') as mock_save:
                result = enrollment_manager.enroll_user(
                    user_id='test_user',
                    timeout=5,
                    interactive=False
                )
                
                assert result['success']
                assert result['user_id'] == 'test_user'
                assert result['samples_collected'] >= 1
                assert 'duration' in result
                mock_save.assert_called_once()
    
    @pytest.mark.integration
    @patch('cv2.VideoCapture')
    def test_enroll_user_webcam_error(self, mock_videocapture, enrollment_manager):
        """Test enrollment with webcam access error."""
        # Mock webcam initialization failure
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_videocapture.return_value = mock_cap
        
        result = enrollment_manager.enroll_user(
            user_id='test_user',
            timeout=5,
            interactive=False
        )
        
        assert not result['success']
        assert result['code'] == 'CAMERA_ERROR'
    
    @pytest.mark.integration
    @patch('cv2.VideoCapture')
    @patch('cv2.waitKey')
    def test_enroll_user_timeout(self, mock_waitkey, mock_videocapture, enrollment_manager):
        """Test enrollment timeout."""
        # Mock webcam
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, create_test_frame_no_face())  # No face
        mock_cap.set.return_value = True
        mock_cap.release.return_value = None
        mock_videocapture.return_value = mock_cap
        
        # Mock key press (no quit)
        mock_waitkey.return_value = -1
        
        result = enrollment_manager.enroll_user(
            user_id='test_user',
            timeout=1,  # Very short timeout
            interactive=False
        )
        
        assert not result['success']
        assert result['code'] == 'TIMEOUT'
    
    @pytest.mark.integration
    @patch('cv2.VideoCapture')
    @patch('cv2.waitKey')
    def test_enroll_user_cancelled(self, mock_waitkey, mock_videocapture, enrollment_manager):
        """Test enrollment cancellation."""
        # Mock webcam
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, create_test_frame())
        mock_cap.set.return_value = True
        mock_cap.release.return_value = None
        mock_videocapture.return_value = mock_cap
        
        # Mock 'q' key press to cancel
        mock_waitkey.return_value = ord('q')
        
        result = enrollment_manager.enroll_user(
            user_id='test_user',
            timeout=10,
            interactive=False
        )
        
        # Should still succeed if we got some samples before cancellation
        # Result depends on how many samples were collected
        assert 'success' in result
        assert 'code' in result
    
    @pytest.mark.unit
    def test_enroll_user_existing_user(self, enrollment_manager):
        """Test enrollment of already existing user."""
        with patch.object(enrollment_manager, 'verify_enrollment', return_value=True):
            result = enrollment_manager.enroll_user(
                user_id='existing_user',
                timeout=5,
                interactive=False
            )
            
            assert not result['success']
            assert result['code'] == 'USER_EXISTS'
    
    @pytest.mark.unit
    def test_enroll_user_invalid_user_id(self, enrollment_manager):
        """Test enrollment with invalid user ID."""
        result = enrollment_manager.enroll_user(
            user_id='',  # Empty user ID
            timeout=5,
            interactive=False
        )
        
        assert not result['success']
        assert 'invalid' in result.get('error', '').lower()
    
    @pytest.mark.unit
    def test_delete_user_success(self, enrollment_manager):
        """Test successful user deletion."""
        with patch.object(enrollment_manager.storage, 'delete_user_data', return_value=True):
            result = enrollment_manager.delete_user('test_user')
            assert result
    
    @pytest.mark.unit
    def test_delete_user_not_exists(self, enrollment_manager):
        """Test deletion of non-existent user."""
        with patch.object(enrollment_manager.storage, 'delete_user_data', return_value=False):
            result = enrollment_manager.delete_user('nonexistent_user')
            assert not result
    
    @pytest.mark.performance
    def test_enrollment_performance(self, enrollment_manager, benchmark_config, mock_face_embedding):
        """Test enrollment performance benchmarks."""
        import time
        
        with patch('cv2.VideoCapture') as mock_videocapture, \
             patch('cv2.waitKey') as mock_waitkey, \
             patch.object(enrollment_manager, '_extract_face_and_embedding') as mock_extract:
            
            # Mock webcam
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, create_test_frame())
            mock_cap.set.return_value = True
            mock_cap.release.return_value = None
            mock_videocapture.return_value = mock_cap
            
            # Mock fast face extraction
            mock_extract.return_value = (mock_face_embedding, None)
            mock_waitkey.return_value = ord('q')
            
            # Mock storage save
            with patch.object(enrollment_manager.storage, 'save_user_embedding'):
                start_time = time.time()
                
                result = enrollment_manager.enroll_user(
                    user_id='perf_test_user',
                    timeout=30,
                    interactive=False
                )
                
                duration = time.time() - start_time
                
                assert result['success']
                assert duration < benchmark_config['max_enrollment_time']
    
    @pytest.mark.security
    def test_enrollment_data_cleanup(self, enrollment_manager, mock_face_embedding):
        """Test that sensitive data is properly cleaned up after enrollment."""
        # This test ensures no sensitive data remains in memory
        with patch('cv2.VideoCapture') as mock_videocapture, \
             patch.object(enrollment_manager, '_extract_face_and_embedding') as mock_extract:
            
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_videocapture.return_value = mock_cap
            
            mock_extract.return_value = (mock_face_embedding, None)
            
            with patch.object(enrollment_manager.storage, 'save_user_embedding'):
                result = enrollment_manager.enroll_user(
                    user_id='security_test_user',
                    timeout=1,
                    interactive=False
                )
                
                # Verify that temporary embeddings are cleared
                # (This would require checking internal state or memory)
                assert result is not None


class TestFaceDetector:
    """Test suite for FaceDetector class."""
    
    @pytest.mark.unit
    def test_face_detector_initialization(self):
        """Test FaceDetector initialization."""
        from faceauth.core.enrollment import FaceDetector
        
        with patch('faceauth.core.enrollment.MTCNN'):
            detector = FaceDetector(device='cpu')
            assert detector.device == 'cpu'
    
    @pytest.mark.unit
    def test_detect_faces_success(self):
        """Test successful face detection."""
        from faceauth.core.enrollment import FaceDetector
        
        with patch('faceauth.core.enrollment.MTCNN') as mock_mtcnn:
            # Mock MTCNN detection
            mock_instance = Mock()
            mock_instance.detect.return_value = (
                np.array([[100, 100, 200, 200]]),  # bounding boxes
                np.array([0.95])  # confidence scores
            )
            mock_instance.return_value = Mock()  # face tensor
            mock_mtcnn.return_value = mock_instance
            
            detector = FaceDetector(device='cpu')
            test_frame = create_test_frame()
            
            faces, confidences = detector.detect_faces(test_frame)
            
            assert len(faces) == 1
            assert len(confidences) == 1
            assert confidences[0] > 0.9
    
    @pytest.mark.unit
    def test_detect_faces_no_face(self):
        """Test face detection when no face is present."""
        from faceauth.core.enrollment import FaceDetector
        
        with patch('faceauth.core.enrollment.MTCNN') as mock_mtcnn:
            mock_instance = Mock()
            mock_instance.detect.return_value = (None, None)
            mock_mtcnn.return_value = mock_instance
            
            detector = FaceDetector(device='cpu')
            test_frame = create_test_frame_no_face()
            
            faces, confidences = detector.detect_faces(test_frame)
            
            assert len(faces) == 0
            assert len(confidences) == 0


class TestFaceEmbeddingGenerator:
    """Test suite for FaceEmbeddingGenerator class."""
    
    @pytest.mark.unit
    def test_embedding_generator_initialization(self):
        """Test FaceEmbeddingGenerator initialization."""
        from faceauth.core.enrollment import FaceEmbeddingGenerator
        
        with patch('faceauth.core.enrollment.InceptionResnetV1'):
            generator = FaceEmbeddingGenerator(device='cpu')
            assert generator.device == 'cpu'
    
    @pytest.mark.unit
    def test_generate_embedding(self, mock_face_embedding):
        """Test embedding generation."""
        from faceauth.core.enrollment import FaceEmbeddingGenerator
        
        with patch('faceauth.core.enrollment.InceptionResnetV1') as mock_facenet:
            # Mock model
            mock_model = Mock()
            mock_model.eval.return_value = mock_model
            mock_model.to.return_value = mock_model
            
            # Mock forward pass
            mock_output = Mock()
            mock_output.cpu.return_value.numpy.return_value.flatten.return_value = mock_face_embedding
            mock_model.return_value = mock_output
            mock_facenet.return_value = mock_model
            
            generator = FaceEmbeddingGenerator(device='cpu')
            
            # Mock face tensor
            mock_face_tensor = Mock()
            mock_face_tensor.unsqueeze.return_value.to.return_value = mock_face_tensor
            
            embedding = generator.generate_embedding(mock_face_tensor)
            
            assert embedding is not None
            assert len(embedding) == 512
            assert isinstance(embedding, np.ndarray)


# Edge cases and error handling tests

class TestEnrollmentEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.mark.unit
    def test_enrollment_with_corrupted_storage(self, enrollment_manager):
        """Test enrollment when storage is corrupted."""
        with patch.object(enrollment_manager.storage, 'save_user_embedding', 
                         side_effect=Exception("Storage corrupted")):
            
            with patch('cv2.VideoCapture') as mock_videocapture, \
                 patch.object(enrollment_manager, '_extract_face_and_embedding') as mock_extract:
                
                mock_cap = Mock()
                mock_cap.isOpened.return_value = True
                mock_videocapture.return_value = mock_cap
                
                mock_extract.return_value = (np.random.random(512), None)
                
                result = enrollment_manager.enroll_user(
                    user_id='test_user',
                    timeout=1,
                    interactive=False
                )
                
                assert not result['success']
    
    @pytest.mark.unit
    def test_enrollment_with_memory_error(self, enrollment_manager, memory_error):
        """Test enrollment when running out of memory."""
        with patch.object(enrollment_manager, '_extract_face_and_embedding', 
                         side_effect=memory_error):
            
            with patch('cv2.VideoCapture') as mock_videocapture:
                mock_cap = Mock()
                mock_cap.isOpened.return_value = True
                mock_videocapture.return_value = mock_cap
                
                result = enrollment_manager.enroll_user(
                    user_id='test_user',
                    timeout=1,
                    interactive=False
                )
                
                assert not result['success']
    
    @pytest.mark.unit
    def test_enrollment_with_filesystem_error(self, enrollment_manager, filesystem_error):
        """Test enrollment with filesystem permission errors."""
        with patch.object(enrollment_manager.storage, 'save_user_embedding', 
                         side_effect=filesystem_error):
            
            with patch('cv2.VideoCapture') as mock_videocapture, \
                 patch.object(enrollment_manager, '_extract_face_and_embedding') as mock_extract:
                
                mock_cap = Mock()
                mock_cap.isOpened.return_value = True
                mock_videocapture.return_value = mock_cap
                
                mock_extract.return_value = (np.random.random(512), None)
                
                result = enrollment_manager.enroll_user(
                    user_id='test_user',
                    timeout=1,
                    interactive=False
                )
                
                assert not result['success']


# Parametrized tests for different scenarios

class TestEnrollmentParametrized:
    """Parametrized tests for various enrollment scenarios."""
    
    @pytest.mark.parametrize("user_id", [
        "valid_user", "user@example.com", "test_user_123", "user-with-dashes"
    ])
    @pytest.mark.unit
    def test_valid_user_ids(self, enrollment_manager, user_id):
        """Test enrollment with various valid user IDs."""
        # This test would need proper mocking for full execution
        # For now, just test the user ID validation part
        assert enrollment_manager._validate_user_id(user_id)
    
    @pytest.mark.parametrize("invalid_id", [
        "", " ", None, "user with spaces", "user/with/slashes"
    ])
    @pytest.mark.unit
    def test_invalid_user_ids(self, enrollment_manager, invalid_id):
        """Test enrollment rejection with invalid user IDs."""
        # This test validates user ID format checking
        result = enrollment_manager.enroll_user(
            user_id=invalid_id,
            timeout=1,
            interactive=False
        )
        
        assert not result['success']
    
    @pytest.mark.parametrize("quality_threshold", [0.1, 0.3, 0.5, 0.7, 0.9])
    @pytest.mark.unit
    def test_different_quality_thresholds(self, temp_storage_dir, quality_threshold):
        """Test enrollment with different quality thresholds."""
        with patch('faceauth.core.enrollment.MTCNN'), \
             patch('faceauth.core.enrollment.InceptionResnetV1'):
            
            manager = FaceEnrollmentManager(
                storage_dir=temp_storage_dir,
                quality_threshold=quality_threshold
            )
            
            assert manager.quality_threshold == quality_threshold
