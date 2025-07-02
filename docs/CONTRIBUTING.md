# Contributing to FaceAuth

Thank you for your interest in contributing to FaceAuth! This guide will help you get started with contributing to our privacy-first face authentication platform.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Security Considerations](#security-considerations)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Ways to Contribute

We welcome contributions in many forms:

- **🐛 Bug Reports**: Found a bug? Help us fix it!
- **✨ Feature Requests**: Have an idea for improvement?
- **📝 Documentation**: Help improve our docs
- **🔒 Security**: Report security issues responsibly
- **🧪 Testing**: Help us test on different platforms
- **🌍 Translations**: Help make FaceAuth accessible globally
- **💻 Code**: Submit patches and new features
- **🎨 Design**: UI/UX improvements and visual assets

### Before You Start

1. **Read our [Code of Conduct](CODE_OF_CONDUCT.md)**
2. **Review existing [Issues](https://github.com/your-username/faceauth/issues)**
3. **Check [Discussions](https://github.com/your-username/faceauth/discussions)**
4. **Read this contributing guide completely**

### First-Time Contributors

New to open source? Start here:

1. **Good First Issues**: Look for the `good first issue` label
2. **Documentation**: Help improve docs and examples
3. **Testing**: Try FaceAuth on your platform and report results
4. **Community**: Join discussions and help other users

## Development Setup

### Prerequisites

- **Python 3.8+**
- **Git**
- **Camera/Webcam** for testing
- **Development Tools**: Your favorite editor/IDE

### Environment Setup

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/your-username/faceauth.git
cd faceauth

# Add upstream remote
git remote add upstream https://github.com/original-owner/faceauth.git
```

#### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv dev_env

# Activate environment
# Windows:
dev_env\Scripts\activate
# macOS/Linux:
source dev_env/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .  # Install in development mode
```

#### 3. Install Development Tools

```bash
# Install pre-commit hooks
pre-commit install

# Install testing tools
pip install pytest pytest-cov pytest-mock

# Install documentation tools
pip install sphinx sphinx-rtd-theme

# Install linting tools
pip install black flake8 mypy isort
```

#### 4. Verify Setup

```bash
# Run tests
pytest

# Run linting
flake8 faceauth/
black --check faceauth/
mypy faceauth/

# Generate documentation
cd docs
make html
```

### Development Configuration

Create a development configuration file:

```bash
# Copy example config
cp config/development.ini.example config/development.ini

# Set development options
python main.py config-set --config development.ini debug_mode true
python main.py config-set --config development.ini log_level DEBUG
```

## Contributing Guidelines

### Issue Reporting

#### Bug Reports

Use the bug report template and include:

- **Environment**: OS, Python version, FaceAuth version
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error messages and stack traces
- **Logs**: Relevant log excerpts (sanitize sensitive data)

```markdown
**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.6
- FaceAuth: 1.0.0

**Steps to Reproduce:**
1. Run `python main.py enroll-face testuser`
2. Position face in camera
3. Wait for completion

**Expected:** Successful enrollment
**Actual:** Crashes with TypeError

**Error Message:**
```
TypeError: cannot unpack non-sequence NoneType
  File "faceauth/core/enrollment.py", line 142
```

**Additional Context:**
Using USB webcam, good lighting conditions.
```

#### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of desired behavior.

**Describe alternatives you've considered**
Alternative solutions or workarounds.

**Additional context**
Screenshots, examples, use cases.
```

#### Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security@faceauth.dev
2. Include "SECURITY" in the subject line
3. Provide detailed description
4. Allow time for response before disclosure

### Pull Request Process

#### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

#### 2. Make Changes

- **Small, focused commits**: One logical change per commit
- **Clear commit messages**: Follow conventional commit format
- **Test your changes**: Ensure all tests pass
- **Update documentation**: Keep docs current

#### 3. Commit Guidelines

Use [Conventional Commits](https://conventionalcommits.org/):

```bash
# Feature
git commit -m "feat: add batch file encryption support"

# Bug fix
git commit -m "fix: resolve camera detection on macOS"

# Documentation
git commit -m "docs: update installation guide for Ubuntu"

# Breaking change
git commit -m "feat!: change authentication API interface"
```

#### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Use the PR template
```

#### 5. PR Requirements

Before submitting:

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Security considerations addressed
- [ ] Performance impact assessed

## Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these additions:

#### Code Formatting

```python
# Use Black for automatic formatting
black faceauth/

# Maximum line length: 88 characters (Black default)
# Use double quotes for strings
# 4 spaces for indentation
```

#### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import click
import cv2
import numpy as np
import torch

# Local imports
from faceauth.core.authentication import FaceAuthenticator
from faceauth.utils.storage import FaceDataStorage
```

#### Type Hints

```python
# Use type hints for all public functions
def authenticate_user(
    self, 
    user_id: str, 
    timeout: int = 30,
    threshold: float = 0.6
) -> Dict[str, Any]:
    """Authenticate user with face recognition.
    
    Args:
        user_id: Unique identifier for user
        timeout: Maximum time to wait for authentication
        threshold: Similarity threshold for acceptance
        
    Returns:
        Dictionary containing authentication result and metadata
        
    Raises:
        AuthenticationError: If authentication fails
        CameraError: If camera is not available
    """
```

#### Documentation Strings

```python
def process_face_embedding(self, image: np.ndarray) -> np.ndarray:
    """Process face image to generate embedding vector.
    
    Extracts facial features from input image and generates a 
    512-dimensional embedding vector for authentication.
    
    Args:
        image: Input face image as numpy array (H, W, 3)
        
    Returns:
        Face embedding as 512-dimensional numpy array
        
    Raises:
        FaceDetectionError: If no face found in image
        QualityError: If image quality insufficient
        
    Example:
        >>> processor = FaceProcessor()
        >>> image = cv2.imread("face.jpg")
        >>> embedding = processor.process_face_embedding(image)
        >>> embedding.shape
        (512,)
    """
```

### Security Coding Standards

#### Secure Data Handling

```python
# ✅ Good: Secure memory handling
import mlock
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher

class SecureDataHandler:
    def __init__(self):
        self._secure_memory = mlock.mlockall()
    
    def process_sensitive_data(self, data: bytes) -> bytes:
        # Use secure memory for sensitive operations
        with self.allocate_secure_memory(len(data)) as secure_buffer:
            secure_buffer[:] = data
            result = self.encrypt_data(secure_buffer)
            # Automatically zeroed on exit
            return result
```

#### Input Validation

```python
# ✅ Good: Comprehensive input validation
def validate_user_id(self, user_id: str) -> str:
    """Validate and sanitize user ID."""
    if not isinstance(user_id, str):
        raise ValueError("User ID must be string")
    
    if not user_id.strip():
        raise ValueError("User ID cannot be empty")
    
    if len(user_id) > 255:
        raise ValueError("User ID too long")
    
    # Sanitize dangerous characters
    safe_chars = re.match(r'^[a-zA-Z0-9._@-]+$', user_id)
    if not safe_chars:
        raise ValueError("User ID contains invalid characters")
    
    return user_id.strip()
```

#### Error Handling

```python
# ✅ Good: Secure error handling
try:
    result = self.authenticate_user(user_id)
except AuthenticationError as e:
    # Log error without sensitive details
    self.logger.warning(f"Authentication failed for user {user_id[:8]}...")
    # Return generic error to user
    return {"success": False, "error": "Authentication failed"}
except Exception as e:
    # Log full error for debugging
    self.logger.error(f"Unexpected error: {e}", exc_info=True)
    # Return generic error
    return {"success": False, "error": "System error"}
```

### Performance Guidelines

#### Efficient Algorithms

```python
# ✅ Good: Efficient face processing
class OptimizedFaceProcessor:
    def __init__(self):
        # Load model once, reuse
        self.model = self.load_face_model()
        
    def process_batch(self, images: List[np.ndarray]) -> List[np.ndarray]:
        """Process multiple images efficiently."""
        # Batch processing is more efficient
        return self.model.predict_batch(images)
    
    @lru_cache(maxsize=100)
    def get_cached_embedding(self, image_hash: str) -> np.ndarray:
        """Cache embeddings for repeated images."""
        return self.compute_embedding(image_hash)
```

#### Memory Management

```python
# ✅ Good: Proper memory management
class MemoryEfficientProcessor:
    def process_large_dataset(self, image_paths: List[str]) -> None:
        """Process images without loading all into memory."""
        for batch in self.batch_iterator(image_paths, batch_size=32):
            images = [self.load_image(path) for path in batch]
            embeddings = self.process_batch(images)
            self.save_embeddings(embeddings)
            
            # Explicitly clean up
            del images
            del embeddings
            gc.collect()
```

## Testing Requirements

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_authentication.py
│   ├── test_enrollment.py
│   └── test_storage.py
├── integration/             # Integration tests
│   ├── test_full_workflow.py
│   └── test_api.py
├── performance/             # Performance tests
│   └── test_benchmarks.py
├── security/               # Security tests
│   └── test_security.py
└── fixtures/               # Test data
    ├── sample_faces/
    └── test_configs/
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from faceauth.core.authentication import FaceAuthenticator

class TestFaceAuthenticator:
    @pytest.fixture
    def mock_storage(self):
        """Mock storage for testing."""
        storage = Mock()
        storage.load_user_embedding.return_value = np.random.rand(512)
        return storage
    
    @pytest.fixture
    def authenticator(self, mock_storage):
        """Create authenticator with mocked dependencies."""
        return FaceAuthenticator(storage=mock_storage)
    
    def test_successful_authentication(self, authenticator, mock_storage):
        """Test successful face authentication."""
        # Arrange
        user_id = "test_user"
        test_embedding = np.random.rand(512)
        mock_storage.load_user_embedding.return_value = test_embedding
        
        # Act
        with patch.object(authenticator, 'extract_face_embedding') as mock_extract:
            mock_extract.return_value = test_embedding
            result = authenticator.authenticate(user_id)
        
        # Assert
        assert result['success'] is True
        assert result['similarity'] >= 0.9
        mock_storage.load_user_embedding.assert_called_once_with(user_id)
    
    def test_authentication_failure(self, authenticator, mock_storage):
        """Test authentication failure with different embedding."""
        # Arrange
        user_id = "test_user"
        stored_embedding = np.random.rand(512)
        different_embedding = np.random.rand(512)
        mock_storage.load_user_embedding.return_value = stored_embedding
        
        # Act
        with patch.object(authenticator, 'extract_face_embedding') as mock_extract:
            mock_extract.return_value = different_embedding
            result = authenticator.authenticate(user_id)
        
        # Assert
        assert result['success'] is False
        assert result['similarity'] < 0.6
```

#### Integration Tests

```python
class TestFullWorkflow:
    def test_complete_enrollment_and_authentication(self, tmp_path):
        """Test complete workflow from enrollment to authentication."""
        # Setup
        storage_dir = tmp_path / "test_storage"
        config = TestConfig(storage_dir=str(storage_dir))
        
        enrollment_manager = FaceEnrollmentManager(config)
        authenticator = FaceAuthenticator(config)
        
        # Test enrollment
        with patch('cv2.VideoCapture') as mock_camera:
            mock_camera.return_value.read.return_value = (True, self.sample_face_image)
            
            result = enrollment_manager.enroll_user("test_user")
            assert result['success'] is True
        
        # Test authentication
        with patch('cv2.VideoCapture') as mock_camera:
            mock_camera.return_value.read.return_value = (True, self.sample_face_image)
            
            result = authenticator.authenticate("test_user")
            assert result['success'] is True
```

#### Security Tests

```python
class TestSecurity:
    def test_user_isolation(self):
        """Test that users cannot access each other's data."""
        # Create two users
        user1_data = self.create_test_user("user1")
        user2_data = self.create_test_user("user2")
        
        # Verify user1 cannot access user2's data
        with pytest.raises(PermissionError):
            storage.load_user_embedding("user2", user1_data['key'])
    
    def test_encryption_strength(self):
        """Test encryption cannot be easily broken."""
        plaintext = b"sensitive biometric data"
        key = os.urandom(32)
        
        encrypted = encrypt_data(plaintext, key)
        
        # Verify encrypted data looks random
        assert encrypted != plaintext
        assert len(set(encrypted)) > len(encrypted) * 0.7  # High entropy
        
        # Verify decryption works
        decrypted = decrypt_data(encrypted, key)
        assert decrypted == plaintext
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/security/

# Run with coverage
pytest --cov=faceauth --cov-report=html

# Run performance tests
pytest tests/performance/ --benchmark-only

# Run tests with specific markers
pytest -m "not slow"  # Skip slow tests
pytest -m "security"  # Run only security tests
```

### Test Coverage Requirements

- **Minimum coverage**: 80% overall
- **Critical modules**: 95% coverage required
  - Authentication
  - Encryption
  - Storage
  - Security utilities

## Documentation

### Documentation Structure

```
docs/
├── README.md              # Main documentation
├── API_REFERENCE.md       # API documentation
├── USER_GUIDE.md          # User guide
├── SETUP_GUIDE.md         # Installation guide
├── SECURITY.md            # Security documentation
├── TROUBLESHOOTING.md     # Troubleshooting guide
├── CONTRIBUTING.md        # This file
├── examples/              # Code examples
├── tutorials/             # Step-by-step tutorials
└── api/                   # Generated API docs
```

### Writing Documentation

#### Style Guidelines

- **Clear and concise**: Use simple language
- **Step-by-step**: Break complex procedures into steps
- **Examples**: Include code examples and outputs
- **Cross-references**: Link related sections
- **Screenshots**: Include visuals where helpful

#### Code Documentation

```python
class FaceAuthenticator:
    """Face authentication system for secure user verification.
    
    This class provides face recognition capabilities for user authentication
    using state-of-the-art deep learning models. All processing happens 
    locally with no external dependencies.
    
    Attributes:
        storage: Face data storage backend
        model: Face recognition model
        threshold: Similarity threshold for authentication
        
    Example:
        >>> from faceauth.utils.storage import FaceDataStorage
        >>> storage = FaceDataStorage()
        >>> auth = FaceAuthenticator(storage)
        >>> result = auth.authenticate("john.doe")
        >>> print(result['success'])
        True
    """
```

#### API Documentation

Use Sphinx for API documentation:

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Generate API docs
cd docs
sphinx-apidoc -o api ../faceauth
make html
```

## Security Considerations

### Security Review Process

All contributions must undergo security review:

1. **Automated Security Scanning**: Runs on all PRs
2. **Manual Security Review**: For changes to security-critical code
3. **Penetration Testing**: For major features

### Security-Critical Areas

These areas require extra scrutiny:

- **Authentication logic**
- **Encryption/decryption**
- **Key management**
- **Input validation**
- **File operations**
- **Memory management**

### Security Testing

```python
# Example security test
def test_timing_attack_resistance():
    """Test that authentication timing doesn't leak information."""
    valid_user = "valid_user"
    invalid_user = "invalid_user"
    
    # Measure authentication times
    valid_times = []
    invalid_times = []
    
    for _ in range(100):
        start = time.time()
        auth.authenticate(valid_user)
        valid_times.append(time.time() - start)
        
        start = time.time()
        auth.authenticate(invalid_user)
        invalid_times.append(time.time() - start)
    
    # Times should be similar to prevent timing attacks
    valid_avg = sum(valid_times) / len(valid_times)
    invalid_avg = sum(invalid_times) / len(invalid_times)
    
    assert abs(valid_avg - invalid_avg) < 0.1  # Within 100ms
```

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication

- **Be respectful**: Treat everyone with respect
- **Be constructive**: Provide helpful feedback
- **Be patient**: Remember people have different experience levels
- **Be inclusive**: Welcome newcomers and diverse perspectives

### Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check docs first
- **Community**: Help other contributors

### Recognition

We recognize contributors in several ways:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Credited for significant contributions
- **Blog posts**: Featured contributor spotlights
- **Swag**: Stickers and merchandise for regular contributors

## Development Workflow

### Branch Protection

- **Main branch**: Protected, requires PR review
- **Feature branches**: Created from main, merged via PR
- **Release branches**: For preparing releases
- **Hotfix branches**: For critical bug fixes

### Release Process

1. **Feature freeze**: No new features for upcoming release
2. **Testing phase**: Comprehensive testing on all platforms
3. **Documentation review**: Ensure docs are current
4. **Security audit**: Security review of all changes
5. **Release candidate**: Tagged RC for final testing
6. **Release**: Tagged release with changelog

### Continuous Integration

Our CI pipeline includes:

- **Automated testing**: Unit, integration, and security tests
- **Code quality**: Linting, formatting, and type checking
- **Security scanning**: Dependency and code security scans
- **Documentation**: Auto-generation and link checking
- **Performance**: Benchmark regression detection

### Development Tools

Recommended development setup:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Configure IDE (example for VS Code)
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
```

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/your-username/faceauth/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/your-username/faceauth/issues)
- **Security issues**: security@faceauth.dev
- **Other inquiries**: contribute@faceauth.dev

Thank you for contributing to FaceAuth! Together, we're building a more secure and privacy-respecting future.
