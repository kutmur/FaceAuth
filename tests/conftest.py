# conftest.py - Pytest configuration and shared fixtures
import pytest
import tempfile
import shutil
import numpy as np
import cv2
import os
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Generator

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from faceauth.core.enrollment import FaceEnrollmentManager
from faceauth.core.authentication import FaceAuthenticator
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager
from faceauth.security.secure_storage import SecureStorage
from faceauth.security.encryption_manager import EncryptionManager


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        'similarity_threshold': 0.6,
        'timeout': 10,
        'max_attempts': 3,
        'image_size': (640, 480),
        'embedding_size': 512
    }


@pytest.fixture
def temp_storage_dir():
    """Create temporary directory for test storage."""
    temp_dir = tempfile.mkdtemp(prefix="faceauth_test_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_webcam():
    """Mock webcam capture for testing."""
    mock_cap = Mock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, create_test_frame())
    mock_cap.set.return_value = True
    mock_cap.release.return_value = None
    return mock_cap


@pytest.fixture
def mock_face_embedding():
    """Generate mock face embedding vector."""
    # Create a realistic 512-dimensional embedding
    np.random.seed(42)  # For reproducible tests
    embedding = np.random.normal(0, 1, 512).astype(np.float32)
    # Normalize to unit vector (like FaceNet does)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


@pytest.fixture
def mock_face_embedding_different():
    """Generate different mock face embedding for negative tests."""
    np.random.seed(123)  # Different seed for different embedding
    embedding = np.random.normal(0, 1, 512).astype(np.float32)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


@pytest.fixture
def mock_mtcnn():
    """Mock MTCNN face detection."""
    with patch('faceauth.core.authentication.MTCNN') as mock:
        mock_instance = Mock()
        mock_instance.return_value = create_mock_face_tensor()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_facenet():
    """Mock FaceNet model."""
    with patch('faceauth.core.authentication.InceptionResnetV1') as mock:
        mock_model = Mock()
        mock_model.eval.return_value = mock_model
        mock_model.to.return_value = mock_model
        
        # Mock forward pass to return embedding
        def mock_forward(x):
            mock_tensor = Mock()
            mock_tensor.cpu.return_value.numpy.return_value.flatten.return_value = create_mock_embedding()
            return mock_tensor
        
        mock_model.return_value = mock_forward
        mock.return_value = mock_model
        yield mock_model


@pytest.fixture
def security_manager(temp_storage_dir):
    """Create test security manager."""
    return SecurityManager(master_key="test_key_123")


@pytest.fixture
def face_storage(temp_storage_dir, security_manager):
    """Create test face data storage."""
    return FaceDataStorage(temp_storage_dir, security_manager)


@pytest.fixture
def secure_storage(temp_storage_dir):
    """Create test secure storage."""
    return SecureStorage(temp_storage_dir)


@pytest.fixture
def face_authenticator(face_storage, temp_storage_dir):
    """Create test face authenticator."""
    with patch('faceauth.core.authentication.MTCNN'), \
         patch('faceauth.core.authentication.InceptionResnetV1'):
        return FaceAuthenticator(face_storage, device='cpu', storage_dir=temp_storage_dir)


@pytest.fixture
def enrollment_manager(temp_storage_dir):
    """Create test enrollment manager."""
    with patch('faceauth.core.enrollment.MTCNN'), \
         patch('faceauth.core.enrollment.InceptionResnetV1'):
        return FaceEnrollmentManager(storage_dir=temp_storage_dir)


@pytest.fixture
def test_files():
    """Create test files for encryption/decryption testing."""
    files = {}
    
    # Small text file
    files['small_text'] = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    files['small_text'].write("This is a test file for FaceAuth encryption testing.")
    files['small_text'].close()
    
    # Binary file (fake image)
    files['binary'] = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
    files['binary'].write(b'\x89PNG\r\n\x1a\n' + os.urandom(1000))
    files['binary'].close()
    
    # Large text file
    files['large_text'] = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    large_content = "Large file content.\n" * 10000  # ~200KB
    files['large_text'].write(large_content)
    files['large_text'].close()
    
    # JSON file
    files['json'] = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    test_data = {'test': True, 'data': [1, 2, 3], 'nested': {'key': 'value'}}
    json.dump(test_data, files['json'])
    files['json'].close()
    
    yield {k: v.name for k, v in files.items()}
    
    # Cleanup
    for file_path in files.values():
        try:
            os.unlink(file_path.name)
        except FileNotFoundError:
            pass


@pytest.fixture
def corrupted_file():
    """Create a corrupted file for testing error handling."""
    corrupted = tempfile.NamedTemporaryFile(delete=False, suffix='.corrupted')
    # Write some random bytes that look like encrypted data but are corrupted
    corrupted.write(b'FACEAUTH_ENCRYPTED' + os.urandom(100))
    corrupted.close()
    
    yield corrupted.name
    
    try:
        os.unlink(corrupted.name)
    except FileNotFoundError:
        pass


# Helper functions for creating test data

def create_test_frame(width=640, height=480):
    """Create a test frame that looks like a webcam image."""
    # Create a realistic-looking frame with a face-like pattern
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add some face-like features
    # Face outline (ellipse)
    cv2.ellipse(frame, (width//2, height//2), (100, 130), 0, 0, 360, (180, 160, 140), -1)
    
    # Eyes
    cv2.circle(frame, (width//2 - 30, height//2 - 20), 10, (50, 50, 50), -1)
    cv2.circle(frame, (width//2 + 30, height//2 - 20), 10, (50, 50, 50), -1)
    
    # Nose
    cv2.line(frame, (width//2, height//2 - 5), (width//2, height//2 + 15), (120, 100, 80), 3)
    
    # Mouth
    cv2.ellipse(frame, (width//2, height//2 + 30), (20, 10), 0, 0, 180, (100, 80, 80), 2)
    
    return frame


def create_test_frame_no_face(width=640, height=480):
    """Create a test frame with no detectable face."""
    # Just noise or simple patterns
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return frame


def create_test_frame_multiple_faces(width=640, height=480):
    """Create a test frame with multiple faces."""
    frame = create_test_frame(width, height)
    
    # Add a second face
    cv2.ellipse(frame, (width//4, height//4), (50, 65), 0, 0, 360, (170, 150, 130), -1)
    cv2.circle(frame, (width//4 - 15, height//4 - 10), 5, (40, 40, 40), -1)
    cv2.circle(frame, (width//4 + 15, height//4 - 10), 5, (40, 40, 40), -1)
    
    return frame


def create_test_frame_poor_quality(width=640, height=480):
    """Create a test frame with poor quality (blurry, dark)."""
    frame = create_test_frame(width, height)
    
    # Make it dark and blurry
    frame = (frame * 0.3).astype(np.uint8)  # Very dark
    frame = cv2.GaussianBlur(frame, (15, 15), 0)  # Very blurry
    
    return frame


def create_mock_face_tensor():
    """Create a mock face tensor for MTCNN output."""
    # Return a mock tensor that represents a detected face
    mock_tensor = Mock()
    mock_tensor.unsqueeze.return_value.to.return_value = mock_tensor
    return mock_tensor


def create_mock_embedding():
    """Create a mock face embedding."""
    np.random.seed(42)
    embedding = np.random.normal(0, 1, 512).astype(np.float32)
    return embedding / np.linalg.norm(embedding)


@pytest.fixture
def mock_cv2_videocapture():
    """Mock cv2.VideoCapture for testing."""
    with patch('cv2.VideoCapture') as mock:
        mock_instance = Mock()
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, create_test_frame())
        mock_instance.set.return_value = True
        mock_instance.release.return_value = None
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_cv2_functions():
    """Mock cv2 functions for testing."""
    with patch('cv2.cvtColor') as mock_cvtcolor, \
         patch('cv2.putText') as mock_puttext, \
         patch('cv2.imshow') as mock_imshow, \
         patch('cv2.waitKey') as mock_waitkey, \
         patch('cv2.destroyAllWindows') as mock_destroy:
        
        mock_cvtcolor.return_value = create_test_frame()
        mock_waitkey.return_value = ord('q')  # Simulate 'q' press to quit
        
        yield {
            'cvtColor': mock_cvtcolor,
            'putText': mock_puttext,
            'imshow': mock_imshow,
            'waitKey': mock_waitkey,
            'destroyAllWindows': mock_destroy
        }


# Parametrized test data

@pytest.fixture(params=[
    'valid_user_123',
    'user@example.com',
    'test_user_with_underscores',
    'user-with-dashes'
])
def valid_user_id(request):
    """Parametrized valid user IDs for testing."""
    return request.param


@pytest.fixture(params=[
    '',
    ' ',
    None,
    'user with spaces',
    'user/with/slashes',
    'user\\with\\backslashes'
])
def invalid_user_id(request):
    """Parametrized invalid user IDs for testing."""
    return request.param


@pytest.fixture(params=[0.1, 0.3, 0.5, 0.7, 0.9])
def similarity_threshold(request):
    """Parametrized similarity thresholds for testing."""
    return request.param


@pytest.fixture(params=[5, 10, 30, 60])
def timeout_values(request):
    """Parametrized timeout values for testing."""
    return request.param


# Performance benchmarking fixture

@pytest.fixture
def benchmark_config():
    """Configuration for performance benchmarks."""
    return {
        'max_enrollment_time': 30.0,  # seconds
        'max_authentication_time': 5.0,  # seconds
        'max_encryption_time_per_mb': 2.0,  # seconds per MB
        'max_decryption_time_per_mb': 2.0,  # seconds per MB
        'min_similarity_accuracy': 0.95,  # 95% accuracy
        'max_false_positive_rate': 0.01,  # 1% FPR
        'max_false_negative_rate': 0.05   # 5% FNR
    }


# Error simulation fixtures

@pytest.fixture
def network_error():
    """Simulate network errors (though FaceAuth shouldn't use network)."""
    with patch('socket.socket') as mock_socket:
        mock_socket.side_effect = ConnectionError("Network unavailable")
        yield mock_socket


@pytest.fixture
def filesystem_error():
    """Simulate filesystem errors."""
    def raise_permission_error(*args, **kwargs):
        raise PermissionError("Access denied")
    
    return raise_permission_error


@pytest.fixture
def memory_error():
    """Simulate memory allocation errors."""
    def raise_memory_error(*args, **kwargs):
        raise MemoryError("Out of memory")
    
    return raise_memory_error


# Database/Storage error simulation

@pytest.fixture
def storage_corruption():
    """Simulate storage corruption scenarios."""
    def corrupt_data(data):
        # Corrupt some bytes in the middle
        if len(data) > 10:
            corrupted = bytearray(data)
            corrupted[len(data)//2:len(data)//2+5] = b'\x00\xFF\x00\xFF\x00'
            return bytes(corrupted)
        return data
    
    return corrupt_data


# Test markers for different test categories

pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance benchmark"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring hardware (webcam)"
    )


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    # Clean up any temporary files created during tests
    for pattern in ['test_*.tmp', '*.encrypted', 'faceauth_test_*']:
        for file in Path('.').glob(pattern):
            try:
                file.unlink()
            except (FileNotFoundError, PermissionError):
                pass
