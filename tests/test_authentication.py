#!/usr/bin/env python3
"""
Integration tests for FaceAuth authentication module.
Tests the complete authentication workflow.
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path
import numpy as np
import pytest

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from faceauth.core.authentication import FaceAuthenticator, AuthenticationError
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager


class TestAuthenticationIntegration:
    """Integration tests for face authentication."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.security_manager = SecurityManager()
        self.storage = FaceDataStorage(self.test_dir, self.security_manager)
        self.authenticator = FaceAuthenticator(self.storage, similarity_threshold=0.6)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_full_authentication_workflow(self):
        """Test complete authentication workflow with mock data."""
        # Create mock user embedding
        user_id = "test_user"
        mock_embedding = np.random.rand(512).astype(np.float32)
        mock_embedding = mock_embedding / np.linalg.norm(mock_embedding)
        
        # Save mock user data
        success = self.storage.save_user_enrollment(
            user_id, 
            mock_embedding, 
            {'test': True}
        )
        assert success, "Failed to save mock user data"
        
        # Verify user exists
        assert self.storage.user_exists(user_id), "User should exist after enrollment"
        
        # Test loading embedding
        loaded_embedding = self.storage.load_user_embedding(user_id)
        assert loaded_embedding is not None, "Should be able to load saved embedding"
        
        # Test similarity calculation
        similarity = self.authenticator._calculate_similarity(mock_embedding, loaded_embedding)
        assert similarity > 0.99, f"Embeddings should be nearly identical, got {similarity}"
    
    def test_authentication_performance_requirements(self):
        """Test that authentication meets performance requirements."""
        # Test initialization time
        start_time = time.time()
        authenticator = FaceAuthenticator(self.storage)
        init_time = time.time() - start_time
        
        # Initialization should be reasonable (under 5 seconds)
        assert init_time < 5.0, f"Initialization too slow: {init_time:.2f}s"
        
        # Test embedding similarity calculation performance
        embedding1 = np.random.rand(512).astype(np.float32)
        embedding2 = np.random.rand(512).astype(np.float32)
        
        start_time = time.time()
        for _ in range(100):
            similarity = authenticator._calculate_similarity(embedding1, embedding2)
        calc_time = time.time() - start_time
        
        # 100 similarity calculations should be very fast
        assert calc_time < 0.1, f"Similarity calculation too slow: {calc_time:.4f}s for 100 operations"
    
    def test_authentication_error_handling(self):
        """Test authentication error handling."""
        # Test with non-existent user
        result = self.authenticator.authenticate_realtime("nonexistent", timeout=0.1)
        assert not result['success']
        assert result['error_type'] == 'user_not_found'
        
        # Test with very short timeout (should timeout)
        user_id = "test_user"
        mock_embedding = np.random.rand(512).astype(np.float32)
        self.storage.save_user_enrollment(user_id, mock_embedding)
        
        # This should fail quickly due to webcam issues in test environment
        result = self.authenticator.authenticate_realtime(user_id, timeout=0.001)
        assert not result['success']
        # Should fail due to webcam error or timeout
        assert result['error_type'] in ['webcam_error', 'timeout']
    
    def test_metrics_tracking(self):
        """Test that performance metrics are tracked correctly."""
        initial_metrics = self.authenticator.get_performance_metrics()
        assert initial_metrics['total_attempts'] == 0
        assert initial_metrics['successful_attempts'] == 0
        
        # Simulate an authentication attempt
        self.authenticator.total_attempts += 1
        self.authenticator.authentication_times.append(1.5)
        
        updated_metrics = self.authenticator.get_performance_metrics()
        assert updated_metrics['total_attempts'] == 1
        assert updated_metrics['successful_attempts'] == 1
        assert updated_metrics['average_authentication_time'] == 1.5
    
    def test_quality_assessment_integration(self):
        """Test image quality assessment integration."""
        # Create test images
        good_image = np.ones((480, 640, 3), dtype=np.uint8) * 120
        poor_image = np.ones((480, 640, 3), dtype=np.uint8) * 20
        
        good_quality = self.authenticator._assess_image_quality(good_image)
        poor_quality = self.authenticator._assess_image_quality(poor_image)
        
        good_result, _ = self.authenticator._is_good_quality(good_quality)
        poor_result, reason = self.authenticator._is_good_quality(poor_quality)
        
        assert good_result == True
        assert poor_result == False
        assert "dark" in reason.lower()


def test_cli_integration():
    """Test CLI integration (mock test)."""
    # This would test CLI commands but requires actual CLI execution
    # For now, just test that imports work correctly
    try:
        from faceauth.core.authentication import FaceAuthenticator
        from faceauth.utils.storage import FaceDataStorage
        assert True, "CLI integration components import successfully"
    except ImportError as e:
        pytest.fail(f"CLI integration import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
