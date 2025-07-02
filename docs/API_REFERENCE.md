# FaceAuth API Documentation

## Overview

FaceAuth provides both programmatic Python APIs and a comprehensive CLI interface for face authentication and file encryption. This document covers the complete API reference for developers.

## Table of Contents

- [Core Classes](#core-classes)
- [CLI Interface](#cli-interface)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Security APIs](#security-apis)
- [Performance Monitoring](#performance-monitoring)

## Core Classes

### FaceEnrollment

The `FaceEnrollment` class handles user enrollment workflows.

```python
from faceauth.core.enrollment import FaceEnrollment
from faceauth.utils.storage import FaceDataStorage

# Initialize enrollment system
storage = FaceDataStorage()
enrollment = FaceEnrollment(storage)

# Enroll a user
result = enrollment.enroll_user(
    user_id="john_doe",
    min_samples=3,
    quality_threshold=0.8,
    timeout=30
)

if result.success:
    print(f"User enrolled with {result.samples_collected} samples")
    print(f"Average quality: {result.average_quality:.3f}")
else:
    print(f"Enrollment failed: {result.error}")
```

#### Methods

**`enroll_user(user_id, min_samples=3, quality_threshold=0.8, timeout=30)`**
- **Description**: Enroll a new user with face authentication
- **Parameters**:
  - `user_id` (str): Unique identifier for the user
  - `min_samples` (int): Minimum face samples to collect (default: 3)
  - `quality_threshold` (float): Minimum quality score (0.0-1.0, default: 0.8)
  - `timeout` (int): Maximum enrollment time in seconds (default: 30)
- **Returns**: `EnrollmentResult` object
- **Raises**: `EnrollmentError` on critical failures

**`get_user_info(user_id)`**
- **Description**: Get enrollment information for a user
- **Parameters**: `user_id` (str): User identifier
- **Returns**: Dictionary with user enrollment data
- **Raises**: `UserNotFoundError` if user doesn't exist

### FaceAuthenticator

The `FaceAuthenticator` class handles real-time face authentication.

```python
from faceauth.core.authentication import FaceAuthenticator

# Initialize authenticator
authenticator = FaceAuthenticator(
    similarity_threshold=0.6,
    device='cpu'  # or 'cuda' for GPU acceleration
)

# Authenticate user
result = authenticator.authenticate_realtime(
    user_id="john_doe",
    timeout=10,
    max_attempts=5
)

if result['success']:
    print(f"Authentication successful!")
    print(f"Similarity: {result['similarity']:.3f}")
    print(f"Duration: {result['duration']:.2f}s")
else:
    print(f"Authentication failed: {result['error']}")
```

#### Methods

**`authenticate_realtime(user_id, timeout=10, max_attempts=5)`**
- **Description**: Perform real-time face authentication via webcam
- **Parameters**:
  - `user_id` (str): User to authenticate
  - `timeout` (int): Maximum authentication time in seconds
  - `max_attempts` (int): Maximum authentication attempts
- **Returns**: Dictionary with authentication results
- **Key Result Fields**:
  - `success` (bool): Whether authentication succeeded
  - `similarity` (float): Face similarity score (0.0-1.0)
  - `duration` (float): Authentication duration in seconds
  - `error` (str): Error message if failed

**`authenticate(user_id, timeout=10)`**
- **Description**: Simple boolean authentication check
- **Parameters**: Same as `authenticate_realtime` but fewer options
- **Returns**: `True` if authenticated, `False` otherwise

**`get_performance_metrics()`**
- **Description**: Get authentication performance statistics
- **Returns**: Dictionary with performance data

### EncryptionManager

The `EncryptionManager` class handles file encryption/decryption with face authentication.

```python
from faceauth.security.encryption_manager import EncryptionManager

# Initialize encryption manager
encryption = EncryptionManager()

# Encrypt a file with password
encryption.encrypt_file(
    input_path="secret_document.pdf",
    output_path="secret_document.pdf.enc",
    password="my_secure_password"
)

# Decrypt the file
encryption.decrypt_file(
    input_path="secret_document.pdf.enc",
    output_path="decrypted_document.pdf",
    password="my_secure_password"
)
```

#### Methods

**`encrypt_file(input_path, output_path, password)`**
- **Description**: Encrypt a file with AES-256-GCM
- **Parameters**:
  - `input_path` (str): Path to file to encrypt
  - `output_path` (str): Path for encrypted output
  - `password` (str): Encryption password
- **Returns**: `True` on success
- **Raises**: `EncryptionError` on failures

**`decrypt_file(input_path, output_path, password)`**
- **Description**: Decrypt an encrypted file
- **Parameters**: Same as `encrypt_file`
- **Returns**: `True` on success
- **Raises**: `DecryptionError` on failures

## CLI Interface

FaceAuth provides a comprehensive command-line interface for all operations.

### Core Commands

#### Face Management

```bash
# Enroll a new user
python main.py enroll-face <user_id>

# Authenticate user
python main.py verify-face <user_id>

# List enrolled users
python main.py list-users

# Delete user data
python main.py delete-user <user_id>
```

#### File Encryption

```bash
# Encrypt file with face authentication
python main.py encrypt-file <file_path> [--output <output_path>]

# Decrypt file with face authentication  
python main.py decrypt-file <file_path> [--output <output_path>]

# Batch encrypt multiple files
python main.py encrypt-batch <directory>
```

#### System Management

```bash
# Check system health
python main.py system-check

# View performance metrics
python main.py auth-metrics

# Security audit
python main.py security-audit

# Privacy compliance check
python main.py privacy-check
```

#### Configuration

```bash
# Initialize configuration
python main.py config-init

# Show current configuration
python main.py config-show

# Set configuration option
python main.py config-set <key> <value>

# Install shell completion
python main.py install-completion
```

### Command Options

Most commands support additional options:

```bash
# Common options
--verbose, -v           # Verbose output
--quiet, -q            # Quiet mode
--config <path>        # Custom config file
--storage-dir <path>   # Custom storage directory

# Enrollment options
--min-samples <n>      # Minimum face samples (default: 3)
--quality <threshold>  # Quality threshold (default: 0.8)
--timeout <seconds>    # Enrollment timeout (default: 30)

# Authentication options
--similarity <threshold>  # Similarity threshold (default: 0.6)
--max-attempts <n>       # Maximum attempts (default: 5)
--timeout <seconds>      # Authentication timeout (default: 10)
```

## Configuration

FaceAuth uses a configuration system for persistent settings.

### Configuration File

Default location: `~/.faceauth/config.yaml`

```yaml
# FaceAuth Configuration
storage:
  directory: "~/.faceauth/storage"
  backup_enabled: true
  encryption_enabled: true

authentication:
  similarity_threshold: 0.6
  max_attempts: 5
  timeout: 10
  device: "auto"  # "cpu", "cuda", or "auto"

enrollment:
  min_samples: 3
  quality_threshold: 0.8
  timeout: 30

privacy:
  consent_required: true
  audit_enabled: true
  data_retention_days: 365

security:
  audit_log_encryption: true
  memory_protection: true
  secure_deletion: true
```

### Programmatic Configuration

```python
from faceauth.config import FaceAuthConfig

# Load configuration
config = FaceAuthConfig.load()

# Modify settings
config.authentication.similarity_threshold = 0.7
config.enrollment.min_samples = 5

# Save configuration
config.save()

# Get configuration value
threshold = config.get('authentication.similarity_threshold')
```

## Error Handling

FaceAuth defines specific exception types for different error categories.

### Exception Hierarchy

```python
FaceAuthError                    # Base exception
├── EnrollmentError              # Enrollment failures
│   ├── EnrollmentTimeoutError   # Enrollment timeout
│   ├── FaceQualityError         # Poor face quality
│   └── CameraError              # Camera access issues
├── AuthenticationError          # Authentication failures
│   ├── UserNotFoundError        # User not enrolled
│   ├── AuthenticationTimeoutError # Auth timeout
│   └── SimilarityThresholdError # Below similarity threshold
├── EncryptionError              # Encryption failures
│   ├── KeyDerivationError       # Key derivation issues
│   └── FileEncryptionError      # File encryption failures
├── StorageError                 # Storage system errors
│   ├── DataCorruptionError      # Data integrity issues
│   └── PermissionError          # File permission errors
└── SecurityError                # Security-related errors
    ├── AuditLogError            # Audit logging failures
    └── PrivacyViolationError    # Privacy policy violations
```

### Error Handling Example

```python
from faceauth.core.enrollment import FaceEnrollment
from faceauth.exceptions import (
    EnrollmentError, 
    EnrollmentTimeoutError,
    FaceQualityError
)

try:
    enrollment = FaceEnrollment()
    result = enrollment.enroll_user("john_doe")
    
except EnrollmentTimeoutError:
    print("Enrollment timed out. Please try again.")
    
except FaceQualityError as e:
    print(f"Face quality too low: {e.quality_score:.3f}")
    print("Please ensure good lighting and face the camera directly.")
    
except EnrollmentError as e:
    print(f"Enrollment failed: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security APIs

### Audit Logging

```python
from faceauth.security.audit_logger import SecureAuditLogger

# Initialize audit logger
logger = SecureAuditLogger("/path/to/logs")

# Log authentication events
logger.log_authentication_success("user_id", {"ip": "192.168.1.1"})
logger.log_authentication_failure("user_id", "reason", {"attempts": 3})

# Log privacy events
logger.log_privacy_event("DATA_DELETION", {"user_id": "john_doe"})

# Export logs for compliance
logger.export_logs("/path/to/export.json")
```

### Privacy Management

```python
from faceauth.security.privacy_manager import PrivacyManager

# Initialize privacy manager
privacy = PrivacyManager("/path/to/privacy")

# Register user consent
privacy.register_user_consent("user_id", [
    "data_collection",
    "biometric_processing", 
    "storage"
])

# Check processing permissions
if privacy.is_processing_allowed("user_id"):
    # Proceed with biometric processing
    pass

# Generate privacy report
report = privacy.generate_privacy_report("user_id")
```

### Compliance Checking

```python
from faceauth.security.compliance_checker import ComplianceChecker

# Initialize compliance checker
checker = ComplianceChecker("/path/to/data")

# Check GDPR compliance
gdpr_result = checker.check_gdpr_compliance()
print(f"GDPR Compliant: {gdpr_result['overall_compliance']}")

# Check CCPA compliance
ccpa_result = checker.check_ccpa_compliance()

# Generate compliance report
report = checker.generate_compliance_report()
checker.export_compliance_report("/path/to/report.json")
```

## Performance Monitoring

### System Metrics

```python
from faceauth.core.authentication import FaceAuthenticator

authenticator = FaceAuthenticator()

# Get performance metrics
metrics = authenticator.get_performance_metrics()

print(f"Average auth time: {metrics['average_authentication_time']:.2f}s")
print(f"Success rate: {metrics['successful_attempts']}/{metrics['total_attempts']}")
print(f"False positive rate: {metrics['false_positive_rate']:.3f}")
print(f"False negative rate: {metrics['false_negative_rate']:.3f}")
```

### Storage Statistics

```python
from faceauth.utils.storage import FaceDataStorage

storage = FaceDataStorage()

# Get storage information
stats = storage.get_statistics()

print(f"Total users: {stats['user_count']}")
print(f"Storage size: {stats['total_size_bytes']:,} bytes")
print(f"Average user size: {stats['average_user_size_bytes']:,} bytes")
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify
from faceauth.core.authentication import FaceAuthenticator

app = Flask(__name__)
authenticator = FaceAuthenticator()

@app.route('/api/auth', methods=['POST'])
def authenticate_user():
    user_id = request.json.get('user_id')
    
    try:
        result = authenticator.authenticate_realtime(user_id, timeout=5)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Desktop Application Integration

```python
import tkinter as tk
from faceauth.core.enrollment import FaceEnrollment

class FaceAuthGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.enrollment = FaceEnrollment()
        self.setup_ui()
    
    def enroll_user(self):
        user_id = self.user_entry.get()
        try:
            result = self.enrollment.enroll_user(user_id)
            if result.success:
                tk.messagebox.showinfo("Success", "User enrolled successfully!")
            else:
                tk.messagebox.showerror("Error", result.error)
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))
```

## Best Practices

### Security Best Practices

1. **Always validate user input** before passing to FaceAuth APIs
2. **Use secure storage directories** with appropriate permissions
3. **Enable audit logging** for compliance and security monitoring
4. **Regularly backup** encrypted user data
5. **Monitor performance metrics** for anomalies
6. **Keep software updated** for security patches

### Performance Optimization

1. **Use GPU acceleration** when available (`device='cuda'`)
2. **Adjust quality thresholds** based on your security requirements
3. **Monitor memory usage** for long-running applications
4. **Cache authentication results** for short periods if appropriate
5. **Use batch operations** for multiple file encryptions

### Privacy Compliance

1. **Always obtain user consent** before enrollment
2. **Implement data retention policies** according to regulations
3. **Provide data deletion capabilities** upon user request
4. **Regular compliance audits** using built-in tools
5. **Maintain audit trails** for all biometric processing

## Troubleshooting

### Common API Issues

**Import Errors**
```python
# Ensure FaceAuth is in Python path
import sys
sys.path.append('/path/to/faceauth')
```

**Camera Access Issues**
```python
# Check camera permissions and availability
import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not accessible")
```

**Performance Issues**
```python
# Check GPU availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

For more troubleshooting information, see the [Troubleshooting Guide](TROUBLESHOOTING.md).

---

*This API documentation is for FaceAuth v1.0. For the latest updates, visit the [GitHub repository](https://github.com/your-username/faceauth).*
