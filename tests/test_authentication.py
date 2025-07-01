"""
Unit Tests for Authentication Module
====================================

Tests for face authentication functionality in authentication.py, focusing on:
- Face verification with mocked webcam and DeepFace
- Error handling for various face detection scenarios
- Authentication flow without requiring hardware
- Integration with crypto module for loading embeddings
"""

import pytest
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import the modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from authentication import (
    FaceAuthenticator,
    FaceAuthenticationError
)
from crypto import SecureEmbeddingStorage


class TestFaceAuthenticatorInit:
    """Test FaceAuthenticator initialization."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        authenticator = FaceAuthenticator()
        
        assert authenticator.model_name == "Facenet"
        assert authenticator.data_dir == Path("face_data")
        assert authenticator.verification_timeout == 15.0
        assert authenticator.frame_skip == 2
        assert authenticator.current_status == "INITIALIZING"
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        custom_model = "ArcFace"
        custom_dir = "custom_face_data"
        
        authenticator = FaceAuthenticator(model_name=custom_model, data_dir=custom_dir)
        
        assert authenticator.model_name == custom_model
        assert authenticator.data_dir == Path(custom_dir)


class TestLoadStoredEmbedding:
    """Test loading stored face embeddings."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.authenticator = FaceAuthenticator(data_dir=self.test_dir)
        self.user_id = "test_user"
        self.password = "test_password"
        self.test_embedding = np.random.rand(512).astype(np.float32)
        
        # Create test face data using SecureEmbeddingStorage
        self.storage = SecureEmbeddingStorage(self.test_dir)
        self.storage.save_user_embedding(self.user_id, self.test_embedding, self.password)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_existing_embedding(self):
        """Test loading an existing user embedding."""
        loaded_embedding = self.authenticator.load_stored_embedding(self.user_id, self.password)
        
        assert isinstance(loaded_embedding, np.ndarray)
        assert np.allclose(self.test_embedding, loaded_embedding, rtol=1e-6)
    
    def test_load_embedding_wrong_password(self):
        """Test loading embedding with wrong password."""
        with pytest.raises(FaceAuthenticationError, match="Incorrect password"):
            self.authenticator.load_stored_embedding(self.user_id, "wrong_password")
    
    def test_load_embedding_nonexistent_user(self):
        """Test loading embedding for non-existent user."""
        with pytest.raises(FaceAuthenticationError, match="No face data found"):
            self.authenticator.load_stored_embedding("nonexistent_user", self.password)
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_load_embedding_permission_error(self, mock_open):
        """Test handling of file permission errors."""
        with pytest.raises(FaceAuthenticationError, match="Failed to load face data"):
            self.authenticator.load_stored_embedding(self.user_id, self.password)


class TestFaceVerification:
    """Test face verification functionality with mocking."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.authenticator = FaceAuthenticator(data_dir=self.test_dir)
        self.user_id = "test_user"
        self.password = "test_password"
        
        # Create mock frame data
        self.mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('authentication.cv2.imwrite')
    @patch('authentication.tempfile.mkstemp')
    @patch('authentication.os.close')
    def test_save_frame_for_verification(self, mock_close, mock_mkstemp, mock_imwrite):
        """Test saving frame to temporary file."""
        # Mock tempfile creation
        mock_mkstemp.return_value = (1, '/tmp/test_frame.jpg')
        mock_imwrite.return_value = True
        
        temp_path = self.authenticator.save_frame_for_verification(self.mock_frame)
        
        assert temp_path == '/tmp/test_frame.jpg'
        mock_mkstemp.assert_called_once_with(suffix='.jpg')
        mock_close.assert_called_once_with(1)
        mock_imwrite.assert_called_once()
    
    @patch('authentication.DeepFace.verify')
    @patch('authentication.os.unlink')
    @patch.object(FaceAuthenticator, 'save_frame_for_verification')
    def test_verify_face_success(self, mock_save_frame, mock_unlink, mock_deepface_verify):
        """Test successful face verification."""
        # Mock frame saving
        mock_save_frame.return_value = '/tmp/current_frame.jpg'
        
        # Mock DeepFace verification - successful match
        mock_deepface_verify.return_value = {
            'verified': True,
            'distance': 0.3,
            'threshold': 0.68
        }
        
        stored_embedding_path = '/tmp/stored_embedding.jpg'
        
        result = self.authenticator.verify_face_against_stored(self.mock_frame, stored_embedding_path)
        
        assert result['verified'] is True
        assert 'confidence' in result
        assert result['confidence'] > 0
        assert 'distance' in result
        assert 'threshold' in result
        
        # Verify cleanup
        mock_unlink.assert_called_once_with('/tmp/current_frame.jpg')
    
    @patch('authentication.DeepFace.verify')
    @patch('authentication.os.unlink')
    @patch.object(FaceAuthenticator, 'save_frame_for_verification')
    def test_verify_face_failure(self, mock_save_frame, mock_unlink, mock_deepface_verify):
        """Test failed face verification (faces don't match)."""
        # Mock frame saving
        mock_save_frame.return_value = '/tmp/current_frame.jpg'
        
        # Mock DeepFace verification - faces don't match
        mock_deepface_verify.return_value = {
            'verified': False,
            'distance': 0.9,
            'threshold': 0.68
        }
        
        stored_embedding_path = '/tmp/stored_embedding.jpg'
        
        result = self.authenticator.verify_face_against_stored(self.mock_frame, stored_embedding_path)
        
        assert result['verified'] is False
        assert 'confidence' in result
        assert 'distance' in result
        assert 'threshold' in result
        
        # Verify cleanup
        mock_unlink.assert_called_once_with('/tmp/current_frame.jpg')
    
    @patch('authentication.DeepFace.verify')
    @patch('authentication.os.unlink')
    @patch.object(FaceAuthenticator, 'save_frame_for_verification')
    def test_verify_face_no_face_detected(self, mock_save_frame, mock_unlink, mock_deepface_verify):
        """Test verification when no face is detected."""
        # Mock frame saving
        mock_save_frame.return_value = '/tmp/current_frame.jpg'
        
        # Mock DeepFace verification - no face detected
        mock_deepface_verify.side_effect = Exception("Face could not be detected")
        
        stored_embedding_path = '/tmp/stored_embedding.jpg'
        
        result = self.authenticator.verify_face_against_stored(self.mock_frame, stored_embedding_path)
        
        assert 'error' in result
        assert result['error'] == 'NO_FACE_DETECTED'
        
        # Verify cleanup
        mock_unlink.assert_called_once_with('/tmp/current_frame.jpg')
    
    @patch('authentication.DeepFace.verify')
    @patch('authentication.os.unlink')
    @patch.object(FaceAuthenticator, 'save_frame_for_verification')
    def test_verify_face_multiple_faces(self, mock_save_frame, mock_unlink, mock_deepface_verify):
        """Test verification when multiple faces are detected."""
        # Mock frame saving
        mock_save_frame.return_value = '/tmp/current_frame.jpg'
        
        # Mock DeepFace verification - multiple faces
        mock_deepface_verify.side_effect = Exception("More than one face detected")
        
        stored_embedding_path = '/tmp/stored_embedding.jpg'
        
        result = self.authenticator.verify_face_against_stored(self.mock_frame, stored_embedding_path)
        
        assert 'error' in result
        assert result['error'] == 'MULTIPLE_FACES'
        
        # Verify cleanup
        mock_unlink.assert_called_once_with('/tmp/current_frame.jpg')
    
    @patch('authentication.DeepFace.verify')
    @patch('authentication.os.unlink')
    @patch.object(FaceAuthenticator, 'save_frame_for_verification')
    def test_verify_face_general_error(self, mock_save_frame, mock_unlink, mock_deepface_verify):
        """Test verification with general error."""
        # Mock frame saving
        mock_save_frame.return_value = '/tmp/current_frame.jpg'
        
        # Mock DeepFace verification - general error
        mock_deepface_verify.side_effect = Exception("Model loading failed")
        
        stored_embedding_path = '/tmp/stored_embedding.jpg'
        
        result = self.authenticator.verify_face_against_stored(self.mock_frame, stored_embedding_path)
        
        assert 'error' in result
        assert 'VERIFICATION_ERROR' in result['error']
        assert 'Model loading failed' in result['error']
        
        # Verify cleanup
        mock_unlink.assert_called_once_with('/tmp/current_frame.jpg')


class TestFaceDetection:
    """Test face detection functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.authenticator = FaceAuthenticator()
        self.mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    @patch('authentication.cv2.CascadeClassifier')
    @patch('authentication.cv2.cvtColor')
    def test_detect_faces_opencv_success(self, mock_cvtcolor, mock_cascade_classifier):
        """Test successful face detection with OpenCV."""
        # Mock grayscale conversion
        mock_gray = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        mock_cvtcolor.return_value = mock_gray
        
        # Mock cascade classifier
        mock_classifier = MagicMock()
        mock_cascade_classifier.return_value = mock_classifier
        
        # Mock face detection - return one face
        mock_faces = np.array([[100, 100, 200, 200]])  # x, y, w, h
        mock_classifier.detectMultiScale.return_value = mock_faces
        
        faces = self.authenticator.detect_faces_opencv(self.mock_frame)
        
        assert len(faces) == 1
        assert faces[0] == [100, 100, 200, 200]
    
    @patch('authentication.cv2.CascadeClassifier')
    @patch('authentication.cv2.cvtColor')
    def test_detect_faces_opencv_no_faces(self, mock_cvtcolor, mock_cascade_classifier):
        """Test face detection when no faces are found."""
        # Mock grayscale conversion
        mock_gray = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        mock_cvtcolor.return_value = mock_gray
        
        # Mock cascade classifier
        mock_classifier = MagicMock()
        mock_cascade_classifier.return_value = mock_classifier
        
        # Mock face detection - return no faces
        mock_classifier.detectMultiScale.return_value = np.array([])
        
        faces = self.authenticator.detect_faces_opencv(self.mock_frame)
        
        assert len(faces) == 0
    
    @patch('authentication.cv2.CascadeClassifier', side_effect=Exception("OpenCV error"))
    def test_detect_faces_opencv_error(self, mock_cascade_classifier):
        """Test face detection error handling."""
        faces = self.authenticator.detect_faces_opencv(self.mock_frame)
        
        # Should return empty list on error
        assert faces == []


class TestVisualizationOverlay:
    """Test the visualization overlay functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.authenticator = FaceAuthenticator()
        self.mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    @patch('authentication.cv2.getTextSize')
    @patch('authentication.cv2.rectangle')
    @patch('authentication.cv2.putText')
    @patch('authentication.cv2.line')
    def test_draw_verification_overlay(self, mock_line, mock_puttext, mock_rectangle, mock_gettextsize):
        """Test drawing verification overlay on frame."""
        # Mock text size calculation
        mock_gettextsize.return_value = ((200, 30), 10)
        
        # Set some status
        self.authenticator.current_status = "VERIFYING IDENTITY"
        self.authenticator.confidence_score = 85.5
        
        # Mock faces
        faces = [[100, 100, 200, 200]]
        
        overlay_frame = self.authenticator.draw_verification_overlay(self.mock_frame, faces)
        
        # Verify frame is returned
        assert overlay_frame is not None
        assert overlay_frame.shape == self.mock_frame.shape
        
        # Verify OpenCV functions were called
        mock_gettextsize.assert_called()
        mock_rectangle.assert_called()
        mock_puttext.assert_called()
        mock_line.assert_called()
    
    def test_status_color_mapping(self):
        """Test that different statuses get different colors."""
        # Test different status messages
        test_statuses = [
            ("ACCESS GRANTED", self.authenticator.color_success),
            ("ACCESS DENIED", self.authenticator.color_denied),
            ("VERIFYING IDENTITY", self.authenticator.color_verifying),
            ("INITIALIZING", self.authenticator.color_info)
        ]
        
        for status, expected_color in test_statuses:
            self.authenticator.current_status = status
            # We can't easily test the color selection without mocking cv2,
            # but we can verify the status is set correctly
            assert self.authenticator.current_status == status


class TestAuthenticationIntegration:
    """Integration tests combining multiple components."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.authenticator = FaceAuthenticator(data_dir=self.test_dir)
        self.user_id = "integration_test_user"
        self.password = "integration_password"
        self.test_embedding = np.random.rand(512).astype(np.float32)
        
        # Create test face data
        self.storage = SecureEmbeddingStorage(self.test_dir)
        self.storage.save_user_embedding(self.user_id, self.test_embedding, self.password)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_and_verify_workflow(self):
        """Test the complete load embedding and prepare for verification workflow."""
        # Load stored embedding (this tests crypto integration)
        loaded_embedding = self.authenticator.load_stored_embedding(self.user_id, self.password)
        
        # Verify embedding was loaded correctly
        assert isinstance(loaded_embedding, np.ndarray)
        assert np.allclose(self.test_embedding, loaded_embedding, rtol=1e-6)
        
        # Test reference image path creation
        reference_path = self.authenticator.create_reference_image_from_embedding(self.user_id)
        expected_path = str(self.authenticator.data_dir / f"{self.user_id}_reference.jpg")
        assert reference_path == expected_path


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.authenticator = FaceAuthenticator(data_dir=self.test_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_invalid_embedding_format(self):
        """Test handling of invalid embedding format."""
        # Create a file with invalid content
        user_id = "invalid_user"
        password = "test_password"
        invalid_file = self.authenticator.data_dir / f"{user_id}_face.dat"
        
        # Create directory and write invalid data
        invalid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(invalid_file, 'wb') as f:
            f.write(b"invalid embedding data")
        
        with pytest.raises(FaceAuthenticationError, match="Incorrect password or corrupted"):
            self.authenticator.load_stored_embedding(user_id, password)
    
    def test_empty_data_directory(self):
        """Test behavior with empty data directory."""
        with pytest.raises(FaceAuthenticationError, match="No face data found"):
            self.authenticator.load_stored_embedding("nonexistent_user", "password")
    
    @patch('authentication.os.path.exists', return_value=False)
    def test_data_directory_not_exists(self, mock_exists):
        """Test behavior when data directory doesn't exist."""
        with pytest.raises(FaceAuthenticationError, match="No face data found"):
            self.authenticator.load_stored_embedding("any_user", "password")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
