# FaceAuth API Documentation

## Table of Contents

- [Overview](#overview)
- [Core Classes](#core-classes)
- [Enrollment API](#enrollment-api)
- [Authentication API](#authentication-api)
- [File Encryption API](#file-encryption-api)
- [Security APIs](#security-apis)
- [Storage APIs](#storage-apis)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)

## Overview

FaceAuth provides a comprehensive Python API for face-based authentication and file encryption. All operations are performed locally with privacy-by-design principles.

### Core Principles
- **Local Processing**: All operations happen on your device
- **Privacy First**: No data leaves your device, ever
- **Security**: Military-grade encryption (AES-256-GCM)
- **Compliance**: GDPR, CCPA, SOC2, ISO27001 ready

## Core Classes

### FaceEnrollmentManager

Primary class for managing face enrollments.

```python
from faceauth.core.enrollment import FaceEnrollmentManager

manager = FaceEnrollmentManager(
    storage_dir=None,      # Custom storage directory
    master_key=None        # Custom encryption key
)
```

**Methods:**
- `enroll_user(user_id, timeout=30, interactive=True)` - Enroll a new user
- `verify_enrollment(user_id)` - Check if user is enrolled
- `delete_user(user_id)` - Remove user enrollment
- `get_enrolled_users()` - List all enrolled users
- `get_storage_stats()` - Get storage information

### FaceAuthenticator

Handle face authentication operations.

```python
from faceauth.core.authentication import FaceAuthenticator
from faceauth.utils.storage import FaceDataStorage

storage = FaceDataStorage()
authenticator = FaceAuthenticator(
    storage=storage,
    similarity_threshold=0.6,    # Authentication threshold
    device='auto'                # Device selection
)
```

**Methods:**
- `authenticate(user_id, timeout=10)` - Simple authentication
- `authenticate_realtime(user_id, timeout=10, max_attempts=5)` - Detailed authentication
- `get_performance_metrics()` - Get authentication metrics
- `reset_metrics()` - Reset performance counters

### FileEncryption

Handle file encryption with face authentication.

```python
from faceauth.crypto.file_encryption import FileEncryption
from faceauth.utils.storage import FaceDataStorage

storage = FaceDataStorage()
file_encryption = FileEncryption(storage)
```

**Methods:**
- `encrypt_file(file_path, user_id, output_path=None, ...)` - Encrypt file
- `decrypt_file(encrypted_path, user_id, output_path=None, ...)` - Decrypt file
- `verify_encrypted_file(file_path)` - Verify file integrity
- `get_encryption_info(kdf_method)` - Get encryption details

## Enrollment API

### Basic Enrollment

```python
from faceauth.core.enrollment import FaceEnrollmentManager

# Initialize manager
manager = FaceEnrollmentManager()

# Enroll a user
result = manager.enroll_user(
    user_id="john.doe",
    timeout=30,          # Enrollment timeout in seconds
    interactive=True     # Show progress in terminal
)

# Check result
if result['success']:
    print(f"✅ Enrollment successful!")
    print(f"📊 Quality: {result['average_quality']:.3f}")
    print(f"📸 Samples: {result['samples_collected']}")
    print(f"⏱️  Duration: {result['duration']:.1f}s")
else:
    print(f"❌ Enrollment failed: {result['error']}")
    print(f"🔍 Error code: {result.get('code')}")
```

### Advanced Enrollment

```python
# Custom storage and encryption
manager = FaceEnrollmentManager(
    storage_dir="/secure/path",
    master_key="your-secure-password"
)

# Enroll with custom parameters
result = manager.enroll_user(
    user_id="alice@company.com",
    timeout=60,
    interactive=False,   # Programmatic mode
    quality_threshold=0.8,  # Higher quality requirement
    min_samples=10       # More samples for better accuracy
)
```

### Enrollment Management

```python
# Check if user exists
if manager.verify_enrollment("john.doe"):
    print("User is enrolled")

# Get all enrolled users
users = manager.get_enrolled_users()
for user in users:
    print(f"User: {user}")

# Delete user enrollment
if manager.delete_user("old_user"):
    print("User deleted successfully")

# Get storage statistics
stats = manager.get_storage_stats()
print(f"Total users: {stats['total_users']}")
print(f"Storage size: {stats['storage_size_bytes']} bytes")
print(f"Storage dir: {stats['storage_dir']}")
```

## Authentication API

### Basic Authentication

```python
from faceauth.core.authentication import FaceAuthenticator
from faceauth.utils.storage import FaceDataStorage

# Initialize
storage = FaceDataStorage()
authenticator = FaceAuthenticator(storage, similarity_threshold=0.6)

# Simple authentication
success = authenticator.authenticate("john.doe", timeout=10)
if success:
    print("Authentication successful!")
else:
    print("Authentication failed!")
```

### Detailed Authentication

```python
# Detailed authentication with metrics
result = authenticator.authenticate_realtime(
    user_id="john.doe",
    timeout=15,
    max_attempts=5,
    show_camera=True,    # Show camera preview
    quality_check=True   # Enable quality checking
)

if result['success']:
    print(f"✅ Authentication successful!")
    print(f"🎯 Similarity: {result['similarity']:.3f}")
    print(f"⏱️  Duration: {result['duration']:.2f}s")
    print(f"🔄 Attempts: {result['attempts']}")
    print(f"📊 Quality: {result['quality']:.3f}")
else:
    print(f"❌ Authentication failed: {result['error']}")
    print(f"🔍 Error type: {result.get('error_type')}")
    print(f"📈 Best similarity: {result.get('best_similarity', 0):.3f}")
```

### Authentication Metrics

```python
# Get performance metrics
metrics = authenticator.get_performance_metrics()

print(f"📊 Total authentications: {metrics['total_attempts']}")
print(f"✅ Successful: {metrics['successful_attempts']}")
print(f"❌ Failed: {metrics['failed_attempts']}")
print(f"⏱️  Average time: {metrics['average_authentication_time']:.2f}s")
print(f"📈 Success rate: {metrics['success_rate']:.1%}")

# False positive/negative rates (if available)
if 'false_positive_rate' in metrics:
    print(f"📈 False positive rate: {metrics['false_positive_rate']:.1%}")
    print(f"📉 False negative rate: {metrics['false_negative_rate']:.1%}")

# Reset metrics
authenticator.reset_metrics()
```

## File Encryption API

### Basic File Encryption

```python
from faceauth.crypto.file_encryption import FileEncryption
from faceauth.utils.storage import FaceDataStorage

# Initialize
storage = FaceDataStorage()
file_encryption = FileEncryption(storage)

# Encrypt a file
result = file_encryption.encrypt_file(
    file_path="document.pdf",
    user_id="john.doe",
    output_path="document.pdf.faceauth",  # Optional
    auth_timeout=15
)

if result['success']:
    print(f"✅ File encrypted: {result['output_file']}")
    print(f"⏱️  Duration: {result['duration']:.2f}s")
    print(f"📦 Size: {result['original_size']} → {result['encrypted_size']} bytes")
    print(f"🔐 KDF: {result['kdf_method']}")
else:
    print(f"❌ Encryption failed: {result['error']}")
```

### Advanced File Encryption

```python
# Advanced encryption with custom parameters
result = file_encryption.encrypt_file(
    file_path="sensitive_data.json",
    user_id="alice@company.com",
    output_path="/secure/encrypted_data.faceauth",
    kdf_method="argon2",     # Key derivation: argon2, pbkdf2, scrypt, multi
    chunk_size=2*1024*1024,  # 2MB chunks for large files
    auth_timeout=30,         # Authentication timeout
    overwrite=True           # Overwrite existing files
)
```

### File Decryption

```python
# Decrypt a file
result = file_encryption.decrypt_file(
    encrypted_path="document.pdf.faceauth",
    user_id="john.doe",
    output_path="document_decrypted.pdf",  # Optional
    auth_timeout=15
)

if result['success']:
    print(f"✅ File decrypted: {result['output_file']}")
    print(f"⏱️  Duration: {result['duration']:.2f}s")
    print(f"🔍 Verified: {result['integrity_verified']}")
else:
    print(f"❌ Decryption failed: {result['error']}")
```

### File Verification

```python
# Verify encrypted file without decrypting
info = file_encryption.verify_encrypted_file("document.pdf.faceauth")

if info['is_faceauth_file']:
    print(f"✅ Valid FaceAuth file")
    print(f"📄 Original: {info['original_filename']}")
    print(f"📦 Size: {info['original_size']} bytes")
    print(f"🔐 KDF: {info['kdf_method']}")
    print(f"📅 Created: {info['creation_time']}")
    print(f"🔍 Integrity: {info['integrity_check']}")
else:
    print(f"❌ Not a valid FaceAuth file")
```

### Encryption Information

```python
# Get encryption algorithm details
crypto_info = file_encryption.get_encryption_info("argon2")

print(f"🔐 Algorithm: {crypto_info['encryption_algorithm']}")
print(f"🔑 Key size: {crypto_info['key_size_bits']} bits")
print(f"🧮 KDF: {crypto_info['kdf_algorithm']}")
print(f"⚙️  KDF params: {crypto_info['kdf_parameters']}")
print(f"📋 Description: {crypto_info['description']}")
```

## Security APIs

### Privacy Manager

```python
from faceauth.security.privacy_manager import PrivacyManager

privacy = PrivacyManager()

# Grant consent
privacy.grant_consent("john.doe", "facial_recognition")

# Check consent
if privacy.has_consent("john.doe", "facial_recognition"):
    print("User has given consent")

# Export user data (GDPR right to portability)
data = privacy.export_user_data("john.doe")
with open("user_data.json", "w") as f:
    f.write(data)

# Delete user data (GDPR right to erasure)
privacy.delete_user_data("john.doe")
```

### Audit Logger

```python
from faceauth.security.audit_logger import SecureAuditLogger

audit = SecureAuditLogger()

# Log authentication event
audit.log_authentication("john.doe", success=True, similarity=0.85)

# Log encryption event
audit.log_encryption("document.pdf", "john.doe", "encrypt")

# Log privacy event
audit.log_privacy_event("john.doe", "consent_granted", "facial_recognition")

# Get audit logs
logs = audit.get_audit_logs(user_id="john.doe", limit=10)
for log in logs:
    print(f"{log['timestamp']}: {log['event_type']} - {log['message']}")
```

### Compliance Checker

```python
from faceauth.security.compliance_checker import ComplianceChecker

compliance = ComplianceChecker()

# Check GDPR compliance
gdpr_result = compliance.check_gdpr_compliance()
print(f"GDPR Score: {gdpr_result['score']:.1f}/100")

# Check all standards
all_results = compliance.check_all_standards()
for standard, result in all_results.items():
    print(f"{standard}: {result['score']:.1f}/100 ({'PASS' if result['passed'] else 'FAIL'})")

# Export compliance report
report = compliance.export_compliance_report()
with open("compliance_report.json", "w") as f:
    f.write(report)
```

## Storage APIs

### Face Data Storage

```python
from faceauth.utils.storage import FaceDataStorage

storage = FaceDataStorage(
    storage_dir="/custom/path",
    master_key="encryption-key"
)

# Check if user exists
if storage.user_exists("john.doe"):
    print("User data exists")

# Get user metadata
metadata = storage.get_user_metadata("john.doe")
print(f"Enrolled: {metadata['enrollment_date']}")
print(f"Quality: {metadata['average_quality']}")

# Store face embedding (internal use)
# This is typically done by enrollment manager
storage.store_face_embedding("user_id", embedding_vector, metadata)

# Load face embedding (internal use)
embedding = storage.load_face_embedding("user_id")
```

### Secure Storage

```python
from faceauth.security.secure_storage import SecureStorage

secure = SecureStorage()

# Store encrypted data
secure.store_encrypted("user_key", {"sensitive": "data"})

# Load encrypted data
data = secure.load_encrypted("user_key")

# Delete encrypted data
secure.delete_encrypted("user_key")

# List stored keys
keys = secure.list_keys()
```

## Error Handling

### Common Exceptions

```python
from faceauth.core.enrollment import FaceEnrollmentError
from faceauth.core.authentication import AuthenticationError
from faceauth.crypto.file_encryption import EncryptionError

try:
    # Enrollment
    result = manager.enroll_user("john.doe")
except FaceEnrollmentError as e:
    print(f"Enrollment error: {e}")
    print(f"Error code: {e.error_code}")

try:
    # Authentication
    result = authenticator.authenticate("john.doe")
except AuthenticationError as e:
    print(f"Authentication error: {e}")
    print(f"Error type: {e.error_type}")

try:
    # File encryption
    result = file_encryption.encrypt_file("file.pdf", "john.doe")
except EncryptionError as e:
    print(f"Encryption error: {e}")
    print(f"Error details: {e.details}")
```

### Error Codes

**Enrollment Errors:**
- `CAMERA_ERROR` - Camera not accessible
- `NO_FACE_DETECTED` - No face found in camera
- `POOR_QUALITY` - Face quality too low
- `TIMEOUT` - Enrollment timed out
- `USER_EXISTS` - User already enrolled
- `STORAGE_ERROR` - Storage operation failed

**Authentication Errors:**
- `USER_NOT_FOUND` - User not enrolled
- `CAMERA_ERROR` - Camera not accessible
- `TIMEOUT` - Authentication timed out
- `MAX_ATTEMPTS_EXCEEDED` - Too many failed attempts
- `THRESHOLD_NOT_MET` - Similarity below threshold

**Encryption Errors:**
- `FILE_NOT_FOUND` - Input file doesn't exist
- `INVALID_FILE` - File is corrupted or invalid
- `AUTHENTICATION_FAILED` - Face authentication failed
- `PERMISSION_DENIED` - File access denied
- `STORAGE_FULL` - Insufficient storage space

## Code Examples

### Complete Enrollment and Authentication Workflow

```python
from faceauth import FaceEnrollmentManager
from faceauth.core.authentication import FaceAuthenticator
from faceauth.utils.storage import FaceDataStorage

def complete_workflow():
    """Complete enrollment and authentication example."""
    
    # Step 1: Initialize system
    manager = FaceEnrollmentManager()
    storage = FaceDataStorage()
    authenticator = FaceAuthenticator(storage)
    
    user_id = "demo_user"
    
    try:
        # Step 2: Enroll user
        print("👤 Enrolling user...")
        result = manager.enroll_user(user_id, timeout=30)
        
        if not result['success']:
            print(f"❌ Enrollment failed: {result['error']}")
            return
            
        print(f"✅ User enrolled! Quality: {result['average_quality']:.3f}")
        
        # Step 3: Authenticate user
        print("🔍 Authenticating user...")
        auth_result = authenticator.authenticate_realtime(user_id, timeout=10)
        
        if auth_result['success']:
            print(f"✅ Authentication successful!")
            print(f"🎯 Similarity: {auth_result['similarity']:.3f}")
        else:
            print(f"❌ Authentication failed: {auth_result['error']}")
            
        # Step 4: Clean up
        manager.delete_user(user_id)
        print("🧹 Demo user cleaned up")
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")

# Run the example
complete_workflow()
```

### File Encryption Workflow

```python
from faceauth import FaceEnrollmentManager
from faceauth.crypto.file_encryption import FileEncryption
from faceauth.utils.storage import FaceDataStorage

def file_encryption_workflow():
    """Complete file encryption example."""
    
    # Initialize
    manager = FaceEnrollmentManager()
    storage = FaceDataStorage()
    file_encryption = FileEncryption(storage)
    
    user_id = "file_user"
    test_file = "test_document.txt"
    
    # Create test file
    with open(test_file, "w") as f:
        f.write("This is sensitive information that should be encrypted.")
    
    try:
        # Step 1: Enroll user (if not already enrolled)
        if not manager.verify_enrollment(user_id):
            print("👤 Enrolling user for file encryption...")
            result = manager.enroll_user(user_id)
            if not result['success']:
                print(f"❌ Enrollment failed: {result['error']}")
                return
        
        # Step 2: Encrypt file
        print("🔐 Encrypting file...")
        encrypt_result = file_encryption.encrypt_file(
            file_path=test_file,
            user_id=user_id,
            kdf_method="argon2"
        )
        
        if not encrypt_result['success']:
            print(f"❌ Encryption failed: {encrypt_result['error']}")
            return
            
        encrypted_file = encrypt_result['output_file']
        print(f"✅ File encrypted: {encrypted_file}")
        
        # Step 3: Verify encrypted file
        print("🔍 Verifying encrypted file...")
        info = file_encryption.verify_encrypted_file(encrypted_file)
        if info['is_faceauth_file']:
            print(f"✅ Valid FaceAuth file: {info['original_filename']}")
        
        # Step 4: Decrypt file
        print("🔓 Decrypting file...")
        decrypt_result = file_encryption.decrypt_file(
            encrypted_path=encrypted_file,
            user_id=user_id,
            output_path="decrypted_" + test_file
        )
        
        if decrypt_result['success']:
            print(f"✅ File decrypted: {decrypt_result['output_file']}")
            
            # Verify content
            with open(decrypt_result['output_file'], "r") as f:
                content = f.read()
                print(f"📄 Content: {content[:50]}...")
        else:
            print(f"❌ Decryption failed: {decrypt_result['error']}")
            
    except Exception as e:
        print(f"❌ File encryption error: {e}")
    finally:
        # Clean up test files
        import os
        for file in [test_file, encrypted_file, "decrypted_" + test_file]:
            if os.path.exists(file):
                os.remove(file)

# Run the example
file_encryption_workflow()
```

### Security and Privacy Example

```python
from faceauth.security.privacy_manager import PrivacyManager
from faceauth.security.audit_logger import SecureAuditLogger
from faceauth.security.compliance_checker import ComplianceChecker

def security_privacy_example():
    """Security and privacy features example."""
    
    privacy = PrivacyManager()
    audit = SecureAuditLogger()
    compliance = ComplianceChecker()
    
    user_id = "privacy_user"
    
    try:
        # Step 1: Grant consent
        print("📋 Managing user consent...")
        privacy.grant_consent(user_id, "facial_recognition")
        privacy.grant_consent(user_id, "data_processing")
        
        if privacy.has_consent(user_id, "facial_recognition"):
            print("✅ User has granted facial recognition consent")
        
        # Step 2: Log privacy event
        audit.log_privacy_event(user_id, "consent_granted", "facial_recognition")
        
        # Step 3: Check compliance
        print("🔍 Checking privacy compliance...")
        privacy_result = compliance.check_privacy_compliance()
        print(f"Privacy score: {privacy_result['score']:.1f}/100")
        
        # Step 4: Export user data (GDPR right to portability)
        print("📤 Exporting user data...")
        user_data = privacy.export_user_data(user_id)
        print(f"Exported data: {len(user_data)} bytes")
        
        # Step 5: Set data retention
        privacy.set_data_retention(user_id, days=365)
        print("📅 Data retention set to 365 days")
        
        # Step 6: Get audit logs
        print("📊 Recent audit events:")
        logs = audit.get_audit_logs(user_id=user_id, limit=5)
        for log in logs:
            print(f"  {log['timestamp']}: {log['event_type']}")
            
    except Exception as e:
        print(f"❌ Security/privacy error: {e}")

# Run the example
security_privacy_example()
```

## Best Practices

### Security Best Practices

1. **Use Strong Master Keys**: If using custom encryption keys, ensure they are cryptographically strong
2. **Secure Storage Location**: Use encrypted directories for storage when possible
3. **Regular Backups**: Create encrypted backups of enrollment data
4. **Access Control**: Limit file system access to FaceAuth directories
5. **Memory Security**: Use secure memory management for sensitive operations

### Privacy Best Practices

1. **Explicit Consent**: Always obtain explicit user consent before enrollment
2. **Data Minimization**: Only collect necessary biometric data
3. **Retention Limits**: Set appropriate data retention periods
4. **Regular Audits**: Regularly audit privacy compliance
5. **User Rights**: Implement all user privacy rights (access, portability, erasure)

### Performance Best Practices

1. **Hardware Optimization**: Use GPU acceleration when available
2. **Quality Thresholds**: Set appropriate quality thresholds for accuracy vs. speed
3. **Timeout Settings**: Configure timeouts based on use case requirements
4. **Memory Management**: Clean up resources after operations
5. **Caching**: Cache models and resources for repeated operations

---

*FaceAuth API Documentation v1.0 | Privacy-First Face Authentication*
