# FaceAuth User Guide

Complete guide to using FaceAuth for secure, privacy-first face authentication and file encryption.

## Table of Contents
- [Getting Started](#getting-started)
- [Core Workflows](#core-workflows)
- [File Encryption & Decryption](#file-encryption--decryption)
- [Privacy & Security Management](#privacy--security-management)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Examples & Tutorials](#examples--tutorials)

## Getting Started

### First Time Setup

After installation, initialize FaceAuth:

```bash
# Initialize configuration
python main.py config-init

# Verify system is ready
python main.py system-check

# Optional: Install shell completion
python main.py install-completion
```

### Quick Start Tutorial

#### 1. Enroll Your First User

```bash
# Basic enrollment
python main.py enroll-face john.doe

# Follow the interactive prompts:
# ✅ Camera will open
# ✅ Position your face in the frame
# ✅ Look directly at the camera
# ✅ Wait for enrollment to complete
```

**What happens during enrollment:**
- Camera captures multiple face samples
- Face detection and quality assessment
- Creates encrypted face embeddings
- Stores data locally (never uploaded)
- Completes consent and privacy setup

#### 2. Test Authentication

```bash
# Verify your enrolled face
python main.py verify-face john.doe

# ✅ Look at camera when prompted
# ✅ Authentication completes in 1-3 seconds
```

#### 3. Encrypt Your First File

```bash
# Encrypt a document with face authentication
python main.py encrypt-file document.pdf john.doe

# ✅ Face authentication required
# ✅ File encrypted as document.pdf.encrypted
# ✅ Original file can be securely deleted
```

#### 4. Decrypt Your File

```bash
# Decrypt with face authentication
python main.py decrypt-file document.pdf.encrypted john.doe

# ✅ Face authentication required
# ✅ Original file restored
```

## Core Workflows

### User Management

#### Enrolling Users

**Basic Enrollment:**
```bash
# Simple enrollment with default settings
python main.py enroll-face alice@company.com
```

**Advanced Enrollment:**
```bash
# Enrollment with custom settings
python main.py enroll-face bob.smith \
  --timeout 45 \
  --samples 10 \
  --quality-threshold 0.8 \
  --storage-dir /secure/location
```

**Batch Enrollment:**
```bash
# Enroll multiple users from file
python main.py enroll-batch users.txt

# users.txt format:
# john.doe
# alice.smith
# bob.jones
```

#### Listing Users

```bash
# List all enrolled users
python main.py list-users

# Detailed user information
python main.py list-users --detailed

# Export user list
python main.py list-users --export users.json
```

#### User Information

```bash
# Get detailed user information
python main.py user-info alice@company.com

# Check enrollment status
python main.py verify-enrollment alice@company.com

# View user statistics
python main.py user-stats alice@company.com
```

#### Deleting Users

```bash
# Delete a user (with confirmation)
python main.py delete-user bob.smith

# Force delete without confirmation
python main.py delete-user bob.smith --force

# Delete all users (dangerous!)
python main.py delete-all-users --force
```

### Authentication Workflows

#### Basic Authentication

```bash
# Simple face verification
python main.py verify-face john.doe

# Authentication with custom threshold
python main.py verify-face john.doe --threshold 0.7

# Verbose authentication with metrics
python main.py verify-face john.doe --verbose --show-metrics
```

#### Advanced Authentication

```bash
# Authentication with multiple attempts
python main.py verify-face alice@company.com \
  --max-attempts 3 \
  --timeout 30 \
  --retry-delay 2

# Silent authentication (no UI)
python main.py verify-face bob.smith --quiet

# Debug mode authentication
python main.py verify-face john.doe --debug
```

#### Batch Authentication

```bash
# Test authentication for multiple users
python main.py verify-batch users.txt

# Authentication benchmark
python main.py auth-benchmark --users 5 --iterations 10
```

## File Encryption & Decryption

### Basic File Operations

#### Single File Encryption

```bash
# Encrypt a file
python main.py encrypt-file secret.txt john.doe

# Encrypt with custom output name
python main.py encrypt-file document.pdf john.doe \
  --output secure_document.encrypted

# Encrypt and delete original
python main.py encrypt-file sensitive.docx john.doe --delete-original
```

#### Single File Decryption

```bash
# Decrypt a file
python main.py decrypt-file secret.txt.encrypted john.doe

# Decrypt to specific location
python main.py decrypt-file document.encrypted john.doe \
  --output /recovery/document.pdf

# Decrypt and delete encrypted file
python main.py decrypt-file data.encrypted john.doe --delete-encrypted
```

### Advanced File Operations

#### Batch File Encryption

```bash
# Encrypt multiple files
python main.py encrypt-batch john.doe *.pdf *.docx *.txt

# Encrypt entire directory
python main.py encrypt-directory /documents john.doe

# Encrypt with pattern matching
python main.py encrypt-pattern "*.sensitive.*" john.doe
```

#### Batch File Decryption

```bash
# Decrypt multiple files
python main.py decrypt-batch john.doe *.encrypted

# Decrypt entire directory
python main.py decrypt-directory /encrypted_docs john.doe

# Decrypt with verification
python main.py decrypt-batch john.doe *.encrypted --verify-integrity
```

### Encryption Options

#### Encryption Methods

```bash
# AES-256-GCM (default, recommended)
python main.py encrypt-file data.txt john.doe --method aes256-gcm

# ChaCha20-Poly1305 (faster on some systems)
python main.py encrypt-file data.txt john.doe --method chacha20-poly1305

# AES-256-CBC (legacy compatibility)
python main.py encrypt-file data.txt john.doe --method aes256-cbc
```

#### Key Derivation Options

```bash
# Argon2 (default, most secure)
python main.py encrypt-file data.txt john.doe --kdf argon2

# PBKDF2 (faster, less secure)
python main.py encrypt-file data.txt john.doe --kdf pbkdf2

# Custom iterations
python main.py encrypt-file data.txt john.doe --kdf-iterations 1000000
```

### File Integrity and Verification

#### Verification Commands

```bash
# Verify encrypted file integrity
python main.py verify-file document.pdf.encrypted

# Batch verification
python main.py verify-batch *.encrypted

# Deep integrity check
python main.py integrity-check /encrypted_folder --deep
```

#### Repair and Recovery

```bash
# Attempt to repair corrupted files
python main.py repair-file corrupted.encrypted john.doe

# Emergency recovery
python main.py emergency-decrypt corrupted.encrypted \
  --user john.doe \
  --force \
  --partial-recovery
```

## Privacy & Security Management

### Privacy Controls

#### Data Rights Management

```bash
# Grant explicit consent
python main.py privacy-settings john.doe --grant-consent

# Revoke consent (stops processing)
python main.py privacy-settings john.doe --revoke-consent

# Set data retention period
python main.py privacy-settings john.doe --set-retention 365
```

#### Data Export (GDPR Right to Portability)

```bash
# Export all user data
python main.py privacy-settings john.doe --export-data user_data.json

# Export with metadata
python main.py privacy-settings john.doe \
  --export-data user_data.json \
  --include-metadata \
  --include-audit-logs
```

#### Data Deletion (GDPR Right to Erasure)

```bash
# Secure data deletion
python main.py privacy-settings john.doe --delete-data

# Immediate deletion without confirmation
python main.py privacy-settings john.doe --delete-data --force

# Deletion with audit trail
python main.py privacy-settings john.doe --delete-data --audit-trail
```

### Security Auditing

#### System Security Audit

```bash
# Comprehensive security audit
python main.py security-audit

# Audit with automatic fixes
python main.py security-audit --fix

# Export security report
python main.py security-audit --export security_report.json
```

#### Compliance Checking

```bash
# Check GDPR compliance
python main.py compliance-check --standard gdpr

# Check multiple standards
python main.py compliance-check --standard gdpr --standard ccpa --standard iso27001

# Generate compliance report
python main.py compliance-check --export compliance_report.pdf
```

#### Privacy Impact Assessment

```bash
# Run privacy assessment
python main.py privacy-check

# Assessment for specific user
python main.py privacy-check --user-id john.doe

# Generate privacy report
python main.py privacy-check --export privacy_assessment.json
```

### Audit Logs and Monitoring

#### Viewing Audit Logs

```bash
# View recent audit logs
python main.py audit-logs --recent 24h

# View logs for specific user
python main.py audit-logs --user john.doe

# Export audit logs
python main.py audit-logs --export audit_export.json --date-range 2024-01-01:2024-12-31
```

#### Security Monitoring

```bash
# Real-time security monitoring
python main.py security-monitor --live

# Generate security alerts
python main.py security-alerts --threshold high

# Security dashboard
python main.py security-dashboard
```

## Advanced Usage

### Configuration Management

#### System Configuration

```bash
# View current configuration
python main.py config-show

# Set configuration values
python main.py config-set storage_dir /secure/path
python main.py config-set log_level DEBUG
python main.py config-set camera_device 1

# Reset to defaults
python main.py config-reset

# Export configuration
python main.py config-export config_backup.json
```

#### User-Specific Configuration

```bash
# Set user-specific settings
python main.py user-config john.doe --set quality_threshold 0.8
python main.py user-config john.doe --set max_attempts 5
python main.py user-config john.doe --set timeout 30
```

### Backup and Restore

#### Creating Backups

```bash
# Full system backup
python main.py backup full_backup.zip

# Encrypted backup with password
python main.py backup secure_backup.zip --encrypt --password

# User-specific backup
python main.py backup user_backup.zip --user john.doe

# Incremental backup
python main.py backup incremental_backup.zip --incremental --since 2024-01-01
```

#### Restoring from Backup

```bash
# Full restore
python main.py restore full_backup.zip

# Restore specific user
python main.py restore user_backup.zip --user john.doe

# Dry-run restore (test only)
python main.py restore backup.zip --dry-run

# Restore with verification
python main.py restore backup.zip --verify
```

### Integration and Automation

#### API Integration

```bash
# Start API server
python main.py api-server --port 8080 --host localhost

# API with authentication
python main.py api-server --port 8080 --api-key your-secret-key

# HTTPS API server
python main.py api-server --port 8443 --ssl-cert cert.pem --ssl-key key.pem
```

#### Automated Scripts

```bash
# Run automated enrollment
python main.py auto-enroll --config auto_enroll.json

# Scheduled authentication checks
python main.py scheduled-auth --interval 1h --users "john.doe,alice@company.com"

# Automated file monitoring
python main.py file-monitor /secure/folder --encrypt-new --user john.doe
```

### Performance Optimization

#### Performance Tuning

```bash
# Set performance profile
python main.py config-set performance_profile fast  # or balanced, secure

# Enable GPU acceleration
python main.py config-set use_gpu true

# Optimize memory usage
python main.py config-set memory_efficient true

# Set thread count
python main.py config-set worker_threads 4
```

#### Performance Monitoring

```bash
# System performance stats
python main.py performance-stats

# Benchmark authentication speed
python main.py benchmark-auth --iterations 100

# Memory usage monitoring
python main.py memory-monitor --duration 300
```

## Best Practices

### Security Best Practices

1. **Regular Security Audits**
   ```bash
   # Schedule weekly security audits
   python main.py security-audit --schedule weekly
   ```

2. **Secure Storage Configuration**
   ```bash
   # Use encrypted storage location
   python main.py config-set storage_dir /encrypted/volume/faceauth
   
   # Set restrictive permissions
   chmod 700 ~/.faceauth
   ```

3. **Strong Encryption Settings**
   ```bash
   # Use strongest encryption
   python main.py config-set encryption_method aes256-gcm
   python main.py config-set kdf_method argon2
   python main.py config-set kdf_iterations 1000000
   ```

### Privacy Best Practices

1. **Explicit Consent Management**
   ```bash
   # Always obtain explicit consent
   python main.py privacy-settings --require-consent true
   ```

2. **Data Minimization**
   ```bash
   # Set short retention periods
   python main.py config-set default_retention_days 90
   ```

3. **Regular Privacy Assessments**
   ```bash
   # Monthly privacy checks
   python main.py privacy-check --schedule monthly
   ```

### Operational Best Practices

1. **Regular Backups**
   ```bash
   # Daily encrypted backups
   python main.py backup daily_backup_$(date +%Y%m%d).zip --encrypt
   ```

2. **Camera Quality Settings**
   ```bash
   # Optimal camera settings
   python main.py config-set camera_resolution 640x480
   python main.py config-set camera_fps 30
   ```

3. **User Training**
   - Ensure proper lighting during enrollment
   - Look directly at camera during authentication
   - Keep face visible and unobstructed
   - Report authentication issues promptly

## Examples & Tutorials

### Tutorial 1: Setting Up Secure Document Storage

**Scenario**: Create a secure document vault using face authentication.

```bash
# 1. Create dedicated user
python main.py enroll-face document-vault

# 2. Create secure directory
mkdir ~/secure_documents

# 3. Encrypt all documents
python main.py encrypt-directory ~/documents document-vault

# 4. Move encrypted files to secure location
mv ~/documents/*.encrypted ~/secure_documents/

# 5. Set up automatic monitoring
python main.py file-monitor ~/secure_documents --user document-vault
```

### Tutorial 2: Multi-User Family Setup

**Scenario**: Set up FaceAuth for a family with different access levels.

```bash
# 1. Enroll family members
python main.py enroll-face dad
python main.py enroll-face mom
python main.py enroll-face teen_child

# 2. Create shared family files
python main.py encrypt-file family_budget.xlsx dad
python main.py encrypt-file family_photos.zip mom

# 3. Set up individual secure folders
python main.py encrypt-directory ~/Dad/private dad
python main.py encrypt-directory ~/Mom/private mom
python main.py encrypt-directory ~/Teen/private teen_child

# 4. Configure privacy settings
python main.py privacy-settings dad --set-retention 1095  # 3 years
python main.py privacy-settings mom --set-retention 1095
python main.py privacy-settings teen_child --set-retention 365  # 1 year
```

### Tutorial 3: Business Document Security

**Scenario**: Secure business documents with employee face authentication.

```bash
# 1. Enroll employees
python main.py enroll-batch employees.txt

# 2. Set up department-specific encryption
python main.py encrypt-pattern "hr_*.pdf" hr_manager
python main.py encrypt-pattern "finance_*.xlsx" finance_manager
python main.py encrypt-pattern "legal_*.docx" legal_counsel

# 3. Set up compliance monitoring
python main.py compliance-check --standard gdpr --schedule weekly

# 4. Configure audit logging
python main.py config-set audit_logging true
python main.py config-set audit_retention_days 2555  # 7 years

# 5. Set up backup schedule
python main.py backup company_backup.zip --encrypt --schedule daily
```

### Tutorial 4: Developer Integration

**Scenario**: Integrate FaceAuth into a Python application.

```python
#!/usr/bin/env python3
"""
Example: FaceAuth integration in a Python application
"""

from faceauth import FaceEnrollmentManager
from faceauth.core.authentication import FaceAuthenticator
from faceauth.utils.storage import FaceDataStorage
import os

class SecureApp:
    def __init__(self):
        self.storage = FaceDataStorage()
        self.enrollment_manager = FaceEnrollmentManager()
        self.authenticator = FaceAuthenticator(self.storage)
    
    def setup_user(self, user_id):
        """Set up a new user with face enrollment."""
        print(f"Setting up user: {user_id}")
        
        # Check if user already exists
        if self.enrollment_manager.is_user_enrolled(user_id):
            print(f"User {user_id} already enrolled")
            return True
        
        # Enroll user
        result = self.enrollment_manager.enroll_user(user_id, timeout=30)
        
        if result['success']:
            print(f"✅ User {user_id} enrolled successfully")
            print(f"📊 Quality: {result['average_quality']:.3f}")
            return True
        else:
            print(f"❌ Enrollment failed: {result['error']}")
            return False
    
    def authenticate_user(self, user_id):
        """Authenticate user with face recognition."""
        print(f"Authenticating user: {user_id}")
        
        result = self.authenticator.authenticate_realtime(
            user_id=user_id,
            timeout=10,
            max_attempts=3
        )
        
        if result['success']:
            print(f"✅ Authentication successful")
            print(f"🎯 Similarity: {result['similarity']:.3f}")
            print(f"⏱️  Duration: {result['duration']:.2f}s")
            return True
        else:
            print(f"❌ Authentication failed: {result['error']}")
            return False
    
    def secure_file_operation(self, user_id, file_path, operation='read'):
        """Perform secure file operation with authentication."""
        
        # Authenticate user first
        if not self.authenticate_user(user_id):
            raise PermissionError("Authentication required")
        
        # Perform file operation
        if operation == 'read':
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return f.read()
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        
        elif operation == 'write':
            # Implementation for secure file writing
            pass
    
    def cleanup_user(self, user_id):
        """Securely remove user data."""
        
        # Get user consent for deletion
        consent = input(f"Delete all data for user {user_id}? (yes/no): ")
        
        if consent.lower() == 'yes':
            success = self.enrollment_manager.delete_user(user_id)
            if success:
                print(f"✅ User {user_id} data deleted")
            else:
                print(f"❌ Failed to delete user {user_id}")

# Example usage
if __name__ == "__main__":
    app = SecureApp()
    
    # Set up a user
    app.setup_user("employee_001")
    
    # Authenticate and perform secure operation
    try:
        content = app.secure_file_operation("employee_001", "secure_document.txt")
        print("File accessed successfully")
    except PermissionError:
        print("Access denied - authentication failed")
    except FileNotFoundError:
        print("File not found")
```

### Troubleshooting Common Issues

#### Issue: Camera Not Working

```bash
# Diagnose camera issues
python main.py diagnose-camera

# List available cameras
python main.py list-cameras

# Test specific camera
python main.py test-camera --device 1

# Reset camera settings
python main.py config-reset camera
```

#### Issue: Poor Authentication Accuracy

```bash
# Check image quality
python main.py quality-check john.doe

# Re-enroll with better samples
python main.py enroll-face john.doe --overwrite --samples 15

# Adjust similarity threshold
python main.py config-set similarity_threshold 0.5  # Lower = more lenient
```

#### Issue: Slow Performance

```bash
# Check system performance
python main.py performance-check

# Enable optimizations
python main.py config-set performance_profile fast
python main.py config-set use_gpu true

# Reduce image resolution
python main.py config-set camera_resolution 320x240
```

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Getting Help

- **Documentation**: [docs/](docs/)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **GitHub Issues**: [Issues](https://github.com/your-username/faceauth/issues)
- **Discussions**: [Discussions](https://github.com/your-username/faceauth/discussions)

## What's Next?

1. **Explore Advanced Features**: Try batch operations, API integration, and automation
2. **Set Up Monitoring**: Configure audit logs and security monitoring
3. **Implement Best Practices**: Follow security and privacy recommendations
4. **Join the Community**: Contribute to the project or help other users

Continue with the [Contributing Guide](CONTRIBUTING.md) if you want to help improve FaceAuth!
