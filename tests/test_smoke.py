#!/usr/bin/env python3
"""
Simple smoke tests to verify FaceAuth test infrastructure.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import numpy as np


class TestInfrastructure:
    """Test basic infrastructure and imports."""
    
    def test_python_version(self):
        """Test that we're running on a supported Python version."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    def test_numpy_available(self):
        """Test that numpy is available and working."""
        arr = np.array([1, 2, 3])
        assert arr.sum() == 6
    
    def test_temp_directory_creation(self):
        """Test temporary directory creation for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            assert temp_path.exists()
            assert temp_path.is_dir()
    
    def test_project_structure(self):
        """Test that project structure is in place."""
        project_root = Path(__file__).parent.parent
        
        # Check for main package
        faceauth_dir = project_root / "faceauth"
        assert faceauth_dir.exists(), "faceauth package directory not found"
        
        # Check for core modules
        core_dir = faceauth_dir / "core"
        assert core_dir.exists(), "faceauth.core module not found"
        
        # Check for utils
        utils_dir = faceauth_dir / "utils"
        assert utils_dir.exists(), "faceauth.utils module not found"


class TestMockData:
    """Test mock data generation for testing."""
    
    def test_mock_face_embedding(self):
        """Test generation of mock face embeddings."""
        # Generate a mock 128-dimensional face embedding
        embedding = np.random.rand(128).astype(np.float32)
        
        assert embedding.shape == (128,)
        assert embedding.dtype == np.float32
        assert 0.0 <= embedding.min() <= 1.0
        assert 0.0 <= embedding.max() <= 1.0
    
    def test_mock_user_data(self):
        """Test mock user data structure."""
        user_data = {
            "user_id": "test_user_001",
            "encoding": np.random.rand(128),
            "enrollment_date": "2025-01-01",
            "quality_scores": [0.95, 0.87, 0.92]
        }
        
        assert "user_id" in user_data
        assert "encoding" in user_data
        assert len(user_data["encoding"]) == 128
        assert len(user_data["quality_scores"]) == 3


class TestBasicSecurity:
    """Basic security-related tests."""
    
    def test_secure_random_generation(self):
        """Test secure random number generation."""
        import secrets
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(32)
        assert len(random_bytes) == 32
        
        # Generate random string
        random_string = secrets.token_urlsafe(32)
        assert len(random_string) > 0
    
    def test_memory_cleanup_simulation(self):
        """Test memory cleanup simulation."""
        # Create sensitive data
        sensitive_data = np.random.rand(1000)
        
        # Simulate secure deletion
        sensitive_data.fill(0)
        
        # Verify data is zeroed
        assert np.all(sensitive_data == 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
