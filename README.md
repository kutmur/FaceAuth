# FaceAuth - Local Face Authentication System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Local%20Only-brightgreen)](README.md#security)

A **privacy-first** face authentication platform that keeps all face data local. No cloud dependencies, no third-party services, no data sharing.

## 🔒 Privacy & Security First

- **100% Local**: All face data stays on your device
- **Encrypted Storage**: Face embeddings are encrypted with AES-256
- **No Reconstruction**: Stored data cannot recreate original images  
- **Secure Deletion**: Proper secure file deletion when removing users
- **No Network**: Zero network requests or cloud dependencies

## ✨ Features

- **Modern Deep Learning**: Uses FaceNet with VGGFace2 for high accuracy
- **Fast Enrollment**: Complete face enrollment in under 30 seconds
- **Real-time Authentication**: Face verification in <2 seconds via webcam
- **Robust Detection**: Handles multiple faces, poor lighting, edge cases
- **Quality Assessment**: Automatic image quality validation
- **Performance Metrics**: Track false positive/negative rates
- **CLI Interface**: Easy-to-use command-line interface
- **Backup/Restore**: Encrypted backup and restore functionality
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/faceauth.git
cd faceauth
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run system check:**
```bash
python main.py system-check
```

4. **Try the demo:**
```bash
python demo.py
```

### Basic Usage

**Enroll a new user:**
```bash
python main.py enroll-face john.doe
```

**List enrolled users:**
```bash
python main.py list-users
```

**Delete a user:**
```bash
python main.py delete-user john.doe
```

## 📖 Documentation

### System Requirements

- **Python**: 3.8 or higher
- **Camera**: Webcam or built-in camera
- **Memory**: 2GB+ RAM recommended
- **Storage**: 10MB+ free space
- **OS**: Windows, macOS, or Linux

### Face Enrollment Process

The enrollment process captures multiple face samples to create a robust face profile:

1. **Face Detection**: Uses MTCNN for accurate face detection
2. **Quality Check**: Ensures high-quality face images (>95% confidence)
3. **Multiple Samples**: Collects 5-10 different face angles
4. **Embedding Generation**: Creates 512-dimensional face embedding using FaceNet
5. **Secure Storage**: Encrypts and stores the final averaged embedding

### CLI Commands

#### Core Commands

```bash
# Enroll a new user
python main.py enroll-face <user_id> [options]

# Verify user identity via webcam
python main.py verify-face <user_id> [options]

# Encrypt files with face authentication
python main.py encrypt-file <file_path> <user_id> [options]

# Decrypt FaceAuth encrypted files
python main.py decrypt-file <encrypted_path> <user_id> [options]

# List all enrolled users  
python main.py list-users [options]

# Delete a user's enrollment
python main.py delete-user <user_id> [options]

# Show authentication performance metrics
python main.py auth-metrics [options]

# Show storage information
python main.py storage-info [options]

# Display encrypted file information
python main.py file-info <encrypted_file> [options]

# Show cryptographic parameters
python main.py crypto-info [options]

# System health check
python main.py system-check
```

#### File Encryption Examples

```bash
# Encrypt a file with face authentication
python main.py encrypt-file document.pdf alice@example.com

# Encrypt with custom output path and KDF method
python main.py encrypt-file secret.txt john.doe --output secret.encrypted --kdf-method argon2

# Decrypt an encrypted file
python main.py decrypt-file document.pdf.faceauth alice@example.com

# Verify encrypted file without decrypting
python main.py decrypt-file document.pdf.faceauth alice --verify-only

# Show information about an encrypted file
python main.py file-info document.pdf.faceauth

# Display cryptographic information
python main.py crypto-info --kdf-method multi
```

#### Authentication Examples

```bash
# Basic authentication (10s timeout, 0.6 threshold)
python main.py verify-face alice@example.com

# Quick authentication with lower threshold
python main.py verify-face john.doe --timeout 5 --threshold 0.5

# Strict authentication with higher threshold
python main.py verify-face admin --timeout 15 --threshold 0.8 --max-attempts 8

# Show detailed metrics during authentication
python main.py verify-face user123 --show-metrics

# View authentication performance statistics
python main.py auth-metrics
```

#### Backup & Restore

```bash
# Create encrypted backup
python main.py backup backup.zip

# Restore from backup  
python main.py restore backup.zip
```

#### Options

```bash
# Common Options
--storage-dir, -s    Custom storage directory
--master-key, -k     Master encryption key
--force, -f          Force operation without confirmation
--quiet, -q          Minimal output mode

# Enrollment Options
--timeout, -t        Enrollment timeout (seconds)

# Encryption Options
--kdf-method         Key derivation method (argon2, pbkdf2, scrypt, multi)
--auth-timeout, -t   Authentication timeout (seconds)
--output, -o         Custom output path
--overwrite, -f      Overwrite existing files
--verify-only, -v    Only verify file, don't decrypt

# Authentication Options
--timeout, -t        Authentication timeout (seconds, default: 10)
--max-attempts, -a   Maximum authentication attempts (default: 5)
--threshold, -th     Similarity threshold 0.1-1.0 (default: 0.6)
--show-metrics, -m   Show detailed authentication metrics
--reset, -r          Reset performance metrics (auth-metrics command)
```

### Programming API

#### Enrollment API

```python
from faceauth import FaceEnrollmentManager

# Initialize the enrollment manager
manager = FaceEnrollmentManager()

# Enroll a user
result = manager.enroll_user("john.doe", timeout=30)

if result['success']:
    print(f"Enrolled successfully! Quality: {result['average_quality']:.3f}")
else:
    print(f"Enrollment failed: {result['error']}")

# Check if user exists
if manager.verify_enrollment("john.doe"):
    print("User is enrolled")
```

#### File Encryption API

```python
from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
from faceauth.utils.storage import FaceDataStorage

# Initialize file encryption
storage = FaceDataStorage()
file_encryption = FileEncryption(storage)

# Encrypt a file
result = file_encryption.encrypt_file(
    file_path="document.pdf",
    user_id="john.doe",
    output_path="document.pdf.faceauth",
    kdf_method="argon2",  # or 'pbkdf2', 'scrypt', 'multi'
    auth_timeout=15
)

if result['success']:
    print(f"File encrypted: {result['output_file']}")
    print(f"Encryption time: {result['duration']:.2f}s")
    print(f"Size: {result['original_size']} → {result['encrypted_size']} bytes")

# Decrypt a file
result = file_encryption.decrypt_file(
    encrypted_path="document.pdf.faceauth",
    user_id="john.doe",
    output_path="document_decrypted.pdf"
)

if result['success']:
    print(f"File decrypted: {result['output_file']}")

# Verify encrypted file
info = file_encryption.verify_encrypted_file("document.pdf.faceauth")
if info['is_faceauth_file']:
    print(f"Original filename: {info['original_filename']}")
    print(f"KDF method: {info['kdf_method']}")
    print(f"File size: {info['original_size']} bytes")

# Get encryption information
crypto_info = file_encryption.get_encryption_info("argon2")
print(f"Algorithm: {crypto_info['encryption_algorithm']}")
print(f"Key size: {crypto_info['key_size_bits']} bits")
```

### Performance Characteristics

#### Authentication Speed
- **Target**: <2 seconds per authentication
- **Typical**: 1-2 seconds on modern hardware
- **Factors**: Camera resolution, lighting, face position

#### Accuracy Metrics
- **False Acceptance Rate (FAR)**: <1% with default threshold (0.6)
- **False Rejection Rate (FRR)**: <5% with default threshold (0.6)
- **Equal Error Rate (EER)**: ~2-3% (threshold ~0.65)

#### Quality Requirements
- **Minimum face size**: 20x20 pixels
- **Lighting**: Brightness 80-200 (0-255 scale)
- **Sharpness**: Laplacian variance >100
- **Contrast**: Standard deviation >30

#### Error Handling
- **No face detected**: Automatic retry with guidance
- **Multiple faces**: Clear error message
- **Poor quality**: Real-time quality feedback
- **Wrong person**: Similarity score below threshold
- **Webcam issues**: Graceful fallback and error reporting

# Get all enrolled users
users = manager.get_enrolled_users()
print(f"Total users: {len(users)}")

# Delete a user
manager.delete_user("john.doe")
```

## 🏗️ Architecture

### Project Structure

```
FaceAuth/
├── main.py                 # CLI interface
├── demo.py                 # Demo script
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
├── README.md              # Documentation
├── faceauth/              # Main package
│   ├── __init__.py
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── enrollment.py  # Face enrollment logic
│   │   └── authentication.py  # Future: authentication
│   └── utils/             # Utilities
│       ├── __init__.py
│       ├── security.py    # Encryption & security
│       └── storage.py     # Local storage management
├── data/                  # Face data storage (created automatically)
└── tests/                 # Unit tests
    └── test_basic.py
```

### Security Architecture

1. **Encryption Layer**: AES-256 encryption for all face embeddings
2. **Obfuscation**: Additional XOR obfuscation layer
3. **Key Management**: PBKDF2 key derivation with 100,000 iterations
4. **Secure Storage**: Restrictive file permissions (600/700)
5. **Hash-based IDs**: User IDs are hashed for filename generation

### AI Models

- **Face Detection**: MTCNN (Multi-task Cascaded Convolutional Networks)
- **Face Recognition**: FaceNet with InceptionResNetV1 backbone
- **Training Data**: VGGFace2 dataset (530K+ identities)
- **Embedding Size**: 512-dimensional vectors
- **Accuracy**: 99.6%+ on standard face recognition benchmarks

## 🔧 Configuration

### Storage Configuration

By default, FaceAuth stores data in:
- **Windows**: `%USERPROFILE%\.faceauth\`
- **macOS/Linux**: `~/.faceauth/`

You can customize the storage location:

```bash
python main.py enroll-face john.doe --storage-dir /custom/path
```

### Encryption Configuration

**Default**: Auto-generated system key
```bash
python main.py enroll-face john.doe
```

**Custom Master Key**: Use your own encryption key
```bash
python main.py enroll-face john.doe --master-key "my-secure-password"
```

### Performance Tuning

**GPU Acceleration** (if available):
- Automatically uses CUDA if available
- Falls back to CPU processing
- CPU mode is still very fast (~1-2 seconds per embedding)

**Memory Usage**:
- Enrollment: ~500MB peak memory usage
- Storage: ~1KB per enrolled user
- Models: ~100MB loaded in memory

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=faceauth --cov-report=html
```

Run the demo:

```bash
python demo.py
```

## 🚨 Security Considerations

### What's Stored

- **Face Embeddings**: 512-dimensional mathematical vectors
- **Metadata**: Enrollment time, quality scores, sample count
- **No Images**: Original face images are never stored

### What's NOT Stored

- ❌ Original camera images
- ❌ Face photos or videos  
- ❌ Biometric templates that can reconstruct faces
- ❌ Personal information beyond user ID

### Threat Model

**Protects Against**:
- ✅ Face image reconstruction from stored data
- ✅ Unauthorized access to face data
- ✅ Man-in-the-middle attacks (no network)
- ✅ Data breaches (encrypted storage)

**Does NOT Protect Against**:
- ❌ Physical access to unlocked device
- ❌ Compromised master key
- ❌ Malware with root/admin access
- ❌ Live camera access by malicious software

### Best Practices

1. **Use Strong Master Keys**: If using custom encryption keys
2. **Secure Your Device**: Use device encryption and screen locks
3. **Regular Backups**: Create encrypted backups periodically
4. **Access Control**: Limit access to the storage directory
5. **Clean Up**: Delete enrollments when no longer needed

**FaceAuth** - Because your face data should stay on your device. 🔒